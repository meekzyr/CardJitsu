from .DistributedPlayer import DistributedPlayer
from ..jitsu.CardJitsuGlobals import FONT
from direct.gui.DirectDialog import YesNoDialog
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL


class LocalPlayer(DistributedPlayer):
    ownerview = True

    def __init__(self, cr):
        DistributedPlayer.__init__(self, cr)
        self.requeueFrame = None
        self.requeueDialog = None
        self.gameInterest = None

    def delete(self):
        if self.requeueDialog:
            self.requeueDialog.destroy()
            self.requeueDialog = None

        if self.requeueFrame:
            self.requeueFrame.destroy()
            self.requeueFrame = None

        if self.gameInterest:
            self.cr.removeInterest(self.gameInterest, 'clearInterestDone')
            self.gameInterest = None

        DistributedPlayer.delete(self)

    def requeueResponse(self, queue):
        if queue:
            self.d_sendReady()
        else:
            self.cr.mainMenu.load()
            self.cr.mainMenu.buttons[0]['state'] = NORMAL

        if self.requeueDialog:
            self.requeueDialog.destroy()
            self.requeueDialog = None

        if self.requeueFrame:
            self.requeueFrame.destroy()
            self.requeueFrame = None

    def askForRequeue(self):
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okImageList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'),
                       buttons.find('**/ChtBx_OKBtn_Rllvr'))
        cancelImageList = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'),
                           buttons.find('**/CloseBtn_Rllvr'))
        buttons.removeNode()
        self.cr.mainMenu.buttons[0]['state'] = DISABLED
        self.requeueFrame = DirectFrame(relief=None, image=loader.loadModel('phase_13/models/gui/fade'),
                                        image_scale=(5, 2, 2), image_color=(0, 0, 0, 0.3), image_pos=(0.5, 0, 0),
                                        state=NORMAL, sortOrder=20)
        self.requeueDialog = YesNoDialog(parent=self.requeueFrame, text='Would you like to requeue?',
                                         button_text_pos=(0, -0.1), button_relief=None,
                                         buttonImageList=[okImageList, cancelImageList], button_text_font=FONT,
                                         text_font=FONT, command=self.requeueResponse)

    def setGameZone(self, gameZone):
        if self.gameInterest:
            self.cleanupGameInterest()

        self.gameInterest = self.cr.addInterest(self.parentId, gameZone, 'gameInterest', 'interestComplete')

    def cleanupGameInterest(self):
        self.cr.removeInterest(self.gameInterest, 'interestComplete')
        self.gameInterest = None
