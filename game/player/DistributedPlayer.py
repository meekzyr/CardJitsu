from direct.distributed.DistributedNode import DistributedNode


class DistributedPlayer(DistributedNode):
    notify = directNotify.newCategory('DistributedPlayer')
    ownerview = False

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self._name = ''
        self.winCount = 0
        self.beltLevel = 0

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def setWinCount(self, winCount):
        self.winCount = winCount

    def getWinCount(self):
        return self.winCount

    def setBeltLevel(self, beltLevel):
        self.beltLevel = beltLevel

    def getBeltLevel(self):
        return self.beltLevel

    def d_sendReady(self):
        self.sendUpdate('queueReady')
