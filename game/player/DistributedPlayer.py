from direct.distributed.DistributedNode import DistributedNode


class DistributedPlayer(DistributedNode):
    notify = directNotify.newCategory('DistributedPlayer')
    ownerview = False

    def postGenerateMessage(self):
        self.notify.warning('player post generate, is local = %s' % self.ownerview)
