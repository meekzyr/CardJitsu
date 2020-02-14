from direct.distributed.DistributedNode import DistributedNode


class DistributedPlayer(DistributedNode):
    notify = directNotify.newCategory('DistributedPlayer')
    ownerview = False

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self._name = ''
        self.winCount = 0
        self.beltLevel = 0
        self.dnaString = ''

    def setDNAString(self, dnaString):
        self.dnaString = dnaString

    def b_setDNAString(self, string):
        self.d_setDNAString(string)
        self.setDNAString(string)

    def d_setDNAString(self, string):
        self.sendUpdate('setDNAString', [string])

    def getDNAString(self):
        return self.dnaString

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

    def d_requestSensei(self):
        self.sendUpdate('requestSensei')

    def d_sendReady(self):
        self.sendUpdate('queueReady')
