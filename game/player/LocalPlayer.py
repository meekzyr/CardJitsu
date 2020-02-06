from .DistributedPlayer import DistributedPlayer
from ..jitsu.CardJitsuGlobals import FONT
from direct.gui.DirectDialog import YesNoDialog


class LocalPlayer(DistributedPlayer):
    ownerview = True

    def __init__(self, cr):
        DistributedPlayer.__init__(self, cr)
        self.requeueDialog = None
        self.gameInterest = None

    def delete(self):
        if self.requeueDialog:
            self.requeueDialog.destroy()
            self.requeueDialog = None

        if self.gameInterest:
            self.cr.removeInterest(self.gameInterest, 'clearInterestDone')
            self.gameInterest = None

        DistributedPlayer.delete(self)

    def requeueResponse(self, queue):
        if queue:
            self.d_sendReady()
        else:
            self.cr.mainMenu.load()

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
