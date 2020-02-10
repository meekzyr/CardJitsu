from direct.actor.Actor import Actor
from panda3d.core import NodePath, Texture
from .ToonHead import ToonHead
from .ToonGlobals import *
from . import ToonDNA

LegsAnimDict = {}
TorsoAnimDict = {}
HeadAnimDict = {}


def compileGlobalAnimList():
    phaseList = [
        # phase 3 anims
        (('neutral', 'neutral'), ('run', 'run')),

        # phase 3.5 anims
        (('shrug', 'shrug'), ('wave', 'wave'), ('pushbutton', 'press-button'),
         ('throw', 'pie-throw'), ('jump', 'jump'), ('conked', 'conked')),

        # phase 4 anims
        (('confused', 'confused'), ('applause', 'applause'),
         ('bow', 'bow'), ('curtsy', 'curtsy'), ('bored', 'bored'),
         ('think', 'think')),

        # phase 5 anims
        (('water-gun', 'water-gun'),
         ('hold-bottle', 'hold-bottle'),
         ('firehose', 'firehose'),
         ('spit', 'spit'))
    ]
    phaseStrList = ['phase_3', 'phase_3.5', 'phase_4', 'phase_5']
    for animList in phaseList:
        phaseStr = phaseStrList[phaseList.index(animList)]
        for key in list(LegDict.keys()):
            LegsAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + LegDict[key] + anim[1]
                LegsAnimDict[key][anim[0]] = file

        for key in list(TorsoDict.keys()):
            TorsoAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + TorsoDict[key] + anim[1]
                TorsoAnimDict[key][anim[0]] = file

        for key in list(HeadDict.keys()):
            if key.find('d') >= 0:
                HeadAnimDict.setdefault(key, {})
                for anim in animList:
                    file = phaseStr + HeadDict[key] + anim[1]
                    HeadAnimDict[key][anim[0]] = file


