from .DistributedCardJitsuAI import DistributedCardJitsuAI
from .CardJitsuGlobals import BLACK, TRACK_FIRE, TRACK_ICE, TRACK_WATER
import random


class FakeToon:
    fake = True

    def __init__(self, doId):
        self._doId = doId

    @property
    def doId(self):
        return self._doId

    def getName(self):
        return 'Sensei'

    def getBeltLevel(self):
        return BLACK

    def getDNAString(self):
        return b't\x13\x01\x01\x01\x01\x1b\x01\x1b\x00\x1b\x19\x19\x19\x19'


class DistributedSenseiBattleAI(DistributedCardJitsuAI):
    notify = directNotify.newCategory('DistributedSenseiBattleAI')

    def __init__(self, air, name):
        self.air = air
        fakeId = self.air.allocateChannel()
        self._sensei = FakeToon(fakeId)
        self.air.doId2do[fakeId] = self._sensei
        DistributedCardJitsuAI.__init__(self, air, name)

    def delete(self):
        if self._sensei.doId in self.air.doId2do:
            del self.air.doId2do[self._sensei.doId]
        self._sensei = None
        DistributedCardJitsuAI.delete(self)

    def requestBegin(self):
        if self._sensei.doId not in self.activePlayers:
            self.activePlayers.append(self._sensei.doId)
        DistributedCardJitsuAI.requestBegin(self)

    def requestSelectCard(self, cardIndex, trackId, cardTier):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            self.notify.warning('av lost')
            return

        if av.getBeltLevel() < BLACK:
            _cardTier = random.randint(2, 6)
            if trackId == TRACK_FIRE:
                _trackId = TRACK_WATER
            elif trackId == TRACK_WATER:
                _trackId = TRACK_ICE
            elif trackId == TRACK_ICE:
                _trackId = TRACK_FIRE
            else:
                self.notify.warning('should not get here')
                _trackId = TRACK_FIRE
        else:
            _trackId, _cardTier = random.choice(self.playerDecks[self._sensei.doId])
            self.playerDecks[self._sensei.doId].remove((trackId, cardTier))

        self.currentTurn.append([_trackId, _cardTier, self._sensei.doId])
        if self._sensei.doId in self.waitingOn:
            self.waitingOn.remove(self._sensei.doId)
        self.sendUpdate('cardSelected', [self._sensei.doId, _cardTier - 1])

        DistributedCardJitsuAI.requestSelectCard(self, cardIndex, trackId, cardTier)
