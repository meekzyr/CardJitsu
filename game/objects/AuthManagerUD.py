from direct.distributed.DistributedObjectUD import DistributedObjectUD
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.fsm.FSM import *
from .DatabaseClass import AccountDB


class AuthFSM(FSM):
    DATABASE_CONTROL_CHANNEL = 4003

    def __init__(self, mgr, target):
        FSM.__init__(self, 'AuthFSM')
        self.mgr = mgr
        self.air = mgr.air
        self.target = target
        self.accountId = 0
        self.token = ''
        self.playerId = 0

    def enterBegin(self, username, password):
        self.token = username
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
            self.demand('GrabAccount')
        else:
            self.demand('CreateAccount')

    def enterGrabAccount(self):
        self.air.dbInterface.queryObject(self.DATABASE_CONTROL_CHANNEL, self.accountId, self.__handleGrabbed)

    def __handleGrabbed(self, dclass, fields):
        if dclass != self.air.dclassesByName['AccountUD']:
            self.notify.warning('wrong dclass')
            # todo : kill connection
            return

        print('found account', dclass, fields)
        self.account = fields
        self.demand('SetAccount')

    def enterCreateAccount(self):
        # prepare the player
        self.air.dbInterface.createObject(self.DATABASE_CONTROL_CHANNEL, self.air.dclassesByName['AccountUD'],
                                          {'ACCOUNT_ID': str(self.username), 'PLAYER_ID': 0}, self.__handleCreate)

    def __handleCreate(self, accountId):
        if not accountId:
            self.notify.warning('no account id')
            return

        self.accountId = accountId
        self.demand('CreatePlayer')

    def enterCreatePlayer(self):
        self.air.dbInterface.createObject(self.DATABASE_CONTROL_CHANNEL, self.air.dclassesByName['DistributedPlayerUD'],
                                          {'setWinLevel': (0,)}, self.__handlePlayerCreated)

    def __handlePlayerCreated(self, avId):
        self.playerId = avId
        self.air.dbInterface.updateObject(self.DATABASE_CONTROL_CHANNEL, self.accountId,
                                          self.air.dclassesByName['AccountUD'], {'PLAYER_ID': avId},
                                          callback=self.__updateDone)

    def __updateDone(self, *args):
        self.demand('StoreAccount')

    def enterStoreAccount(self):
        self.mgr.accountDb.storeAccountID(self.username, self.accountId, self.__handleStored)

    def __handleStored(self, success=True):
        self.demand('SetAccount')

    def enterSetAccount(self):
        # activate the player on the dbss
        self.air.sendActivate(self.playerId, 0, 0, self.air.dclassesByName['DistributedPlayerUD'])

        datagram = PyDatagram()
        datagram.addServerHeader(self.target, self.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.mgr.GetAccountConnectionChannel(self.accountId))
        self.air.send(datagram)

        self.air.setOwner(self.playerId, self.target)
        self.air.clientAddSessionObject(self.target, self.playerId)

        datagram = PyDatagram()
        datagram.addServerHeader(self.target, self.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.mgr.GetPuppetConnectionChannel(self.target))
        self.air.send(datagram)

        dg = PyDatagram()
        dg.addServerHeader(self.target, self.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.mgr.GetPuppetConnectionChannel(self.target))
        self.air.send(dg)

        self.mgr.sendUpdateToChannel(self.target, 'accessResponse', [True])
        self.demand('Off')


class AuthManagerUD(DistributedObjectUD):
    notify = directNotify.newCategory("AuthManagerUD")

    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)
        self.air = air
        self.clientId = None
        self.accountDb = AccountDB()

        self.conn2fsm = {}

    def requestLogin(self, username, password):
        self.notify.warning([username, password])
        sender = self.air.getMsgSender()

        self.air.setClientState(sender, 2)

        self.conn2fsm[sender] = AuthFSM(self, sender)
        self.conn2fsm[sender].request('Begin', username, password)

    def requestAccess(self):
        return
        clientId = self.air.getMsgSender()

        # unsandbox
        self.air.setClientState(clientId, 2)

        dg = PyDatagram()
        dg.addServerHeader(clientId, self.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.GetPuppetConnectionChannel(clientId))
        self.air.send(dg)

        '''
        accChannel = self.GetAccountConnectionChannel(clientId)
        # Now set their sender channel to represent their account affiliation:
        dg = PyDatagram()
        dg.addServerHeader(accChannel, self.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        # High 32 bits: accountId
        # Low 32 bits: avatarId
        dg.addChannel(clientId << 32 | clientId)
        self.air.send(dg)
        '''

        self.sendUpdateToChannel(clientId, 'accessResponse', [True])
