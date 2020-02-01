from panda3d.core import *
from direct.distributed.ClientRepositoryBase import ClientRepositoryBase
from direct.distributed.MsgTypes import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import DistributedSmoothNode
from direct.gui.DirectGui import *
from game.player import LocalPlayer
import sys
from game.gui.LoginScreen import LoginScreen
from .AuthGlobals import *


class JitsuClientRepository(ClientRepositoryBase):
    taskChain = 'net'

    def __init__(self):
        ClientRepositoryBase.__init__(self, dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                      connectMethod=self.CM_NET, threadedNet=True)

        self.GameGlobalsId = 1000
        self.zoneInterest = None
        self.visInterest = None
        self.districtObj = None
        self.url = None
        self.failureText = None

        self.authManager = self.generateGlobalObject(1001, 'AuthManager')
        self.loginInterface = None
        self.gameVersion = base.config.GetString('base-version', 'dev')

        # No game, no avatar (yet).
        base.localAvatar = None

    def lostConnection(self):
        self.notify.warning("Lost connection to gameserver.")
        self.failureText = OnscreenText('Lost connection to gameserver.', scale=0.15, fg=(1, 0, 0, 1),
                                        shadow=(0, 0, 0, 1), pos=(0, 0.2))
        self.failureText.setBin('gui-popup', 0)
        base.transitions.fadeScreen(alpha=1)
        render.hide()

    def exit(self):
        if self.isConnected():
            self.sendDisconnect()
            self.disconnect()

        sys.exit()

    def startConnect(self):
        self.url = None
        if not self.url:
            tcpPort = base.config.GetInt('base-port', 7198)
            hostname = base.config.GetString('base-host', '127.0.0.1')
            if not hostname:
                hostname = '127.0.0.1'
            self.url = URLSpec('g://%s' % hostname, 1)
            self.url.setPort(tcpPort)

        self.connect([self.url], successCallback=self.connectSuccess, failureCallback=self.connectFailure)

    def connectFailure(self, statusCode, statusString):
        self.failureText = OnscreenText('Failed to connect to %s:\n%s.' % (self.url, statusString),
                                        scale=0.15, fg=(1, 0, 0, 1), shadow=(0, 0, 0, 1), pos=(0, 0.2))

    def connectSuccess(self):
        """ Successfully connected.  But we still need to send a CLIENT_HELLO message. """
        dg = PyDatagram()
        dg.addUint16(CLIENT_HELLO)
        dg.addUint32(self.hashVal)
        dg.addString(self.gameVersion)
        self.send(dg)

        if not self.loginInterface:
            self.loginInterface = LoginScreen()
            self.loginInterface.load()

    def handleDatagram(self, di):
        msgType = self.getMsgType()
        if msgType == CLIENT_HELLO_RESP:
            self.handleHelloResp()
        elif msgType == CLIENT_OBJECT_SET_FIELD:
            self.handleUpdateField(di)
        elif msgType == CLIENT_ENTER_OBJECT_REQUIRED:
            self.handleGenerate(di)
        elif msgType == CLIENT_OBJECT_LOCATION:
            self.handleObjectLocation(di)
        #elif msgType == CLIENT_ENTER_OBJECT_REQUIRED_OTHER:
        #    self.handleGenerate(di, True)
        elif msgType == CLIENT_DONE_INTEREST_RESP:
            self.handleInterestDoneMessage(di)
        elif msgType == CLIENT_ENTER_OBJECT_REQUIRED_OWNER:
            self.handleGenerateOwner(di)
        #elif msgType == CLIENT_ENTER_OBJECT_REQUIRED_OTHER_OWNER:
        #    self.handleGenerateOwner(di, True)
        elif msgType == CLIENT_OBJECT_LEAVING:
            self.handleDelete(di)

    def handleHelloResp(self):
        pass

    def sendHeartbeat(self):
        dg = PyDatagram()
        dg.addUint16(CLIENT_HEARTBEAT)
        self.send(dg)

    def sendDisconnect(self):
        dg = PyDatagram()
        dg.addUint16(CLIENT_DISCONNECT)
        self.send(dg)

    def handleGenerate(self, di, other=False):
        doId = di.getUint32()
        parentId = di.getUint32()
        zoneId = di.getUint32()
        classId = di.getUint16()

        dclass = self.dclassesByNumber[classId]
        dclass.startGenerate()
        if other:
            self.generateWithRequiredOtherFields(dclass, doId, di, parentId, zoneId)
        else:
            self.generateWithRequiredFields(dclass, doId, di, parentId, zoneId)
        dclass.stopGenerate()
        self.notify.debug(dclass.getName())

    def handleGenerateOwner(self, di, other=False):
        doId = di.getUint32()
        parentId = di.getUint32()
        zoneId = di.getUint32()
        dclassId = di.getUint16()
        self.handleAvatarResponseMsg(doId, di, parentId, zoneId)

    def handleAvatarResponseMsg(self, avatarId, di, parentId, zoneId):
        dclass = self.dclassesByName['DistributedPlayer']
        localAvatar = LocalPlayer.LocalPlayer(self)
        localAvatar.dclass = dclass
        base.localAvatar = localAvatar
        localAvatar.doId = avatarId
        self.localAvatarDoId = avatarId
        localAvatar.setLocation(parentId, zoneId)
        localAvatar.generateInit()
        localAvatar.generate()
        dclass.receiveUpdateBroadcastRequiredOwner(localAvatar, di)
        localAvatar.announceGenerate()
        localAvatar.postGenerateMessage()
        self.doId2do[avatarId] = localAvatar

    def handleDelete(self, di):
        doId = di.getUint32()
        if doId in self.doId2do:
            obj = self.doId2do[doId]
            del self.doId2do[doId]
            obj.deleteOrDelay()

    def sendSetLocation(self, doId, parentId, zoneId):
        datagram = PyDatagram()
        datagram.addUint16(CLIENT_OBJECT_LOCATION)
        datagram.addUint32(doId)
        datagram.addUint32(parentId)
        datagram.addUint32(zoneId)
        self.send(datagram)

    def gotTimeSync(self):
        pass

    def uberZoneInterestComplete(self):
        base.localAvatar.b_setLocation(self.districtObj.doId, 5)
        if self.timeManager:
            if self.timeManager.synchronize('startup'):
                self.accept('gotTimeSync', self.gotTimeSync)
            else:
                self.notify.warning('No sync from TimeManager.')
                self.gotTimeSync()
            DistributedSmoothNode.globalActivateSmoothing(1, 0)
        else:
            self.notify.warning('No TimeManager present.')
            DistributedSmoothNode.activateSmoothing(0, 0)

        base.localAvatar.enableButton()
