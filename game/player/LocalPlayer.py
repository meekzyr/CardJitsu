from .DistributedPlayer import DistributedPlayer
from direct.gui.DirectButton import *

from ..gui.LoginScreen import LoginScreen

class LocalPlayer(DistributedPlayer):
    ownerview = True

    def __init__(self, cr):
        DistributedPlayer.__init__(self, cr)

    def postGenerateMessage(self):
        self.enableButton()
        DistributedPlayer.postGenerateMessage(self)

    def startButtonPushed(self):
        self.sendUpdate('readyToPlay', [])

    def enableButton(self):
        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.startButton = DirectButton(relief=None, text='Start', text_fg=(1, 1, 0.65, 1), text_pos=(0, -.23),
                                        text_scale=0.6, image=(upButton, downButton, rolloverButton),
                                        image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), pos=(0.92, 0, 0.3),
                                        scale=0.15, command=self.startButtonPushed)
