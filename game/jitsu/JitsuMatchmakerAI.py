from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from .DistributedCardJitsuAI import DistributedCardJitsuAI
from .CardJitsuGlobals import *

import copy


class JitsuMatchmakerAI(DirectObject):
    notify = directNotify.newCategory('JitsuMatchmakerAI')
    TaskDelay = 5.5

    def __init__(self, air):
        DirectObject.__init__(self)
        self.air = air

        self.playersQueueing = []
        self.queueByRanks = {}
        self.rankExtensions = {}  # avID -> rank delta (up or down)
        self.games = {}
        self.zone2Game = {}
        self.avId2Rank = {}

    def startMatchmaking(self):
        taskMgr.doMethodLater(self.TaskDelay, self.matchmakerTask, 'matchmaker')

    def matchmakerTask(self, task):
        matches = []
        done = []

        for _rank, players in self.queueByRanks.items():
            for avId in players:
                if avId in done:
                    continue

                othersInRank = copy.copy(players)
                extension = self.rankExtensions.get(avId, 0)
                if extension:
                    avRank = self.avId2Rank[avId]
                    for extendedRank in range(avRank, avRank + extension):
                        othersInRank.extend(self.queueByRanks.get(extendedRank, []))

                    for lowerRank in range(avRank - extension, avRank):
                        othersInRank.extend(self.queueByRanks.get(lowerRank, []))

                    # remove any potential duplicates
                    othersInRank = list(set(othersInRank))

                othersInRank.remove(avId)
                self.notify.debug(['mmTask', othersInRank, extension, avId, self.queueByRanks])
                if len(othersInRank) + 1 < NUM_PLAYERS:
                    self.rankExtensions[avId] += 1
                else:
                    match = [avId, othersInRank[0]]
                    done.extend(match)
                    matches.append(match)

        self.notify.debug(['matches made', matches])
        for playersMatched in matches:
            zoneId = self.air.allocateChannel()
            for playerId in playersMatched:
                self.games[playerId] = zoneId
                player = self.air.doId2do.get(playerId)
                player.sendUpdate('setGameZone', [zoneId])

                # cleanup the player
                if playerId in self.playersQueueing:
                    self.playerLeft(playerId)

            game = DistributedCardJitsuAI(self.air, f'Jitsu{str(sum(playersMatched))}')
            game.zoneId = zoneId
            game.generateOtpObject(self.air.districtId, zoneId)
            self.zone2Game[zoneId] = game

        return task.again

    def playerEntered(self, avId):
        av = self.air.doId2do.get(avId)
        if av:
            rank = av.getBeltLevel()

            if rank not in self.queueByRanks:
                self.queueByRanks[rank] = [avId]
            else:
                self.queueByRanks[rank].append(avId)

            self.avId2Rank[avId] = rank

        self.rankExtensions[avId] = 0

        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.playerLeft, [avId])
        self.playersQueueing.append(avId)

    def playerLeft(self, avId):
        if avId not in self.playersQueueing:
            return

        if avId in self.rankExtensions:
            del self.rankExtensions[avId]

        if avId in self.avId2Rank:
            del self.avId2Rank[avId]

        for rank in self.queueByRanks:
            if avId in self.queueByRanks[rank]:
                self.queueByRanks[rank].remove(avId)

        self.ignore(self.air.getAvatarExitEvent(avId))
        self.playersQueueing.remove(avId)
