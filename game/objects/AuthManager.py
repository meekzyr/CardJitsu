from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.gui.OnscreenText import OnscreenText
from .AuthGlobals import *


class AuthManager(DistributedObjectGlobal):

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.cr.authManager = self
        self.invalidText = None

    def delete(self):
        if self.invalidText:
            self.invalidText.destroy()
            self.invalidText = None

        self.cr.authManager = None
        DistributedObjectGlobal.delete(self)

    def cleanupText(self, task=None):
        if self.invalidText:
            self.invalidText.destroy()
            self.invalidText = None
        if task:
            return task.done
        else:
            taskMgr.remove(self.uniqueName('loginFailed'))

    def showLoginError(self, text):
        self.invalidText = OnscreenText(text, scale=0.15, fg=(1, 0, 0, 1), shadow=(0, 0, 0, 1), pos=(0, 0.2))
        self.invalidText.setBin('gui-popup', 0)
        taskMgr.remove(self.uniqueName('loginFailed'))
        taskMgr.doMethodLater(3, self.cleanupText, self.uniqueName('loginFailed'))

    def d_requestLogin(self, username, password, wantCreate):
        self.sendUpdate('requestLogin', [username, password, wantCreate])

    def requestAccess(self):
        self.sendUpdate('requestAccess', [])

    def accessResponse(self, success):
        print('accessResponse', [success])
        if success == INVALID_PASSWORD:
            self.showLoginError('Invalid username or password.')
        elif success == INVALID_USERNAME:
            self.showLoginError('Username is already taken.')
        elif success == INVALID_NOACCOUNT:
            self.showLoginError('No account is attached to that username.')
        elif success == LOGIN_SUCCESS:
            messenger.send('accessResponse', [success])
            self.cleanupText()
