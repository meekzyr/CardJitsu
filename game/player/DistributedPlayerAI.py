from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from game.jitsu import CardJitsuGlobals


class DistributedPlayerAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedPlayerAI')

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        self.beltLevel = 0
        self.winCount = 0
        self._name = ''

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def queueReady(self):
        self.air.matchmaker.playerEntered(self.doId)

    def setBeltLevel(self, beltLevel):
        self.notify.warning(['setBeltLevel', self.doId, beltLevel, self.beltLevel])
        self.beltLevel = beltLevel

    def d_setBeltLevel(self, beltLevel):
        self.sendUpdate('setBeltLevel', [beltLevel])

    def b_setBeltLevel(self, beltLevel):
        self.setBeltLevel(beltLevel)
        self.d_setBeltLevel(beltLevel)

    def getBeltLevel(self):
        return self.beltLevel

    def setWinCount(self, winCount):
        self.winCount = winCount

    def d_setWinCount(self, winCount):
        self.sendUpdate('setWinCount', [winCount])

    def b_setWinCount(self, winCount):
        self.setWinCount(winCount)
        self.d_setWinCount(winCount)

    def getWinCount(self):
        return self.winCount

    def addWin(self):
        newCount = self.winCount + 1
        currentBelt = self.beltLevel
        self.b_setWinCount(newCount)

        if newCount <= 88:
            newBelt = CardJitsuGlobals.getBeltLevel(newCount)
            if newBelt != currentBelt:
                self.b_setBeltLevel(newBelt)
