from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal


class AuthManager(DistributedObjectGlobal):

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.cr.authManager = self

    def delete(self):
        self.cr.authManager = None
        DistributedObjectGlobal.delete(self)

    def d_requestLogin(self, username, password):
        self.sendUpdate('requestLogin', [username, password])

    def requestAccess(self):
        self.sendUpdate('requestAccess', [])

    def accessResponse(self, success):
        print('accessResponse', [success])
        if success == 0:
            self.cr.handleFailedLogin()
        elif success == 1:
            messenger.send('accessResponse', [success])
