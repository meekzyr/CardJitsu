from direct.distributed.DistributedNode import DistributedNode
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from panda3d.core import *

from jitsu.gui.DustCloud import DustCloud
from jitsu.gui.Timer import Timer
from jitsu.gui.TextDisplay import TextDisplay
from jitsu.jitsu.CardJitsuGlobals import *
from ..player import ToonHead, ToonDNA

import random


def getDustCloudIval():
    dustCloud = DustCloud()
    dustCloud.setScale(0.14)
    dustCloud.createTrack()
    return Sequence(Wait(0.5), Func(dustCloud.reparentTo, aspect2d), dustCloud.track, Func(dustCloud.detachNode))


class DistributedCardJitsu(DistributedNode):
    notify = directNotify.newCategory('DistributedCardJitsu')

    def __init__(self, cr):
        NodePath.__init__(self, 'DistributedCardJitsu')
        DistributedNode.__init__(self, cr)
        self.reparentTo(render)
        self.localDeck = [None] * NUM_CARDS
        self.dummyDeck = [None] * NUM_CARDS
        self.cardButtons = {}
        self.roundResults = {}
        self.winIndicators = []

        self.turnPlayed = None
        self.leaveButton = None
        self.screenText = None
        self.wantTimer = True
        self.targetCard = None
        self.otherCard = None
        self.otherTrack = 0
        self.otherReturnPos = None

        self.ourFrame = None
        self.ourDot = None

        self.opponentFrame = None
        self.opponentSkillDot = None
        self.revealSequence = None

        self.bgm = loader.loadMusic('phase_audio/bgm/game_bgm.ogg')
        self.textDisplay = TextDisplay(FONT)

        self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.upButton = self.buttonModels.find('**//InventoryButtonUp')
        self.downButton = self.buttonModels.find('**/InventoryButtonDown')
        self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')

        particles = loader.loadModel('phase_3.5/models/props/suit-particles')
        snowModel = loader.loadModel('phase_13/models/props/ice_icon')
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')

        self.trackIcons = {TRACK_FIRE: particles.find('**/fire'),
                           TRACK_WATER: invModel.find('**/inventory_geyser'),
                           TRACK_ICE: snowModel.find('**/g1')}

        invModel.removeNode()
        particles.removeNode()
        snowModel.removeNode()

        self.clockNode = Timer(FONT)
        self.clockNode.setPos(1.16, 0, -.63)
        self.clockNode.setScale(0.5)
        self.clockNode.hide()
        self.fsm = ClassicFSM.ClassicFSM('CardJitsu', [
            State.State('WaitingToBegin', self.enterWaitingToBegin, self.exitWaitingToBegin, ['Playing', 'GameOver']),
            State.State('Playing', self.enterPlaying, self.exitPlaying, ['GameOver']),
            State.State('GameOver', self.enterGameOver, self.exitGameOver, ['WaitingToBegin'])], 'WaitingToBegin',
                                         'WaitingToBegin')
        self.fsm.enterInitialState()

    def delete(self):
        if self.bgm:
            self.bgm.stop()
            del self.bgm

        if self.revealSequence:
            self.revealSequence.clearToInitial()
            self.revealSequence = None

        if self.otherCard:
            self.otherCard.destroy()
            self.otherCard = None

        if self.opponentSkillDot:
            self.opponentSkillDot.destroy()
            self.opponentSkillDot = None

        if self.ourDot:
            self.ourDot.destroy()
            self.ourDot = None

        if self.opponentFrame:
            self.opponentFrame.destroy()
            self.opponentFrame = None

        if self.ourFrame:
            self.ourFrame.destroy()
            self.ourFrame = None

        self.textDisplay.destroy()

        self.clockNode.stop()
        self.clockNode.hide()

        # gameOver cleans up the various nodes and objects we've created
        self.turnPlayed = None
        for button in list(self.cardButtons.values()):
            button.destroy()

        self.cardButtons = {}

        for button in self.dummyDeck:
            if not button:
                continue

            button.destroy()

        self.dummyDeck = []
        self.localDeck = []

        for image in self.winIndicators:
            image.destroy()

        self.winIndicators = []

        for image in list(self.trackIcons.values()):
            image.removeNode()

        self.trackIcons = {}

        if self.leaveButton:
            self.leaveButton.destroy()
            self.leaveButton = None
        if self.screenText:
            self.screenText.destroy()
            self.screenText = None

        if self.buttonModels:
            self.buttonModels.removeNode()
            self.buttonModels = None

        if self.upButton:
            self.upButton.removeNode()
            self.upButton = None

        if self.downButton:
            self.downButton.removeNode()
            self.downButton = None

        if self.rolloverButton:
            self.rolloverButton.removeNode()
            self.rolloverButton = None

        DistributedNode.delete(self)

    def d_requestSelectCard(self, cardIndex, card):
        self.sendUpdate('requestSelectCard', [cardIndex, *card])

    def selectedCard(self, card):
        if self.turnPlayed is not None:
            return

        cardIndex = self.localDeck.index(card)
        for _card in list(self.cardButtons.values()):
            _card['state'] = DGG.DISABLED

        self.turnPlayed = card
        self.d_requestSelectCard(cardIndex, card)

    def cardSelected(self, avId, cardIndex):
        if avId != base.localAvatar.doId:
            target = OTHER_CARD_DEST
            card = self.dummyDeck[cardIndex]
        else:
            target = LOCAL_CARD_DEST
            info = self.localDeck[cardIndex]
            card = self.cardButtons[info]

        if avId == base.localAvatar.doId:
            self.targetCard = card
            self.localDeck[cardIndex] = None
        else:
            self.otherCard = card
            self.otherReturnPos = card.getPos(aspect2d)

        moveSeq = Sequence(
            LerpPosInterval(card, duration=0.6, pos=target, startPos=card.getPos())
        )
        moveSeq.start()

    def enterWaitingToBegin(self):
        self.cr.mainMenu.unload()
        self.enableLeaveButton()

    def exitWaitingToBegin(self):
        if self.leaveButton:
            self.leaveButton.destroy()
            self.leaveButton = None
        self.clockNode.stop()
        self.clockNode.hide()

    def enterPlaying(self):
        base.playMusic(self.bgm, looping=True)
        self.enableLeaveButton()

    def exitPlaying(self):
        if self.leaveButton:
            self.leaveButton.destroy()
            self.leaveButton = None
        if self.screenText:
            self.screenText.destroy()
            self.screenText = None
        self.clockNode.stop()
        self.clockNode.hide()

    def enterGameOver(self):
        base.cr.mainMenu.load()
        base.localAvatar.askForRequeue()
        base.localAvatar.cleanupGameInterest()

    def exitGameOver(self):
        pass

    def receiveCards(self, cards):
        # only new cards should be passed through this function
        emptySlotIndexes = [i for i, x in enumerate(self.localDeck) if x is None]

        for i, info in enumerate(cards):
            trackId, cardTier = info

            np = CARD_MODELS[cardTier].copyTo(NodePath())
            image = self.trackIcons[trackId].copyTo(np)
            image.setScale(ICON_SCALE[trackId])
            image.setR(-90)
            if trackId == TRACK_ICE:
                image.setPos(0.7, 0, 0.2)

            card = DirectButton(parent=aspect2d, relief=None, geom=np, geom_hpr=UNREVEALED_HPR, geom_scale=0.6,
                                command=self.selectedCard, extraArgs=[info], text=str(cardTier), text_pos=(-.59, 0.62),
                                text_font=FONT, text_scale=0.6, scale=0.15)
            slotIndex = emptySlotIndexes[i]
            card.setPos(CARD_POSITIONS[slotIndex])
            self.localDeck[slotIndex] = info

            self.cardButtons[info] = card

        if self.otherCard:
            self.otherCard.show()

    def setOpponentName(self, name, skillLevel, dnaString):
        # first create our own frame
        # create our own frame, the opponent's frame will be created in a later update
        frame = loader.loadModel('phase_3.5/models/modules/trophy_frame')
        dot = loader.loadModel('phase_6/models/golf/checker_marble')
        self.ourFrame = DirectLabel(parent=base.a2dBottomLeft, relief=None, geom=frame, geom_scale=(0.25, 0.1, 0.25),
                                    text=base.localAvatar.getName(), text_wordwrap=7.504, text_align=TextNode.A_center,
                                    text_font=FONT, text_scale=0.07, text_pos=(0, -0.2), sortOrder=70, pos=(0.24, 0, 0.32))

        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(base.localAvatar.getDNAString())
        ourToon = ToonHead.ToonHead()
        ourToon.setH(180)
        ourToon.setupHead(dna, forGui=1)
        ourToon.reparentTo(self.ourFrame)
        ourToon.startBlink()
        ourToon.setScale(HEAD_SCALES.get(dna.head, 0.11))  # TODO: head scales for species

        print('our head is', dna.head)

        ourSkillLevel = base.localAvatar.getBeltLevel()
        if ourSkillLevel != NONE:
            self.ourDot = DirectLabel(parent=self.ourFrame, relief=None, geom=dot, geom_scale=0.3,
                                      sortOrder=80, geom_color=RANK_COLORS[ourSkillLevel], geom_hpr=(0, 90, 0),
                                      geom_pos=(0.11, 0, 0.17))

        self.opponentFrame = DirectLabel(parent=base.a2dTopRight, relief=None, geom=frame, geom_scale=(0.25, 0.1, 0.25),
                                         text=name, text_wordwrap=7.504, text_align=TextNode.A_center, text_font=FONT,
                                         text_scale=0.07, text_pos=(0, -0.2), sortOrder=70, pos=(-0.31, 0, -0.35))

        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(dnaString)
        opponent = ToonHead.ToonHead()
        opponent.setH(180)
        opponent.setupHead(dna, forGui=1)
        opponent.reparentTo(self.opponentFrame)
        opponent.startBlink()
        opponent.setScale(HEAD_SCALES.get(dna.head, 0.11))  # TODO: head scales for species
        print('opponent head is', dna.head)

        if skillLevel != NONE:
            self.opponentSkillDot = DirectLabel(parent=self.opponentFrame, relief=None, geom=dot, geom_scale=0.3,
                                                sortOrder=80, geom_color=RANK_COLORS[skillLevel], geom_hpr=(0, 90, 0),
                                                geom_pos=(0.11, 0, 0.17))

        dot.removeNode()
        frame.removeNode()

    def forcePick(self):
        card = random.choice(list(self.cardButtons.values()))
        if card:
            card.commandFunc(DGG.B1CLICK)

    def postGenerateMessage(self):
        DistributedNode.postGenerateMessage(self)
        self.sendUpdate('requestBegin')
        self.clockNode.stop()
        self.clockNode.hide()

    def leaveButtonPushed(self):
        self.fsm.request('GameOver')
        self.clockNode.stop()
        self.clockNode.hide()
        self.sendUpdate('requestExit')

    def getTimer(self):
        self.sendUpdate('requestTimer', [])

    def enableLeaveButton(self):
        self.leaveButton = DirectButton(parent=base.a2dTopRight, relief=None, text='Quit', text_fg=(1, 1, 0.65, 1),
                                        text_pos=(0, -.13), text_font=FONT, text_scale=0.5, scale=0.15,
                                        command=self.leaveButtonPushed, image=(self.upButton, self.downButton,
                                                                               self.rolloverButton),
                                        image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), pos=(-0.3, 0, -0.77))

    def setTimer(self, timerEnd):
        currentState = self.fsm.getCurrentState()
        playing = currentState.getName() == 'Playing'
        if currentState is not None and playing:
            self.clockNode.stop()
            time = globalClockDelta.networkToLocalTime(timerEnd)
            timeLeft = int(time - globalClock.getRealTime())
            if timeLeft > 0 and timerEnd != 0:
                if timeLeft > 60:
                    timeLeft = 60
                self.clockNode.setPos(1.16, 0, -0.83)

                self.clockNode.countdown(timeLeft)
                self.clockNode.show()
            else:
                self.clockNode.stop()
                self.clockNode.hide()

    def addCardTier(self, trackId, cardTier):
        np = CARD_MODELS[cardTier].copyTo(NodePath())
        image = self.trackIcons[trackId].copyTo(NodePath('icon'))
        image.setScale(ICON_SCALE[trackId])
        image.reparentTo(np)
        image.setR(-90)
        if trackId == TRACK_ICE:
            image.setPos(0.7, 0, 0.2)

        if self.otherCard and not self.otherCard.isEmpty():
            self.otherCard['geom'] = np
            self.otherCard['geom_hpr'] = UNREVEALED_HPR
            self.otherCard['geom_scale'] = 0.6
            self.otherCard['text'] = str(cardTier)
            self.otherCard['text_pos'] = (-.6, 0.62)
            self.otherCard['text_scale'] = 0.6
            self.otherCard['text_font'] = FONT
            self.otherTrack = trackId

    def resetOtherCard(self):
        if self.otherCard and not self.otherCard.isEmpty():
            self.otherCard.hide()
            self.otherCard.setPos(self.otherReturnPos)
            self.otherReturnPos = None

            geom = self.otherCard['geom']
            icon = geom.find(IMAGE_NODES[self.otherTrack])
            if icon:
                icon.removeNode()

            geom = CARD_MODELS[0].copyTo(NodePath())
            self.otherCard['geom'] = geom
            self.otherCard['geom_hpr'] = UNREVEALED_HPR
            self.otherCard['geom_scale'] = 0.6
            self.otherCard['text'] = ''
            self.otherTrack = 0

        for card in list(self.cardButtons.values()):
            card['state'] = DGG.NORMAL

    def d_resultFinished(self):
        self.sendUpdate('resultFinished')

    def addWinIndicator(self, avId, card):
        if not avId or card is None:
            return

        trackId, cardTier = card

        index = len(self.roundResults[avId][trackId])
        if avId != base.localAvatar.doId:
            index += 5

        image = self.trackIcons[trackId].copyTo(NodePath())
        np = CARD_MODELS[cardTier].copyTo(NodePath())
        image.reparentTo(np)
        image.setScale(ICON_SCALE[trackId])
        image.setR(-90)
        card = DirectButton(parent=aspect2d, relief=None, geom=np, geom_hpr=UNREVEALED_HPR, geom_scale=0.3,
                            state=DGG.DISABLED, command=self.doNothing, scale=(0.2, 1, 0.2))

        pos = WON_CARD_POSITIONS[trackId][index]
        card.setPos(pos)
        self.winIndicators.append(card)

    def roundResult(self, winnerId, playedCards):
        self.clockNode.hide()

        if self.turnPlayed in playedCards:
            playedCards.remove(self.turnPlayed)

        if winnerId == base.localAvatar.doId:
            winningCard = self.turnPlayed
        elif winnerId == 0:
            winningCard = []
        else:
            # we need to create a card in this scenario
            winningCard = playedCards[0]

        name = 'Nobody'
        result = 'has won'
        if winnerId:
            name = 'You'
            if winnerId != base.localAvatar.doId:
                result = 'have lost'
            else:
                result = 'have won'

        if winnerId and winningCard:
            track, tier = winningCard
            results = self.roundResults[winnerId]
            if track not in results:
                self.roundResults[winnerId][track] = [tier]
            else:
                if tier not in results[track]:
                    self.roundResults[winnerId][track].append(tier)

        poofSequence = getDustCloudIval()
        self.revealSequence = Sequence(
            poofSequence,
            Func(self.addCardTier, *playedCards[0]),
            Func(self.textDisplay.displayText, f'{name} {result} this round!'),
            Wait(2.5),
            Func(self.addWinIndicator, winnerId, winningCard),
            Wait(4.5),
            Func(self.resetOtherCard),
            Func(self.targetCard.destroy),
            Func(self.clockNode.show),
            Func(self.d_resultFinished),
        )

        self.revealSequence.start()

        if self.targetCard:
            if self.turnPlayed:
                del self.cardButtons[self.turnPlayed]

            self.targetCard = None
            self.turnPlayed = None

    def doNothing(self):
        pass

    def startGame(self, avIds):
        for avId in avIds:
            self.roundResults[avId] = {}

        # create the dummy cards
        for i in range(0, NUM_CARDS):
            np = CARD_MODELS[0].copyTo(NodePath())
            card = DirectButton(parent=aspect2d, relief=None, geom=np, geom_hpr=UNREVEALED_HPR, geom_scale=0.6,
                                state=DGG.DISABLED, text_pos=(-.6, 0.62), text_scale=0.6, command=self.doNothing,
                                scale=0.15)
            card.setPos(CARD_POSITIONS[NUM_CARDS + i])
            self.dummyDeck[i] = card

        self.fsm.request('Playing')

    def gameOver(self, result, resultId):
        name = 'You'
        if result == PLAYER_WON:
            if resultId != base.localAvatar.doId:
                name = 'Your opponent'

            self.textDisplay.displayText(f'{name} won the game!')
        elif result == PLAYER_QUIT:
            if resultId != base.localAvatar.doId:
                name = 'Your opponent'

            self.textDisplay.displayText(f'{name} quit the game!')

        self.fsm.request('GameOver')