class Toon(ToonHead, Actor):
    notify = directNotify.newCategory('Toon')

    def __init__(self, other=None):
        Actor.__init__(self, None, None, other, flattenable=0, setFinal=1)
        ToonHead.__init__(self)
        self.scale = 1
        self.height = 0.0
        self.style = None

    def setDNAString(self, dnaString):
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(dnaString)
        if len(newDNA.torso) < 2:
            newDNA.torso = newDNA.torso + 's'
        self.setDNA(newDNA)

    def getDNAString(self):
        return self.style

    def setDNA(self, dna):
        if self.style:
            self.updateToonDNA(dna)
        else:
            self.style = dna
            self.generateToon()
            #self.initializeDropShadow()

    def swapToonHead(self, headStyle):
        self.stopLookAroundNow()
        self.eyelids.request('open')
        self.unparentToonParts()
        self.removePart('head', '1000')
        self.removePart('head', '500')
        self.removePart('head', '250')
        self.style.head = headStyle
        self.generateToonHead(self.style, forGui=1)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.eyelids.request('open')
        self.startLookAround()

    def swapToonTorso(self, torsoStyle, genClothes=True):
        self.unparentToonParts()
        self.removePart('torso', '1000')
        self.removePart('torso', '500')
        self.removePart('torso', '250')
        self.style.torso = torsoStyle
        self.generateToonTorso(genClothes)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()

    def swapToonLegs(self, legStyle):
        self.unparentToonParts()
        self.removePart('legs', '1000')
        self.removePart('legs', '500')
        self.removePart('legs', '250')
        self.style.legs = legStyle
        self.generateToonLegs()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()

    def swapToonColor(self, dna):
        #self.style = dna
        self.generateToonColor()

    def __swapToonClothes(self, dna):
        #self.style = dna
        self.generateToonClothes(fromNet=True)

    def updateToonDNA(self, newDNA, fForce=0):
        self.style.gender = newDNA.getGender()
        oldDNA = self.style
        if fForce or newDNA.head != oldDNA.head:
            self.swapToonHead(newDNA.head)
        if fForce or newDNA.torso != oldDNA.torso:
            self.swapToonTorso(newDNA.torso, genClothes=False)
            self.loop('neutral')
        if fForce or newDNA.legs != oldDNA.legs:
            self.swapToonLegs(newDNA.legs)
        self.swapToonColor(newDNA)
        self.__swapToonClothes(newDNA)

    def generateToonLegs(self):
        legStyle = self.style.legs
        filePrefix = LegDict.get(legStyle)
        if filePrefix is None:
            self.notify.error('unknown leg style: %s' % legStyle)
        self.loadModel('phase_3' + filePrefix + '1000', 'legs', '1000', 1)
        self.loadModel('phase_3' + filePrefix + '500', 'legs', '500', 1)
        self.loadModel('phase_3' + filePrefix + '250', 'legs', '250', 1)

        self.loadAnims(LegsAnimDict[legStyle], 'legs', '1000')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '500')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '250')
        self.findAllMatches('**/boots_short').stash()
        self.findAllMatches('**/boots_long').stash()
        self.findAllMatches('**/shoes').stash()

    def _generateToonHead(self):
        headHeight = ToonHead.generateToonHead(self, self.style, ('1000', '500', '250'), forGui=1)
        if self.style.getAnimal() == 'dog':
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '1000')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '500')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '250')

    def generateToonTorso(self, genClothes=True):
        torsoStyle = self.style.torso
        filePrefix = TorsoDict.get(torsoStyle)
        if filePrefix is None:
            self.notify.error('unknown torso style: %s' % torsoStyle)
        self.loadModel('phase_3' + filePrefix + '1000', 'torso', '1000', 1)
        if len(torsoStyle) == 1:
            self.loadModel('phase_3' + filePrefix + '1000', 'torso', '500', 1)
            self.loadModel('phase_3' + filePrefix + '1000', 'torso', '250', 1)
        else:
            self.loadModel('phase_3' + filePrefix + '500', 'torso', '500', 1)
            self.loadModel('phase_3' + filePrefix + '250', 'torso', '250', 1)

        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '1000')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '500')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '250')
        if genClothes and len(torsoStyle) != 1:
            self.generateToonClothes()

    def generateToonClothes(self, fromNet=False):
        swappedTorso = 0
        if self.hasLOD():
            if self.style.getGender() == 'f' and (not fromNet):
                try:
                    bottomPair = ToonDNA.GirlBottoms[self.style.botTex]
                except:
                    bottomPair = ToonDNA.GirlBottoms[0]

                if len(self.style.torso) < 2:
                    return 0
                elif self.style.torso[1] == 's' and bottomPair[1] == ToonDNA.SKIRT:
                    self.swapToonTorso(self.style.torso[0] + 'd', genClothes=0)
                    swappedTorso = 1
                elif self.style.torso[1] == 'd' and bottomPair[1] == ToonDNA.SHORTS:
                    self.swapToonTorso(self.style.torso[0] + 's', genClothes=0)
                    swappedTorso = 1
            try:
                texName = ToonDNA.Shirts[self.style.topTex]
            except:
                texName = ToonDNA.Shirts[0]

            shirtTex = loader.loadTexture(texName, okMissing=True)
            if shirtTex is None:
                shirtTex = loader.loadTexture(ToonDNA.Shirts[0])
            shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            shirtTex.setMagfilter(Texture.FTLinear)
            try:
                shirtColor = ToonDNA.ClothesColors[self.style.topTexColor]
            except:
                shirtColor = ToonDNA.ClothesColors[0]

            try:
                texName = ToonDNA.Sleeves[self.style.sleeveTex]
            except:
                texName = ToonDNA.Sleeves[0]

            sleeveTex = loader.loadTexture(texName, okMissing=True)
            if sleeveTex is None:
                sleeveTex = loader.loadTexture(ToonDNA.Sleeves[0])
            sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sleeveTex.setMagfilter(Texture.FTLinear)
            try:
                sleeveColor = ToonDNA.ClothesColors[self.style.sleeveTexColor]
            except:
                sleeveColor = ToonDNA.ClothesColors[0]

            if self.style.getGender() == 'm':
                try:
                    texName = ToonDNA.BoyShorts[self.style.botTex]
                except:
                    texName = ToonDNA.BoyShorts[0]

            else:
                try:
                    texName = ToonDNA.GirlBottoms[self.style.botTex][0]
                except:
                    texName = ToonDNA.GirlBottoms[0][0]

            bottomTex = loader.loadTexture(texName, okMissing=True)
            if bottomTex is None:
                if self.style.getGender() == 'm':
                    bottomTex = loader.loadTexture(ToonDNA.BoyShorts[0])
                else:
                    bottomTex = loader.loadTexture(ToonDNA.GirlBottoms[0][0])
            bottomTex.setMinfilter(Texture.FTLinearMipmapLinear)
            bottomTex.setMagfilter(Texture.FTLinear)
            try:
                bottomColor = ToonDNA.ClothesColors[self.style.botTexColor]
            except:
                bottomColor = ToonDNA.ClothesColors[0]

            darkBottomColor = bottomColor * 0.5
            darkBottomColor.setW(1.0)
            for lodName in self.getLODNames():
                thisPart = self.getPart('torso', lodName)
                top = thisPart.find('**/torso-top')
                top.setTexture(shirtTex, 1)
                top.setColor(shirtColor)
                sleeves = thisPart.find('**/sleeves')
                sleeves.setTexture(sleeveTex, 1)
                sleeves.setColor(sleeveColor)
                bottoms = thisPart.findAllMatches('**/torso-bot')
                for bottomNum in range(0, bottoms.getNumPaths()):
                    bottom = bottoms.getPath(bottomNum)
                    bottom.setTexture(bottomTex, 1)
                    bottom.setColor(bottomColor)

                caps = thisPart.findAllMatches('**/torso-bot-cap')
                caps.setColor(darkBottomColor)

        return swappedTorso

    def generateToonColor(self):
        ToonHead.generateToonColor(self, self.style)
        armColor = self.style.getArmColor()
        gloveColor = self.style.getGloveColor()
        legColor = self.style.getLegColor()
        for lodName in self.getLODNames():
            torso = self.getPart('torso', lodName)
            if len(self.style.torso) == 1:
                parts = torso.findAllMatches('**/torso*')
                parts.setColor(armColor)
            for pieceName in ('arms', 'neck'):
                piece = torso.find('**/' + pieceName)
                piece.setColor(armColor)

            hands = torso.find('**/hands')
            hands.setColor(gloveColor)
            legs = self.getPart('legs', lodName)
            for pieceName in ('legs', 'feet'):
                piece = legs.find('**/%s;+s' % pieceName)
                piece.setColor(legColor)

    def parentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                if not self.getPart('torso', lodName).find('**/def_head').isEmpty():
                    self.attach('head', 'torso', 'def_head', lodName)
                else:
                    self.attach('head', 'torso', 'joint_head', lodName)

                self.attach('torso', 'legs', 'joint_hips', lodName)
        else:
            self.attach('head', 'torso', 'joint_head')
            self.attach('torso', 'legs', 'joint_hips')

    def unparentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                self.getPart('head', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('torso', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('legs', lodName).reparentTo(self.getLOD(lodName))

        else:
            self.getPart('head').reparentTo(self.getGeomNode())
            self.getPart('torso').reparentTo(self.getGeomNode())
            self.getPart('legs').reparentTo(self.getGeomNode())

    def rescaleToon(self):
        animalStyle = self.style.getAnimal()
        bodyScale = toonBodyScales[animalStyle]
        headScale = toonHeadScales[animalStyle]
        self.setAvatarScale(bodyScale)
        for lod in self.getLODNames():
            self.getPart('head', lod).setScale(headScale)

    def getAvatarScale(self):
        return self.scale

    def setAvatarScale(self, scale):
        if self.scale != scale:
            self.scale = scale
            self.getGeomNode().setScale(scale)
            self.setHeight(self.height)

    def getHeight(self):
        return self.height

    def setHeight(self, height):
        self.height = height

    def resetHeight(self):
        if hasattr(self, 'style') and self.style:
            animal = self.style.getAnimal()
            bodyScale = toonBodyScales[animal]
            headScale = toonHeadScales[animal][2]
            shoulderHeight = legHeightDict[self.style.legs] * bodyScale + \
                             torsoHeightDict[self.style.torso] * bodyScale
            height = shoulderHeight + headHeightDict[self.style.head] * headScale
            self.shoulderHeight = shoulderHeight
            self.setHeight(height)

    def setupToonNodes(self):
        eyes = self.findAllMatches('**/*eyes*')
        for eye in eyes:
            eye.setDepthTest(1)

        rightHand = NodePath('rightHand')
        self.rightHand = None
        self.rightHands = []
        leftHand = NodePath('leftHand')
        self.leftHands = []
        self.leftHand = None
        for lodName in self.getLODNames():
            hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            if not self.getPart('torso', lodName).find('**/def_joint_right_hold').isEmpty():
                hand = self.getPart('torso', lodName).find('**/def_joint_right_hold')

            self.rightHands.append(hand)
            rightHand = rightHand.instanceTo(hand)
            if not self.getPart('torso', lodName).find('**/def_joint_left_hold').isEmpty():
                hand = self.getPart('torso', lodName).find('**/def_joint_left_hold')

            self.leftHands.append(hand)
            leftHand = leftHand.instanceTo(hand)
            if self.rightHand is None:
                self.rightHand = rightHand
            if self.leftHand is None:
                self.leftHand = leftHand

        self.headParts = self.findAllMatches('**/__Actor_head')
        self.legsParts = self.findAllMatches('**/__Actor_legs')
        self.hipsParts = self.legsParts.findAllMatches('**/joint_hips')
        self.torsoParts = self.hipsParts.findAllMatches('**/__Actor_torso')

    def generateToon(self):
        self.setLODNode()
        self.addLOD(1000, 20, 0)
        self.addLOD(500, 80, 20)
        self.addLOD(250, 280, 80)

        self.generateToonLegs()
        self._generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()

        self.loop('neutral')


compileGlobalAnimList()
