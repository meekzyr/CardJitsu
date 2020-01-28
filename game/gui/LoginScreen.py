from direct.gui.DirectGui import *
from direct.fsm import StateData
from panda3d.core import *
from . import GuiScreen
from direct.gui import DirectGuiGlobals as DGG


class LoginScreen(StateData.StateData, GuiScreen.GuiScreen):
    def __init__(self):
        self.notify.debug('__init__')
        StateData.StateData.__init__(self, 'done')
        GuiScreen.GuiScreen.__init__(self)
        self.userGlobalFocusHandler = None

        self.userName = ''
        self.password = ''

    def load(self):
        masterScale = 0.8
        textScale = 0.1 * masterScale
        entryScale = 0.08 * masterScale
        lineHeight = 0.21 * masterScale
        buttonScale = 1.15 * masterScale
        self.frame = DirectFrame(parent=aspect2d, relief=None, sortOrder=DGG.GEOM_SORT_INDEX)
        linePos = -0.26
        self.nameLabel = DirectLabel(parent=self.frame, relief=None, pos=(-0.21, 0, linePos),
                                     text='Username:', text_scale=textScale,
                                     text_align=TextNode.ARight)
        self.nameEntry = DirectEntry(parent=self.frame, relief=DGG.SUNKEN, borderWidth=(0.1, 0.1), scale=entryScale,
                                     pos=(-0.125, 0.0, linePos), width=9.1, numLines=1, focus=0,
                                     cursorKeys=1)
        linePos -= lineHeight
        self.passwordLabel = DirectLabel(parent=self.frame, relief=None, pos=(-0.21, 0, linePos),
                                         text='Password', text_scale=textScale,
                                         text_align=TextNode.ARight)
        self.passwordEntry = DirectEntry(parent=self.frame, relief=DGG.SUNKEN, borderWidth=(0.1, 0.1), scale=entryScale,
                                         pos=(-0.125, 0.0, linePos), width=9.1, numLines=1,
                                         focus=0, cursorKeys=1, obscured=1, command=self.__handleLoginPassword)
        linePos -= lineHeight
        self.loginButton = DirectButton(parent=self.frame, relief=DGG.RAISED, borderWidth=(0.01, 0.01),
                                        pos=(0, 0, linePos), scale=buttonScale, text='Login',
                                        text_scale=0.06, text_pos=(0, -0.02), command=self.__handleLoginButton)

    def unload(self):
        self.notify.debug('unload')
        self.nameEntry.destroy()
        self.passwordEntry.destroy()
        self.loginButton.destroy()
        self.frame.destroy()

    def __handleLoginPassword(self, password):
        if password != '':
            if self.nameEntry.get() != '':
                self.__handleLoginButton()

    def __handleLoginButton(self):
        self.removeFocus()
        self.userName = self.nameEntry.get()
        self.password = self.passwordEntry.get()
        if self.userName != '' and self.password != '':
            base.cr.authManager.d_requestLogin(self.userName, self.password)
