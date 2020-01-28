from direct.distributed.DistributedObject import DistributedObject


class DistributedToonManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.cr = cr

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.cr.toonMgr = self
        messenger.send(self.cr.uniqueName('gotToonMgr'))

    def d_requestAvatar(self):
        self.sendUpdate('requestAvatar')
