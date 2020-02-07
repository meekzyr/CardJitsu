from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
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
            ('pos', (-0.5, 0, 0.16), None)
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
        newDNA.updateToonProperties(gender=gender)
        self.makeToon(newDNA.makeNetString())

    def __choseHeadColor(self, *args):
        color = args[0]

        index = ToonDNA.NumToColor.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(headColor=index)
        self.makeToon(newDNA.makeNetString())

    def __choseArmColor(self, *args):
        color = args[0]

        index = ToonDNA.NumToColor.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(armColor=index)
        self.makeToon(newDNA.makeNetString())

    def __choseLegColor(self, *args):
        color = args[0]

        index = ToonDNA.NumToColor.index(color)
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(self.dna.makeNetString())
        newDNA.updateToonProperties(legColor=index)
        self.makeToon(newDNA.makeNetString())

    def load(self):
        genders = ['Boy', 'Girl']
        gMap = {'m': genders[0], 'f': genders[1]}
        gIndex = gMap.get(self.dna.gender)
        self.genderOptions = CustomizeOption(parent=self, command=self.__selectGender, initialitem=gIndex,
                                             items=genders, pos=(1.15, 0, 0.55))
        self.genderLabel = DirectLabel(parent=self.genderOptions, relief=None, text_font=FONT, text='Gender:',
                                       text_scale=0.85, pos=(-1.76, 0, 0))

        species = ['Bear', 'Cat', 'Dog', 'Duck', 'Horse', 'Monkey', 'Mouse', 'Pig', 'Rabbit']
        sIndex = species.index(code2name.get(self.dna.head[0]).capitalize())
        self.speciesOptions = CustomizeOption(parent=self, command=self.__selectHead, initialitem=sIndex,
                                              items=species, pos=(1.15, 0, 0.4))
        self.speciesLabel = DirectLabel(parent=self.speciesOptions, relief=None, text_font=FONT, text='Species:',
                                        text_scale=0.85, pos=(-1.76, 0, 0))

        headOptions = ['Short', 'Long']
        types = {'s': headOptions[0], 'l': headOptions[1]}
        hIndex = headOptions.index(types.get(self.dna.head[1]))

        self.headOptions = CustomizeOption(parent=self, command=self.__selectHeadSize, initialitem=hIndex,
                                           items=headOptions, pos=(1.15, 0, 0.25))
        self.headLabel = DirectLabel(parent=self.headOptions, relief=None, text_font=FONT, text='Head Size:',
                                     text_scale=0.85, pos=(-2.14, 0, 0))

        mIndex = headOptions.index(types.get(self.dna.head[2]))
        self.muzzleOptions = CustomizeOption(parent=self, command=self.__selectMuzzleSize, initialitem=mIndex,
                                             items=headOptions, pos=(1.15, 0, 0.1))
        self.muzzleLabel = DirectLabel(parent=self.muzzleOptions, relief=None, text_font=FONT, text='Muzzle Size:',
                                       text_scale=0.85, pos=(-2.5, 0, 0))

        legs = ['Small', 'Medium', 'Long']
        legType = {'s': 'Small', 'm': 'Medium', 'l': 'Long'}
        lIndex = legs.index(legType.get(self.dna.legs))

        self.legOptions = CustomizeOption(parent=self, command=self.__selectLegs, initialitem=lIndex, items=legs,
                                          pos=(1.15, 0, -0.05))
        self.legLabel = DirectLabel(parent=self.legOptions, relief=None, text_font=FONT, text='Leg Length:',
                                    text_scale=0.85, pos=(-2.35, 0, 0))

        tIndex = legs.index(legType.get(self.dna.torso[0]))
        self.torsoOptions = CustomizeOption(parent=self, command=self.__selectTorso, initialitem=tIndex, items=legs,
                                            pos=(1.15, 0, -0.2))
        self.torsoLabel = DirectLabel(parent=self.torsoOptions, relief=None, text_font=FONT, text='Torso Length:',
                                      text_scale=0.85, pos=(-2.69, 0, 0))

        self.gloveOptions = CustomizeOption(parent=self, command=self.__selectGloves,
                                            initialitem=self.dna.gloveColor - 1, items=ToonDNA.NumToColor[1:],
                                            pos=(1.15, 0, -0.35))
        self.gloveLabel = DirectLabel(parent=self.gloveOptions, relief=None, text_font=FONT, text='Glove Color:',
                                      text_scale=0.85, pos=(-2.54, 0, 0))

        self.headColorOptions = CustomizeOption(parent=self, command=self.__choseHeadColor,
                                                initialitem=self.dna.headColor - 1, items=ToonDNA.NumToColor[1:],
                                                pos=(1.15, 0, -0.5))
        self.headColorLabel = DirectLabel(parent=self.headColorOptions, relief=None,
                                          text_font=FONT, text='Head Color:',
                                          text_scale=0.85, pos=(-2.54, 0, 0))

        self.armColorOptions = CustomizeOption(parent=self, command=self.__choseArmColor,
                                               initialitem=self.dna.armColor - 1, items=ToonDNA.NumToColor[1:],
                                               pos=(1.15, 0, -0.65))
        self.armColorLabel = DirectLabel(parent=self.armColorOptions, relief=None,
                                         text_font=FONT, text='Arm Color:',
                                         text_scale=0.85, pos=(-2.54, 0, 0))

        self.legColorOptions = CustomizeOption(parent=self, command=self.__choseLegColor,
                                               initialitem=self.dna.legColor - 1, items=ToonDNA.NumToColor[1:],
                                               pos=(1.15, 0, -0.8))
        self.legColorLabel = DirectLabel(parent=self.legColorOptions, relief=None,
                                         text_font=FONT, text='Leg Color:',
                                         text_scale=0.85, pos=(-2.54, 0, 0))

        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.doneButton = DirectButton(parent=self, text_font=FONT, text='Done', command=self.__handleDone, scale=0.2,
                                       image=(upButton, downButton, rolloverButton), relief=None,
                                       text_fg=(1, 1, 0.65, 1), pos=(0, 0, -0.94), text_pos=(0, -.23),
                                       image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), sortOrder=DGG.GEOM_SORT_INDEX)
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
