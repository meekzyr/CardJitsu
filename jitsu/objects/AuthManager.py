from direct.distributed.DistributedObject import DistributedObject
from direct.gui.OnscreenText import OnscreenText
from .AuthGlobals import *


class AuthManager(DistributedObject):

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.cr.authManager = self
        self.invalidText = None
        self.shardHandle = None

    def delete(self):
        if self.shardHandle:
            self.cr.removeInterest(self.shardHandle, 'shardHandleComplete')
            self.shardHandle = None

        if self.invalidText:
            self.invalidText.destroy()
            self.invalidText = None

        self.cr.authManager = None
        DistributedObject.delete(self)

    def cleanupText(self, task=None):
        if self.invalidText:
            self.invalidText.destroy()
            self.invalidText = None
        if task:
            return task.done

        taskMgr.remove(self.uniqueName('loginFailed'))

    def showLoginError(self, text):
        self.invalidText = OnscreenText(text, scale=0.15, fg=(1, 0, 0, 1), shadow=(0, 0, 0, 1), pos=(0, 0.2))
        self.invalidText.setBin('gui-popup', 0)
        taskMgr.remove(self.uniqueName('loginFailed'))
        taskMgr.doMethodLater(3, self.cleanupText, self.uniqueName('loginFailed'))

    def d_requestLogin(self, username, password, wantCreate):
        self.sendUpdate('requestLogin', [username, password, wantCreate])

    def loginResponse(self, response):
        if response == INVALID_PASSWORD:
            self.showLoginError('Invalid username or password.')
        elif response == INVALID_USERNAME:
            self.showLoginError('Username is already taken.')
        elif response == INVALID_NOACCOUNT:
            self.showLoginError('No account is attached to that username.')
        elif response == LOGIN_SUCCESS:
            if self.cr.loginInterface:
                self.cr.loginInterface.unload()
                self.cr.loginInterface = None

            self.cleanupText()
            self.shardHandle = self.cr.addInterest(self.cr.GameGlobalsId, 3, 'shardHandle', event='shardHandleComplete')
