from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.fsm import ClassicFSM, State
from game.jitsu.CardJitsuGlobals import *
from direct.distributed.ClockDelta import *
from direct.directnotify.DirectNotifyGlobal import directNotify
import copy
import random


class DistributedCardJitsuAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedCardJitsuAI')
    CleanupDelay = 7.5

    def __init__(self, air, name):
        DistributedNodeAI.__init__(self, air)
        self.name = name
        self.air = air

        self.timerEnd = 0
        self.playersSitting = 0

        self.resultReady = []
        self.waitingOn = []
        self.wantStart = []
        self.activePlayers = []
        self.playersObserving = []

        self.currentTurn = []
        self.playerDecks = {}
        self.roundResults = {}
        self.remainingCards = {}

        self.fsm = ClassicFSM.ClassicFSM('CardJitsu', [
         State.State('waitingToBegin', self.enterWaitingToBegin, self.exitWaitingToBegin, ['playing']),
         State.State('playing', self.enterPlaying, self.exitPlaying, ['gameOver']),
         State.State('gameOver', self.enterGameOver, self.exitGameOver, ['waitingToBegin'])],
                                         'waitingToBegin', 'waitingToBegin')
        self.fsm.enterInitialState()

    def handleEmptyGame(self):
        self.fsm.request('waitingToBegin')

    def setGameCountdownTime(self):
        self.timerEnd = globalClock.getRealTime() + 10

    def requestTimer(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'setTimer', [globalClockDelta.localToNetworkTime(self.timerEnd)])

    def enterWaitingToBegin(self):
        self.setGameCountdownTime()

    def exitWaitingToBegin(self):
        pass

    def enterPlaying(self):
        pass #self.sendUpdate('setTurnTimer', [globalClockDelta.localToNetworkTime(self.turnEnd)])

    def exitPlaying(self):
        pass

    def enterGameOver(self):
        self.fsm.request('waitingToBegin')

    def exitGameOver(self):
        pass

    def getTimer(self):
        return 0

    def d_startGame(self):
        self.fsm.request('playing')
        self.sendUpdate('startGame', [self.activePlayers])

    def d_gameOver(self, result, resultId):
        self.sendUpdate('gameOver', [result, resultId])

    def d_receiveCards(self, avId, cards):
        self.sendUpdateToAvatarId(avId, 'receiveCards', [cards])

    def delete(self):
        self.fsm.requestFinalState()
        self.timerEnd = 0
        self.playersSitting = 0

        self.resultReady = []
        self.wantStart = []
        self.activePlayers = []
        self.playersObserving = []

        self.currentTurn = []
        self.playerDecks = {}
        self.roundResults = {}
        self.remainingCards = {}
        del self.fsm

        DistributedNodeAI.delete(self)

    def addCard(self, avId):
        remaining = self.remainingCards[avId]
        if not remaining:
            remaining = self.remainingCards[avId] = list(copy.copy(ALL_DECK))

        card = random.choice(remaining)
        self.remainingCards[avId].remove(card)
        self.playerDecks[avId].append(card)
        self.d_receiveCards(avId, [card])

    def generateStartingDecks(self):
        self.waitingOn = copy.copy(self.activePlayers)

        for avId in self.activePlayers:
            ind = self.activePlayers.index(avId)
            if ind == 1:
                otherInd = 0
            else:
                otherInd = 1

            otherAv = self.air.doId2do.get(self.activePlayers[otherInd])
            skillLevel = otherAv.getBeltLevel()
            self.sendUpdateToAvatarId(avId, 'setOpponentName', [otherAv.getName(), skillLevel])

            localDeck = list(copy.copy(ALL_DECK))
            deck = []
            for i in range(0, NUM_CARDS):
                _card = random.choice(localDeck)
                localDeck.remove(_card)
                deck.append(_card)

            self.remainingCards[avId] = localDeck
            self.playerDecks[avId] = deck
            self.d_receiveCards(avId, deck)

        self.d_startGame()
        self.turnStarted()

    def informGameOfPlayer(self):
        self.playersSitting += 1
        if self.playersSitting < 2:
            self.timerEnd = 0
        elif self.playersSitting == 2:
            self.timerEnd = globalClock.getRealTime() + 20

        self.sendUpdate('setTimer', [globalClockDelta.localToNetworkTime(self.timerEnd)])

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        taskMgr.remove(self.taskName('calculateResult'))
        self.handlePlayerExit(avId)

    def handlePlayerExit(self, avId):
        self.playersSitting -= 1
        self.sendUpdate('setTimer', [0])

        self.ignore(self.air.getAvatarExitEvent(avId))

        if avId in self.wantStart:
            self.wantStart.remove(avId)

        if avId in self.roundResults:
            del self.roundResults[avId]

        if self.fsm.getCurrentState().getName() == 'playing':
            if len(self.activePlayers) == NUM_PLAYERS:
                self.d_gameOver(PLAYER_QUIT, avId)

        if avId in self.activePlayers:
            self.activePlayers.remove(avId)
            del self.playerDecks[avId]

        if not self.activePlayers:
            taskMgr.doMethodLater(self.CleanupDelay, self.delayedDelete, self.taskName('delete'))

    def delayedDelete(self, task):
        self.requestDelete()
        return task.done

    def requestBegin(self):
        avId = self.air.getAvatarIdFromSender()

        if len(self.activePlayers) < NUM_PLAYERS:
            self.activePlayers.append(avId)
            self.acceptOnce(self.air.getAvatarExitEvent(avId), self.handlePlayerExit, [avId])

            if avId not in self.playerDecks:
                self.playerDecks[avId] = []
            if avId not in self.roundResults:
                self.roundResults[avId] = {}

        if len(self.activePlayers) == NUM_PLAYERS:
            self.generateStartingDecks()

    def calculateRoundResult(self, task=None):
        card1, card2 = self.currentTurn
        track1, tier1, av1 = card1
        track2, tier2, av2 = card2

        if card1 == card2:
            winnerId = 0  # draw
        elif track1 == track2:
            if tier1 > tier2:
                winnerId = av1
                winningTrack = track1
                winningTier = tier1
            elif tier2 > tier1:
                winnerId = av2
                winningTrack = track2
                winningTier = tier2
            elif tier1 == tier2:
                winnerId = 0
        else:
            # Fire beats Snow
            # Snow beats Water
            # Water beats Fire
            if (track1 == TRACK_FIRE and track2 == TRACK_ICE) or (track1 == TRACK_ICE and track2 == TRACK_WATER)\
                    or (track1 == TRACK_WATER and track2 == TRACK_FIRE):
                winnerId = av1
                winningTrack = track1
                winningTier = tier1
            elif (track2 == TRACK_FIRE and track1 == TRACK_ICE) or (
                    track2 == TRACK_ICE and track1 == TRACK_WATER) \
                    or (track2 == TRACK_WATER and track1 == TRACK_FIRE):
                winnerId = av2
                winningTrack = track2
                winningTier = tier2
            else:
                self.notify.warning(['unhandled event', card1, card2])
                winnerId = 0

        if winnerId:
            # return the winning card as default, as that will only be used when
            # the other avatar has left as this task runs
            results = self.roundResults.get(winnerId, {winningTrack: [winningTier]})
            if winningTrack not in results:
                self.roundResults[winnerId][winningTrack] = [winningTier]
            else:
                if winningTier not in results[winningTrack]:
                    self.roundResults[winnerId][winningTrack].append(winningTier)

        self.sendUpdate('roundResult', [winnerId, [[track1, tier1], [track2, tier2]]])
        self.currentTurn = []
        if task:
            return task.done

    def resultFinished(self):
        avId = self.air.getAvatarIdFromSender()

        if avId not in self.resultReady:
            self.resultReady.append(avId)

        if len(self.resultReady) == len(self.activePlayers):
            won = 0
            for avId in self.activePlayers:
                if won:
                    continue

                results = self.roundResults[avId]
                tracksWon = 0
                tiersUsed = set([])
                for track, wins in results.items():
                    unique = tiersUsed ^ set(wins)
                    if unique:
                        tracksWon += 1
                        tiersUsed = set(tiersUsed | unique)

                    if len(wins) >= 3 or tracksWon >= 3:
                        won = avId
                        break

                if not won:
                    self.addCard(avId)

            if won:
                winner = self.air.doId2do.get(won)
                winner.addWin()
                # TODO: maybe the loser loses a point
                self.d_gameOver(PLAYER_WON, won)
                self.fsm.request('gameOver')
            else:
                self.turnStarted()

            self.resultReady = []
            self.waitingOn = copy.copy(self.activePlayers)

    def turnStarted(self):
        self.timerEnd = globalClock.getRealTime() + SELECTION_TIMEOUT
        taskMgr.doMethodLater(SELECTION_TIMEOUT, self.handleSelectTimeout, self.taskName('timeoutTask'))
        self.sendUpdate('setTimer', [globalClockDelta.localToNetworkTime(self.timerEnd)])

    def handleSelectTimeout(self, task):
        if len(self.currentTurn) != len(self.activePlayers):
            for avId in self.waitingOn:
                self.sendUpdateToAvatarId(avId, 'forcePick', [])

        return task.done

    def requestSelectCard(self, cardIndex, trackId, cardTier):
        avId = self.air.getAvatarIdFromSender()
        deck = self.playerDecks.get(avId)
        if not deck:
            return

        self.currentTurn.append([trackId, cardTier, avId])
        self.waitingOn.remove(avId)
        self.playerDecks[avId].remove((trackId, cardTier))
        self.sendUpdate('cardSelected', [avId, cardIndex])
        if len(self.currentTurn) == len(self.activePlayers):
            # time to get the result
            taskMgr.remove(self.taskName('timeoutTask'))
            taskMgr.doMethodLater(3.5, self.calculateRoundResult, self.taskName('calculateResult'))
