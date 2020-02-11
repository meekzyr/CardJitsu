from panda3d.core import *
from direct.distributed.ClientRepositoryBase import ClientRepositoryBase
from direct.distributed.MsgTypes import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import DistributedSmoothNode
from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals
from jitsu.player import LocalPlayer
import sys
from ..jitsu.CardJitsuGlobals import FONT
from jitsu.gui.LoginScreen import LoginScreen
from jitsu.gui.MainMenu import MainMenu

DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))


class JitsuClientRepository(ClientRepositoryBase):
    taskChain = 'net'

    def __init__(self):
        ClientRepositoryBase.__init__(self, connectMethod=self.CM_NET, threadedNet=True)
        self.GameGlobalsId = 1000
        self.zoneInterest = None
        self.visInterest = None
        self.districtObj = None
        self.url = None
        self.connectionBox = None
        self.failureText = None

        self.authManager = self.generateGlobalObject(1001, 'AuthManager')
        self.loginInterface = None
        self.mainMenu = None
        self.gameVersion = base.config.GetString('base-version', 'dev')

        # No jitsu, no avatar (yet).
        base.localAvatar = None

        self.mainBg = loader.loadModel('phase_3/models/gui/background')
        self.mainBg.reparentTo(aspect2d, DirectGuiGlobals.BACKGROUND_SORT_INDEX)
        self._startConnecting()

    def _startConnecting(self):
        self.connectionBox = DirectDialog(text='Connecting...', text_font=FONT)
        taskMgr.doMethodLater(0.1, self.startConnect, 'connection-start')

    def lostConnection(self):
        if self.failureText:
            self.failureText.destroy()
            self.failureText = None

        if self.connectionBox:
            self.connectionBox.destroy()
            self.connectionBox = None

        self.notify.warning("Lost connection to gameserver.")
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okImageList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'),
                       buttons.find('**/ChtBx_OKBtn_Rllvr'))
        cancelImageList = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'),
                           buttons.find('**/CloseBtn_Rllvr'))
        self.failureText = YesNoDialog(text='Lost connection to the gameserver.\n Would you like to retry?',
                                       button_text_pos=(0, -0.1), button_relief=None, button_text_font=FONT,
                                       buttonImageList=[okImageList, cancelImageList], text_font=FONT,
                                       text_align=TextNode.ACenter, command=self.failDiagResponse)

        #base.transitions.fadeScreen(alpha=1)
        #render.hide()

    def exit(self):
        if self.isConnected():
            self.sendDisconnect()
            self.disconnect()

        sys.exit()

    def startConnect(self, task=None):
        tcpPort = base.config.GetInt('gameserver-port', 7198)
        hostname = base.config.GetString('gameserver-host', '127.0.0.1')
        if not hostname:
            hostname = '127.0.0.1'
        self.url = URLSpec('g://%s' % hostname, 1)
        self.url.setPort(tcpPort)

        self.connect([self.url], successCallback=self.connectSuccess, failureCallback=self.connectFailure,
                     successArgs=[task], failureArgs=[task])

    def failDiagResponse(self, retry):
        if retry:
            if self.failureText:
                self.failureText.destroy()
                self.failureText = None

            self._startConnecting()
        else:
            self.exit()

    def connectFailure(self, statusCode, statusString, task):
        if self.connectionBox:
            self.connectionBox.destroy()
            self.connectionBox = None

        if self.failureText:
            self.failureText.destroy()
            self.failureText = None

        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okImageList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'),
                       buttons.find('**/ChtBx_OKBtn_Rllvr'))
        cancelImageList = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'),
                           buttons.find('**/CloseBtn_Rllvr'))
        self.failureText = YesNoDialog(text='Unable to connect to the gameserver.\n Would you like to retry?',
                                       button_text_pos=(0, -0.1), button_relief=None, button_text_font=FONT,
                                       buttonImageList=[okImageList, cancelImageList], text_font=FONT,
                                       text_align=TextNode.ACenter, command=self.failDiagResponse)
        if task:
            return task.done

    def connectSuccess(self, task):
        if self.failureText:
            self.failureText.destroy()
            self.failureText = None

        if self.connectionBox:
            self.connectionBox.destroy()
            self.connectionBox = None

        dg = PyDatagram()
        dg.addUint16(CLIENT_HELLO)
        dg.addUint32(self.hashVal)
        dg.addString(self.gameVersion)
        self.send(dg)

        if not self.loginInterface:
            self.loginInterface = LoginScreen()
            self.loginInterface.load()

        if task:
            return task.done

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

        if self.districtObj:
            self._relocateAv()
        else:
            self.acceptOnce('gotDistrict', self._relocateAv)

        self.doId2do[avatarId] = localAvatar

    def _relocateAv(self):
        base.localAvatar.b_setLocation(self.districtObj.doId, 5)

        self.mainMenu = MainMenu()
        self.mainMenu.load()

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

    def uberZoneInterestComplete(self):
        if self.timeManager:
            DistributedSmoothNode.globalActivateSmoothing(1, 0)
        else:
            self.notify.warning('No TimeManager present.')
            DistributedSmoothNode.activateSmoothing(0, 0)
