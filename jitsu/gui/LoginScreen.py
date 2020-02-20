from direct.gui.DirectGui import *
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from ..jitsu.CardJitsuGlobals import FONT


class LoginScreen:
    def __init__(self):
        self.userName = ''
        self.password = ''
        self.frame = None
        self.logo = None
        self.usernameLabel = None
        self.usernameEntry = None
        self.passwordEntry = None
        self.passwordLabel = None
        self.loginButton = None
        self.createButton = None

    def load(self):
        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.frame = DirectFrame(parent=aspect2d, relief=None, sortOrder=DGG.GEOM_SORT_INDEX)
        self.logo = OnscreenImage(parent=base.a2dTopCenter, image='phase_maps/logo.png', scale=0.4, pos=(0, 0, -0.3))
        self.logo.setTransparency(TransparencyAttrib.MAlpha)
        self.usernameLabel = DirectLabel(parent=self.frame, relief=None, pos=(-0.21, 0, 0.1),
                                         text='Username:', text_scale=0.08, text_font=FONT,
                                         text_align=TextNode.ARight)
        self.usernameEntry = DirectEntry(parent=self.usernameLabel, relief=DGG.SUNKEN, borderWidth=(0.1, 0.1), scale=0.064,
                                         text_font=FONT, pos=(0.08, 0.0, 0.0), width=9.1, numLines=1, focus=0,
                                         cursorKeys=1)
        self.passwordLabel = DirectLabel(parent=self.frame, relief=None, pos=(-0.21, 0, -0.1),
                                         text='Password:', text_scale=0.08, text_font=FONT,
                                         text_align=TextNode.ARight)
        self.passwordEntry = DirectEntry(parent=self.passwordLabel, relief=DGG.SUNKEN, borderWidth=(0.1, 0.1), scale=0.064,
                                         pos=(0.08, 0.0, 0), width=9.1, numLines=1, text_font=FONT,
                                         focus=0, cursorKeys=1, obscured=1, command=self.__handleLoginPassword)
        self.loginButton = DirectButton(parent=self.frame, relief=None, borderWidth=(0.01, 0.01),
                                        image=(upButton, downButton, rolloverButton),
                                        image_color=(1, 0, 0, 1), image_scale=(3, 1, 1),
                                        pos=(0, 0, -0.3), scale=0.919, text='Login', text_font=FONT,
                                        text_scale=0.06, text_pos=(0, -0.02), command=self.__handleScreenButton)
        self.createButton = DirectButton(parent=self.frame, relief=None, borderWidth=(0.01, 0.01),
                                         image=(upButton, downButton, rolloverButton),
                                         image_color=(1, 0, 0, 1), image_scale=(3, 1, 1),
                                         pos=(0, 0, -0.43), scale=0.919, text='Create Account', text_font=FONT,
                                         text_scale=0.06, text_pos=(0, -0.02), command=self.__handleScreenButton,
                                         extraArgs=[True])
        buttonModels.removeNode()

    def unload(self):
        self.usernameEntry.destroy()
        self.passwordEntry.destroy()
        self.usernameLabel.destroy()
        self.passwordLabel.destroy()
        self.loginButton.destroy()
        self.createButton.destroy()
        self.logo.destroy()
        self.frame.destroy()

    def __handleLoginPassword(self, password):
        if password != '':
            if self.usernameEntry.get() != '':
                self.__handleScreenButton()

    def __handleScreenButton(self, creating=False):
        self.userName = self.usernameEntry.get()
        self.password = self.passwordEntry.get()
        if self.userName != '' and self.password != '':
            base.cr.authManager.d_requestLogin(self.userName, self.password, creating)
