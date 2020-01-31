from panda3d.core import *
from direct.distributed.ClientRepositoryBase import ClientRepositoryBase
from direct.distributed.MsgTypes import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import DistributedSmoothNode
from direct.gui.DirectGui import *
from game.player import LocalPlayer
import sys
from game.gui.LoginScreen import LoginScreen


class JitsuClientRepository(ClientRepositoryBase):
    taskChain = 'net'

    def __init__(self, threadedNet=True):
        ClientRepositoryBase.__init__(self, dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                      connectMethod=self.CM_NET, threadedNet=threadedNet)

        self.GameGlobalsId = 1000
        self.zoneInterest = None
        self.visInterest = None
        self.districtObj = None
        self.url = None
        self.failureText = None
        self.invalidText = None
        self.waitingText = None
        self.shardHandle = None

        self.authManager = self.generateGlobalObject(1001, 'AuthManager')
        self.loginInterface = None
        self.gameVersion = base.config.GetString('base-version', 'dev')

        # Allow some time for other processes.  This also allows time
        # each frame for the network thread to run.
        base.setSleep(0.01)

        # No game, no avatar (yet).
        base.localAvatar = None

    def lostConnection(self):
        self.notify.warning("Lost connection to gameserver.")

        cbMgr = CullBinManager.getGlobalPtr()
        cbMgr.addBin('gui-popup', cbMgr.BTUnsorted, 60)

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

        self.waitingText = OnscreenText('Connecting to %s.\nPress ESC to cancel.' % self.url, scale=0.1,
                                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

        self.connect([self.url], successCallback=self.connectSuccess, failureCallback=self.connectFailure)

    def connectFailure(self, statusCode, statusString):
        self.notify.warning('failure')
        self.waitingText.destroy()
        self.failureText = OnscreenText('Failed to connect to %s:\n%s.\nPress ESC to quit.' % (self.url, statusString),
                                        scale=0.15, fg=(1, 0, 0, 1), shadow=(0, 0, 0, 1), pos=(0, 0.2))

    def makeWaitingText(self):
        if self.waitingText:
            self.notify.warning('make destroy')
            self.waitingText.destroy()
        self.waitingText = OnscreenText('Waiting for base.', scale=0.1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

    def connectSuccess(self):
        """ Successfully connected.  But we still can't really do
        anything until we send an CLIENT_HELLO message. """
        if self.waitingText:
            self.waitingText.destroy()

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
        elif msgType == CLIENT_ENTER_OBJECT_REQUIRED_OTHER:
            self.handleGenerate(di, True)
        elif msgType == CLIENT_DONE_INTEREST_RESP:
            self.handleInterestDoneMessage(di)
        elif msgType == CLIENT_ENTER_OBJECT_REQUIRED_OWNER:
            self.handleGenerateOwner(di)
        elif msgType == CLIENT_ENTER_OBJECT_REQUIRED_OTHER_OWNER:
            self.handleGenerateOwner(di, True)
        elif msgType == CLIENT_OBJECT_LEAVING:
            self.handleDelete(di)

    def handleHelloResp(self):
        # self.startHeartbeat()
        self.acceptOnce('accessResponse', self.handleResponse)

    def sendHeartbeat(self):
        dg = PyDatagram()
        dg.addUint16(CLIENT_HEARTBEAT)
        self.send(dg)

    def sendDisconnect(self):
        print('Sending disconnect messsage')
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
        self.notify.warning(dclass.getName())

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

    def handleResponse(self, resp):
        if resp == 1:
            if self.loginInterface:
                self.loginInterface.unload()
                self.loginInterface = None

            taskMgr.remove(self.uniqueName('loginFailed'))
            if self.invalidText:
                self.invalidText.destroy()
                self.invalidText = None

            self.shardHandle = self.addInterest(self.GameGlobalsId, 3, 'shardHandle', event='shardHandleComplete')

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

    def handleFailedLogin(self):
        self.invalidText = OnscreenText('Invalid username or password.', scale=0.15, fg=(1, 0, 0, 1),
                                        shadow=(0, 0, 0, 1), pos=(0, 0.2))
        self.invalidText.setBin('gui-popup', 0)
        taskMgr.remove(self.uniqueName('loginFailed'))

        def cleanupText(task):
            if self.invalidText:
                self.invalidText.destroy()
                self.invalidText = None
            return task.done

        taskMgr.doMethodLater(3, cleanupText, self.uniqueName('loginFailed'))

