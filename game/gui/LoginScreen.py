from direct.gui.DirectGui import *
from direct.fsm import StateData
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from ..jitsu.CardJitsuGlobals import FONT


class LoginScreen(StateData.StateData):
    def __init__(self):
        StateData.StateData.__init__(self, 'done')
        self.userGlobalFocusHandler = None

        self.userName = ''
        self.password = ''

        self.frame = None
        self.nameLabel = None
        self.nameEntry = None
        self.passwordEntry = None
        self.passwordLabel = None
        self.loginButton = None
        self.createButton = None

    def load(self):
        self.frame = DirectFrame(parent=aspect2d, relief=None, sortOrder=DGG.GEOM_SORT_INDEX)
        self.nameLabel = DirectLabel(parent=self.frame, relief=None, pos=(-0.21, 0, 0.1),
                                     text='Username:', text_scale=0.08, text_font=FONT,
                                     text_align=TextNode.ARight)
        self.nameEntry = DirectEntry(parent=self.frame, relief=DGG.SUNKEN, borderWidth=(0.1, 0.1), scale=0.064,
                                     pos=(-0.125, 0.0, 0.1), width=9.1, numLines=1, focus=0, cursorKeys=1)

        self.passwordLabel = DirectLabel(parent=self.frame, relief=None, pos=(-0.21, 0, -0.1),
                                         text='Password:', text_scale=0.08, text_font=FONT,
                                         text_align=TextNode.ARight)
        self.passwordEntry = DirectEntry(parent=self.frame, relief=DGG.SUNKEN, borderWidth=(0.1, 0.1), scale=0.064,
                                         pos=(-0.125, 0.0, -0.1), width=9.1, numLines=1,
                                         focus=0, cursorKeys=1, obscured=1, command=self.__handleLoginPassword)
        self.loginButton = DirectButton(parent=self.frame, relief=DGG.RAISED, borderWidth=(0.01, 0.01),
                                        pos=(-0.1, 0, -0.2), scale=0.919, text='Login', text_font=FONT,
                                        text_scale=0.06, text_pos=(0, -0.02), command=self.__handleScreenButton)
        self.createButton = DirectButton(parent=self.frame, relief=DGG.RAISED, borderWidth=(0.01, 0.01),
                                         pos=(0.25, 0, -0.2), scale=0.919, text='Create Account', text_font=FONT,
                                         text_scale=0.06, text_pos=(0, -0.02), command=self.__handleScreenButton,
                                         extraArgs=[True])

    def unload(self):
        self.notify.debug('unload')
        self.nameEntry.destroy()
        self.passwordEntry.destroy()
        self.loginButton.destroy()
        self.createButton.destroy()
        self.frame.destroy()

    def __handleLoginPassword(self, password):
        if password != '':
            if self.nameEntry.get() != '':
                self.__handleScreenButton()

    def __handleScreenButton(self, creating=False):
        self.userName = self.nameEntry.get()
        self.password = self.passwordEntry.get()
        if self.userName != '' and self.password != '':
            base.cr.authManager.d_requestLogin(self.userName, self.password, creating)
