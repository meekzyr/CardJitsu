from direct.distributed.DistributedObjectUD import DistributedObjectUD
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.fsm.FSM import *
from .DatabaseClass import AccountDB
from .AuthGlobals import *

import bcrypt
import binascii
import hashlib


def hash_pw(salt, pw):
    hmac = hashlib.pbkdf2_hmac('sha512', bytes(pw, 'utf-8'), bytes(salt, 'utf-8'), 100000)
    hash = binascii.hexlify(hmac)
    return (bytes(salt, 'utf-8') + hash).decode('ascii')


def verify_pw(pw, salted_pw):
    salt = salted_pw[:29]
    stored_pw = salted_pw[29:]
    hmac = hashlib.pbkdf2_hmac('sha512', bytes(pw, 'utf-8'), bytes(salt, 'utf-8'), 100000)
    hash = binascii.hexlify(hmac).decode('ascii')
    return hash == stored_pw


class AuthFSM(FSM):
    DATABASE_CONTROL_CHANNEL = 4003

    def __init__(self, mgr, target, creating):
        FSM.__init__(self, 'AuthFSM')
        self.mgr = mgr
        self.air = mgr.air
        self.target = target
        self.accountId = 0
        self.token = ''
        self.password = ''
        self.playerId = 0
        self.creating = creating

    def killConnection(self, connId, reason):
        datagram = PyDatagram()
        datagram.addServerHeader(
            connId,
            self.air.ourChannel,
            CLIENTAGENT_EJECT)
        datagram.addUint16(122)
        datagram.addString(reason)
        self.air.send(datagram)

    def enterBegin(self, username, password):
        self.token = username
        self.password = password
        self.demand('Query')

    def enterQuery(self):
        self.mgr.accountDb.lookup(self.token, self.__handleLookup)

    def __handleLookup(self, result):
        success = result.get('success')
        if not success:
            return

        self.username = result.get('username', 0)
        self.accountId = result.get('accountId', 0)
        if self.accountId:
            if self.creating:
                self.mgr.sendUpdateToChannel(self.target, 'accessResponse', [INVALID_USERNAME])
                return

            self.demand('GrabAccount')
        else:
            if self.creating:
                self.demand('CreateAccount')
            else:
                self.mgr.sendUpdateToChannel(self.target, 'accessResponse', [INVALID_NOACCOUNT])

    def enterGrabAccount(self):
        self.air.dbInterface.queryObject(self.DATABASE_CONTROL_CHANNEL, self.accountId, self.__handleGrabbed)

    def __handleGrabbed(self, dclass, fields):
        if dclass != self.air.dclassesByName['AccountUD']:
            self.killConnection(self.target, 'Invalid dclass retrieved.')
            return

        acc_pass = fields.get('ACCOUNT_PASSWORD', '')
        if acc_pass and not verify_pw(self.password, acc_pass):
            self.mgr.sendUpdateToChannel(self.target, 'accessResponse', [INVALID_PASSWORD])
            return

        self.account = fields
        self.playerId = fields.get('PLAYER_ID', 0)
        self.demand('SetAccount')

    def enterCreateAccount(self):
        # prepare the player
        salt = bcrypt.gensalt().decode('utf-8')
        fields = {'ACCOUNT_ID': str(self.username),
                  'ACCOUNT_PASSWORD': hash_pw(salt, self.password),
                  'PLAYER_ID': 0}

        self.air.dbInterface.createObject(self.DATABASE_CONTROL_CHANNEL, self.air.dclassesByName['AccountUD'], fields,
                                          callback=self.__handleCreate)

    def __handleCreate(self, accountId):
        if not accountId:
            return

        self.accountId = accountId
        self.demand('CreatePlayer')

    def enterCreatePlayer(self):
        self.air.dbInterface.createObject(self.DATABASE_CONTROL_CHANNEL, self.air.dclassesByName['DistributedPlayerUD'],
                                          {'setBeltLevel': (0,)}, self.__handlePlayerCreated)

    def __handlePlayerCreated(self, avId):
        self.playerId = avId
        self.air.dbInterface.updateObject(self.DATABASE_CONTROL_CHANNEL, self.accountId,
                                          self.air.dclassesByName['AccountUD'], {'PLAYER_ID': avId},
                                          callback=self.__updateDone)

    def __updateDone(self, *args):
        self.demand('StoreAccount')

    def enterStoreAccount(self):
        self.mgr.accountDb.storeAccountID(self.username, self.accountId, self.__handleStored)

    def __handleStored(self, success):
        if success:
            self.demand('SetAccount')
        else:
            reason = 'Unable to associate user %s with account %d!' % (self.username, self.accountId)
            self.notify.warning(reason)
            self.killConnection(self.target, reason)

    def enterSetAccount(self):
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.mgr.GetAccountConnectionChannel(self.accountId),
            self.mgr.air.ourChannel,
            CLIENTAGENT_EJECT)
        datagram.addUint16(100)
        datagram.appendData(b'This account has been logged in from elsewhere.')
        self.mgr.air.send(datagram)

        # Next, add this connection to the account channel.
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.mgr.air.ourChannel,
            CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.mgr.GetAccountConnectionChannel(self.accountId))
        self.mgr.air.send(datagram)

        # when this dg is added, the accId is correct, but avId=0
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.accountId << 32)
        self.air.send(datagram)

        # Un-sandbox them!
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.mgr.air.ourChannel,
            CLIENTAGENT_SET_STATE)
        datagram.addUint16(2)  # ESTABLISHED
        self.mgr.air.send(datagram)

        self.mgr.sendUpdateToChannel(self.target, 'accessResponse', [LOGIN_SUCCESS])
        self.demand('SetAvatar')

    def enterSetAvatar(self):
        channel = self.mgr.GetAccountConnectionChannel(self.target)

        datagramCleanup = PyDatagram()
        datagramCleanup.addServerHeader(
            self.playerId,
            channel,
            STATESERVER_OBJECT_DELETE_RAM)
        datagramCleanup.addUint32(self.playerId)
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.air.ourChannel,
            CLIENTAGENT_ADD_POST_REMOVE)
        datagram.appendData(datagramCleanup.getMessage())
        self.air.send(datagram)

        # Activate the avatar on the DBSS:
        self.air.sendActivate(self.playerId, 0, 0, self.air.dclassesByName['DistributedPlayerUD'],
                              fields={'setName': [self.token]})

        # Next, add them to the avatar channel:
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.air.ourChannel,
            CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.mgr.GetPuppetConnectionChannel(self.target))
        self.air.send(datagram)

        # Finally, grant ownership and shut down.
        self.air.setOwner(self.playerId, self.target)

        self.air.clientAddSessionObject(self.target, self.playerId)

        # Now set their sender channel to represent their account affiliation:
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.mgr.GetPuppetConnectionChannel(self.playerId))
        self.air.send(datagram)


class AuthManagerUD(DistributedObjectUD):
    notify = directNotify.newCategory("AuthManagerUD")

    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)
        self.air = air
        self.clientId = None
        self.accountDb = AccountDB()

        self.conn2fsm = {}

    def requestLogin(self, username, password, creating):
        sender = self.air.getMsgSender()

        self.notify.warning([username, password, sender, creating])

        self.conn2fsm[sender] = AuthFSM(self, sender, creating)
        self.conn2fsm[sender].request('Begin', username, password)

    def requestAccess(self):
        return
        #self.sendUpdateToChannel(clientId, 'accessResponse', [True])
