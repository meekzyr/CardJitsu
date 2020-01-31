from direct.distributed.DistributedNode import DistributedNode


class DistributedPlayer(DistributedNode):
    notify = directNotify.newCategory('DistributedPlayer')
    ownerview = False

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self._name = ''
        self.beltLevel = 0

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def setBeltLevel(self, beltLevel):
        self.beltLevel = beltLevel

    def getBeltLevel(self):
        return self.beltLevel
