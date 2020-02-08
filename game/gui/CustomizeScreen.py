from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from .CustomizeOption import CustomizeOption


from ..jitsu.CardJitsuGlobals import FONT
from ..player import ToonDNA, Toon


name2code = {'pig': 's', 'bear': 'b', 'monkey': 'p', 'duck': 'f', 'rabbit': 'r',
             'mouse': 'm', 'horse': 'h', 'cat': 'c', 'dog': 'd'}
code2name = {'s': 'pig', 'b': 'bear', 'p': 'monkey', 'f': 'duck', 'r': 'rabbit',
             'm': 'mouse', 'h': 'horse', 'c': 'cat', 'd': 'dog'}

GloveOptions = ['White', 'Bright Red', 'Maroon', 'Brown', 'Tan', 'Orange', 'Yellow', 'Lime', 'Sea Green',
                'Green', 'Aqua', 'Blue', 'Royal Blue', 'Purple', 'Lavender', 'Pink', 'Black']


class CustomizeScreen(DirectFrame):
    notify = directNotify.newCategory('CustomizeScreen')

    def __init__(self, callback, **kw):
        self._callback = callback
        geom = loader.loadModel('phase_6/models/gui/ui_frame')
        optiondefs = (
            ('relief', None, None),
            ('geom', geom, None),
            ('geom_scale', 1.5, 1.5),
            ('text', base.localAvatar.getName(), None),
            ('text_align', TextNode.ACenter, None),
            ('text_font', FONT, None),
            ('text_scale', 0.075, None),
            ('text_pos', (0, 0.65), None),
            ('pos', (-0.7, 0, 0.16), None)
        )
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, aspect2d)
        self.initialiseoptions(CustomizeScreen)

        self.genderOptions = None
        self.genderLabel = None
        self.speciesOptions = None
        self.speciesLabel = None
        self.legOptions = None
        self.legLabel = None
        self.torsoOptions = None
        self.torsoLabel = None
        self.headOptions = None
        self.headLabel = None
        self.muzzleOptions = None
        self.muzzleLabel = None
        self.gloveOptions = None
        self.gloveLabel = None
        self.headColorOptions = None
        self.headColorLabel = None
        self.armColorOptions = None
        self.armColorLabel = None
        self.legColorOptions = None
        self.legColorLabel = None
        self.shirtColorOptions = None
        self.shirtColorLabel = None
        self.bottomsColorOptions = None
        self.bottomsColorLabel = None
        self.shirtLabel = None
        self.shirtEntry = None
        self.shortsLabel = None
        self.shortsEntry = None
        self.doneButton = None

        geom.removeNode()
        rotateGeoms = loader.loadModel('phase_6/models/gui/ui_arrow_buttons')
        leftGeom = (rotateGeoms.find('**/*ArrowLeft*Up'), rotateGeoms.find('**/*ArrowLeft*Down'),
                    rotateGeoms.find('**/*ArrowLeft*Rollover'))

        rightGeom = (rotateGeoms.find('**/*ArrowRight*Up'), rotateGeoms.find('**/*ArrowRight*Down'),
                     rotateGeoms.find('**/*ArrowRight*Rollover'))
        self.leftButton = DirectButton(parent=self, relief=None, image=leftGeom, pos=(-0.11, 0, -0.07))
        self.rightButton = DirectButton(parent=self, relief=None, image=rightGeom, pos=(0.11, 0, -0.07))

        self.leftButton.bind(DGG.B1PRESS, self.__rotateToon, [-3])
        self.leftButton.bind(DGG.B1RELEASE, self.__stopRotation)
        self.rightButton.bind(DGG.B1PRESS, self.__rotateToon, [3])
        self.rightButton.bind(DGG.B1RELEASE, self.__stopRotation)
        rotateGeoms.removeNode()

        self.toon = None
        self.dna = None
        self.pitch = self.attachNewNode('pitch')
        self.rotate = self.pitch.attachNewNode('rotate')
        self.scale = self.rotate.attachNewNode('scale')
        self.pitch.setP(0)

        self.makeToon()

    def makeToon(self, dna=None):
        if self.toon:
            self.toon.cleanup()
            self.toon.delete()
            self.toon.removeNode()
            self.toon = None
            self.dna = None

        if not dna:
            dna = base.localAvatar.getDNAString()

        self.toon = Toon.Toon()
        self.dna = ToonDNA.ToonDNA()
        self.dna.makeFromNetString(dna)
        self.toon.setDNA(self.dna)
        self.toon.getGeomNode().setDepthWrite(1)
        self.toon.getGeomNode().setDepthTest(1)
        self.toon.setHpr(180, 0, 0)
        self.toon.setZ(-0.45)

        scaleFactor = 0.2
        if self.dna.legs == 'l':
            scaleFactor = 0.19

        self.toon.setScale(scaleFactor)
        self.toon.reparentTo(self.scale)

    def __rotateToon(self, *args):
        taskMgr.add(self.__rotateTask, 'toonRotateTask', extraArgs=[args[0]], appendTask=True)

    def __rotateTask(self, direction, task):
        if hasattr(self, 'pitch'):
            self.pitch.setH((self.pitch.getH() % 360) + 0.4 * direction)
            return task.cont
        else:
            return task.done

    def __stopRotation(self, *args):
        taskMgr.remove('toonRotateTask')

    def __selectHead(self, *args):
        species = name2code.get(args[0].lower())

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(head=species + self.dna.head[1:])
        self.makeToon(newDNA.makeNetString())

    def __selectLegs(self, *args):
        legs = args[0].lower()
        if legs == 'long':
            legs = 'l'
        elif legs == 'medium':
            legs = 'm'
        else:
            legs = 's'

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())

        newDNA.updateToonProperties(legs=legs)
        self.makeToon(newDNA.makeNetString())

    def __selectGloves(self, *args):
        color = args[0]

        if color == 'White':
            index = len(ToonDNA.NumToColor) + 1
        else:
            index = ToonDNA.NumToColor.index(color)

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(gloveColor=index)
        self.makeToon(newDNA.makeNetString())

    def __selectTorso(self, *args):
        torso = args[0][0].lower()
        if self.dna.gender == 'f':
            torso += 'd'
        else:
            torso += 's'

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(torso=torso)
        self.makeToon(newDNA.makeNetString())

    def __selectHeadSize(self, *args):
        size = args[0][0].lower()
        head = self.dna.head

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(head=head[0] + size + head[2])
        self.makeToon(newDNA.makeNetString())

    def __selectMuzzleSize(self, *args):
        size = args[0][0].lower()
        head = self.dna.head

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(head=head[0] + head[1] + size)
        self.makeToon(newDNA.makeNetString())

    def __selectGender(self, *args):
        gender = args[0].lower()
        if gender == 'boy':
            gender = 'm'
        else:
            gender = 'f'

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        #newDNA.updateToonProperties(gender=gender)
        newDNA.updateToonProperties(gender=gender, bottomTexture=0)
        self.makeToon(newDNA.makeNetString())

    def __choseHeadColor(self, *args):
        color = args[0]

        if color == 'White':
            index = len(ToonDNA.NumToColor) + 1
        else:
            index = ToonDNA.NumToColor.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(headColor=index)
        self.makeToon(newDNA.makeNetString())

    def __choseArmColor(self, *args):
        color = args[0]

        if color == 'White':
            index = len(ToonDNA.NumToColor) + 1
        else:
            index = ToonDNA.NumToColor.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(armColor=index)
        self.makeToon(newDNA.makeNetString())

    def __choseLegColor(self, *args):
        color = args[0]

        if color == 'White':
            index = len(ToonDNA.NumToColor) + 1
        else:
            index = ToonDNA.NumToColor.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(legColor=index)
        self.makeToon(newDNA.makeNetString())

    def __choseShirtColor(self, *args):
        color = args[0]
        index = ToonDNA.ClothesColorNames.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(topTextureColor=index, sleeveTextureColor=index)
        self.makeToon(newDNA.makeNetString())

    def __choseShortsColor(self, *args):
        color = args[0]
        index = ToonDNA.ClothesColorNames.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(bottomTextureColor=index)
        self.makeToon(newDNA.makeNetString())

    def __changeShirt(self, *args):
        index = int(args[0])
        if index not in range(0, len(ToonDNA.Shirts)):
            return

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(topTexture=index)
        self.makeToon(newDNA.makeNetString())

    def __changeShorts(self, *args):
        index = int(args[0])

        bottoms = ToonDNA.BoyShorts if self.dna.gender == 'm' else ToonDNA.GirlBottoms
        if index not in range(0, len(bottoms)):
            return

        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(bottomTexture=index)
        self.makeToon(newDNA.makeNetString())

    def load(self):
        genders = ['Boy', 'Girl']
        gMap = {'m': genders[0], 'f': genders[1]}
        gIndex = gMap.get(self.dna.gender)
        self.genderOptions = CustomizeOption(parent=self, command=self.__selectGender, initialitem=gIndex,
                                             items=genders, pos=(1.15, 0, 0.7))
        self.genderLabel = DirectLabel(parent=self.genderOptions, relief=None, text_font=FONT, text='Gender:',
                                       text_scale=0.85, pos=(-2.59, 0, 0))

        species = ['Bear', 'Cat', 'Dog', 'Duck', 'Horse', 'Monkey', 'Mouse', 'Pig', 'Rabbit']
        sIndex = species.index(code2name.get(self.dna.head[0]).capitalize())
        self.speciesOptions = CustomizeOption(parent=self, command=self.__selectHead, initialitem=sIndex,
                                              items=species, pos=(1.15, 0, 0.55))
        self.speciesLabel = DirectLabel(parent=self.speciesOptions, relief=None, text_font=FONT, text='Species:',
                                        text_scale=0.85, pos=(-2.7, 0, 0))

        headOptions = ['Short', 'Long']
        types = {'s': headOptions[0], 'l': headOptions[1]}
        hIndex = headOptions.index(types.get(self.dna.head[1]))

        self.headOptions = CustomizeOption(parent=self, command=self.__selectHeadSize, initialitem=hIndex,
                                           items=headOptions, pos=(1.15, 0, 0.4))
        self.headLabel = DirectLabel(parent=self.headOptions, relief=None, text_font=FONT, text='Head Size:',
                                     text_scale=0.85, pos=(-3.07, 0, 0))

        mIndex = headOptions.index(types.get(self.dna.head[2]))
        self.muzzleOptions = CustomizeOption(parent=self, command=self.__selectMuzzleSize, initialitem=mIndex,
                                             items=headOptions, pos=(1.15, 0, 0.25))
        self.muzzleLabel = DirectLabel(parent=self.muzzleOptions, relief=None, text_font=FONT, text='Muzzle Size:',
                                       text_scale=0.85, pos=(-3.4, 0, 0))

        legs = ['Small', 'Medium', 'Long']
        legType = {'s': 'Small', 'm': 'Medium', 'l': 'Long'}
        lIndex = legs.index(legType.get(self.dna.legs))

        self.legOptions = CustomizeOption(parent=self, command=self.__selectLegs, initialitem=lIndex, items=legs,
                                          pos=(1.15, 0, 0.1))
        self.legLabel = DirectLabel(parent=self.legOptions, relief=None, text_font=FONT, text='Leg Length:',
                                    text_scale=0.85, pos=(-3.21, 0, 0))

        tIndex = legs.index(legType.get(self.dna.torso[0]))
        self.torsoOptions = CustomizeOption(parent=self, command=self.__selectTorso, initialitem=tIndex, items=legs,
                                            pos=(1.15, 0, -0.05))
        self.torsoLabel = DirectLabel(parent=self.torsoOptions, relief=None, text_font=FONT, text='Torso Length:',
                                      text_scale=0.85, pos=(-3.57, 0, 0))

        gloveColor = self.dna.gloveColor
        length = len(ToonDNA.NumToColor)
        if gloveColor > length:
            gloveColor = 0
        headColor = self.dna.headColor
        if headColor > length:
            headColor = 0
        armColor = self.dna.armColor
        if armColor > length:
            armColor = 0
        legColor = self.dna.legColor
        if legColor > length:
            legColor = 0

        self.gloveOptions = CustomizeOption(parent=self, command=self.__selectGloves,
                                            initialitem=gloveColor, items=ToonDNA.NumToColor,
                                            pos=(1.15, 0, -0.2), image_pos=(1.55, 0, 0.15), text_pos=(-0.13, -.1))
        self.gloveLabel = DirectLabel(parent=self.gloveOptions, relief=None, text_font=FONT, text='Glove Color:',
                                      text_scale=0.85, pos=(-3.35, 0, 0))

        self.headColorOptions = CustomizeOption(parent=self, command=self.__choseHeadColor,
                                                initialitem=headColor, items=ToonDNA.NumToColor,
                                                pos=(1.15, 0, -0.35), image_pos=(1.55, 0, 0.15), text_pos=(-0.13, -.1))
        self.headColorLabel = DirectLabel(parent=self.headColorOptions, relief=None,
                                          text_font=FONT, text='Head Color:',
                                          text_scale=0.85, pos=(-3.27, 0, 0))

        self.armColorOptions = CustomizeOption(parent=self, command=self.__choseArmColor,
                                               initialitem=armColor, items=ToonDNA.NumToColor,
                                               pos=(1.15, 0, -0.5), image_pos=(1.55, 0, 0.15), text_pos=(-0.13, -.1))
        self.armColorLabel = DirectLabel(parent=self.armColorOptions, relief=None,
                                         text_font=FONT, text='Arm Color:',
                                         text_scale=0.85, pos=(-3.074, 0, 0))

        self.legColorOptions = CustomizeOption(parent=self, command=self.__choseLegColor,
                                               initialitem=legColor, items=ToonDNA.NumToColor,
                                               pos=(1.15, 0, -0.65), image_pos=(1.55, 0, 0.15), text_pos=(-0.13, -.1))
        self.legColorLabel = DirectLabel(parent=self.legColorOptions, relief=None,
                                         text_font=FONT, text='Leg Color:',
                                         text_scale=0.85, pos=(-3, 0, 0))

        self.shirtColorOptions = CustomizeOption(parent=self, command=self.__choseShirtColor,
                                                 initialitem=self.dna.topTexColor-1, items=ToonDNA.ClothesColorNames[1:],
                                                 pos=(1.15, 0, -0.8), image_pos=(1.55, 0, 0.15), text_pos=(-0.13, -.1))
        self.shirtColorLabel = DirectLabel(parent=self.shirtColorOptions, relief=None,
                                           text_font=FONT, text='Shirt Color:',
                                           text_scale=0.85, pos=(-3, 0, 0))

        self.bottomsColorOptions = CustomizeOption(parent=self, command=self.__choseShortsColor,
                                                   initialitem=self.dna.botTexColor-1, items=ToonDNA.ClothesColorNames[1:],
                                                   pos=(1.15, 0, -0.95), image_pos=(1.55, 0, 0.15), text_pos=(-0.13, -.1))
        self.bottomsColorLabel = DirectLabel(parent=self.bottomsColorOptions, relief=None,
                                             text_font=FONT, text='Shorts Color:',
                                             text_scale=0.85, pos=(-3, 0, 0))

        self.shirtEntry = DirectEntry(parent=self, relief=DGG.GROOVE, scale=0.08, pos=(1.6, 0, 0.3),
                                      borderWidth=(0.05, 0.05), state=DGG.NORMAL, text_font=FONT,
                                      frameColor=((1, 1, 1, 1), (1, 1, 1, 1), (0.5, 0.5, 0.5, 0.5)),
                                      text_align=TextNode.ALeft, text_scale=0.8, width=3.5, numLines=1, focus=1,
                                      backgroundFocus=0, cursorKeys=1, text_fg=(0, 0, 0, 1), suppressMouse=1,
                                      autoCapitalize=0, command=self.__changeShirt)
        self.shirtEntry.enterText(str(self.dna.topTex))
        self.shirtLabel = DirectLabel(parent=self.shirtEntry, relief=None, text_font=FONT,
                                      text='Shirt:', text_scale=0.85, pos=(1.25, 0, 1.25))

        self.shortsEntry = DirectEntry(parent=self, relief=DGG.GROOVE, scale=0.08, pos=(1.6, 0, 0.0),
                                       borderWidth=(0.05, 0.05), state=DGG.NORMAL, text_font=FONT,
                                       frameColor=((1, 1, 1, 1), (1, 1, 1, 1), (0.5, 0.5, 0.5, 0.5)),
                                       text_align=TextNode.ALeft, text_scale=0.8, width=3.5, numLines=1, focus=1,
                                       backgroundFocus=0, cursorKeys=1, text_fg=(0, 0, 0, 1), suppressMouse=1,
                                       autoCapitalize=0, command=self.__changeShorts)
        self.shortsEntry.enterText(str(self.dna.botTex))
        self.shortsLabel = DirectLabel(parent=self.shortsEntry, relief=None, text_font=FONT,
                                      text='Shorts:', text_scale=0.85, pos=(1.25, 0, 1.25))

        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.doneButton = DirectButton(parent=self, text_font=FONT, text='Done', command=self.__handleDone, scale=0.2,
                                       image=(upButton, downButton, rolloverButton), relief=None,
                                       text_fg=(1, 1, 0.65, 1), pos=(0, 0, -0.94), text_pos=(0, -.23),
                                       image_color=(1, 0, 0, 1), image_scale=(20, 1, 15), sortOrder=DGG.GEOM_SORT_INDEX)
        buttonModels.removeNode()

    def __handleDone(self):
        base.localAvatar.b_setDNAString(self.dna.makeNetString())
        self.unload()

    def unload(self):
        if self.genderLabel:
            self.genderLabel.destroy()
            self.genderLabel = None

        if self.genderOptions:
            self.genderOptions.destroy()
            self.genderOptions = None

        if self.speciesLabel:
            self.speciesLabel.destroy()
            self.speciesLabel = None

        if self.speciesOptions:
            self.speciesOptions.destroy()
            self.speciesOptions = None

        if self.headLabel:
            self.headLabel.destroy()
            self.headLabel = None

        if self.headOptions:
            self.headOptions.destroy()
            self.headOptions = None

        if self.muzzleLabel:
            self.muzzleLabel.destroy()
            self.muzzleLabel = None

        if self.muzzleOptions:
            self.muzzleOptions.destroy()
            self.muzzleOptions = None

        if self.torsoLabel:
            self.torsoLabel.destroy()
            self.torsoLabel = None

        if self.torsoOptions:
            self.torsoOptions.destroy()
            self.torsoOptions = None

        if self.legLabel:
            self.legLabel.destroy()
            self.legLabel = None

        if self.legOptions:
            self.legOptions.destroy()
            self.legOptions = None

        if self.gloveLabel:
            self.gloveLabel.destroy()
            self.gloveLabel = None

        if self.gloveOptions:
            self.gloveOptions.destroy()
            self.gloveOptions = None

        if self.headColorOptions:
            self.headColorOptions.destroy()
            self.headColorOptions = None

        if self.headColorLabel:
            self.headColorLabel.destroy()
            self.headColorLabel = None

        if self.armColorOptions:
            self.armColorOptions.destroy()
            self.armColorOptions = None

        if self.armColorLabel:
            self.armColorLabel.destroy()
            self.armColorLabel = None

        if self.legColorOptions:
            self.legColorOptions.destroy()
            self.legColorOptions = None

        if self.legColorLabel:
            self.legColorLabel.destroy()
            self.legColorLabel = None

        if self.shirtColorLabel:
            self.shirtColorLabel.destroy()
            self.shirtColorLabel = None

        if self.shirtColorOptions:
            self.shirtColorOptions.destroy()
            self.shirtColorOptions = None

        if self.bottomsColorLabel:
            self.bottomsColorLabel.destroy()
            self.bottomsColorLabel = None

        if self.bottomsColorOptions:
            self.bottomsColorOptions.destroy()
            self.bottomsColorOptions = None

        if self.shirtLabel:
            self.shirtLabel.destroy()
            self.shirtLabel = None

        if self.shirtEntry:
            self.shirtEntry.destroy()
            self.shirtEntry = None

        if self.shortsLabel:
            self.shortsLabel.destroy()
            self.shortsLabel = None

        if self.shortsEntry:
            self.shortsEntry.destroy()
            self.shortsEntry = None

        if self.doneButton:
            self.doneButton.destroy()
            self.doneButton = None

        if self.toon:
            self.toon.cleanup()
            self.toon.delete()
            self.toon.removeNode()
            self.toon = None
            self.dna = None

        self._callback(self)
