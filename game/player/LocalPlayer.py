from .DistributedPlayer import DistributedPlayer
from ..jitsu.CardJitsuGlobals import FONT
from direct.gui.DirectButton import *
from direct.gui.DirectDialog import YesNoDialog


class LocalPlayer(DistributedPlayer):
    ownerview = True

    def __init__(self, cr):
        DistributedPlayer.__init__(self, cr)
        self.startButton = None
        self.requeueDialog = None
        self.gameInterest = None

    def delete(self):
        if self.startButton:
            self.startButton.destroy()
            self.startButton = None

        if self.requeueDialog:
            self.requeueDialog.destroy()
            self.requeueDialog = None

        if self.gameInterest:
            self.cr.removeInterest(self.gameInterest, 'clearInterestDone')
            self.gameInterest = None

        DistributedPlayer.delete(self)

    def startButtonPushed(self):
        if self.startButton:
            self.startButton.destroy()
            self.startButton = None

        self.d_sendReady()

    def enableButton(self):
        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.startButton = DirectButton(parent=base.a2dTopRight, relief=None, text='Queue', text_fg=(1, 1, 0.65, 1),
                                        text_font=FONT, text_pos=(0, -.23), text_scale=0.6, pos=(-0.3, 0, -0.65),
                                        scale=0.15, image=(upButton, downButton, rolloverButton),
                                        image_color=(1, 0, 0, 1),  image_scale=(20, 1, 11),
                                        command=self.startButtonPushed)
        buttonModels.removeNode()

    def requeueResponse(self, queue):
        self.notify.warning(['requeueResponse', queue])

        if queue:
            self.d_sendReady()
        else:
            self.enableButton()

        if self.requeueDialog:
            self.requeueDialog.destroy()
            self.requeueDialog = None

    def askForRequeue(self):
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okImageList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'),
                       buttons.find('**/ChtBx_OKBtn_Rllvr'))
        cancelImageList = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'),
                           buttons.find('**/CloseBtn_Rllvr'))
        buttons.removeNode()
        self.requeueDialog = YesNoDialog(text='Would you like to requeue?',
                                         button_text_pos=(0, -0.1),
                                         button_relief=None,
                                         buttonImageList=[okImageList, cancelImageList],
                                         button_text_font=FONT,
                                         text_font=FONT,
                                         command=self.requeueResponse)

    def setGameZone(self, gameZone):
        if self.gameInterest:
            self.cleanupGameInterest()

        self.gameInterest = self.cr.addInterest(self.parentId, gameZone, 'gameInterest', 'interestComplete')

    def cleanupGameInterest(self):
        self.cr.removeInterest(self.gameInterest, 'interestComplete')
        self.gameInterest = None
