from direct.gui.DirectGui import *
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from ..jitsu.CardJitsuGlobals import *
from ..player.Toon import Toon
from ..player.ToonDNA import ToonDNA
from ..gui.CustomizeScreen import CustomizeScreen


class MainMenu(NodePath):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        NodePath.__init__(self, 'MainMenu')
        self.reparentTo(aspect2d)

        self.userName = ''
        self.password = ''
        self.beltProgress = None
        self.ourRank = None
        self.nextRank = None
        self.progressFrame = None
        self.nextLabel = None
        self.currLabel = None
        self.toonFrame = None
        self.nameLabel = None
        self.pitch = None
        self.scale = None
        self.rotate = None
        self.toon = None
        self.leftButton = None
        self.rightButton = None
        self.buttons = []
        self.logo = OnscreenImage(parent=base.a2dTopCenter, image='maps/logo.png', scale=0.4,
                                  pos=(0.79, 0, -0.3))
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

    def readyToQueue(self):
        for button in self.buttons:
            button.destroy()

        self.buttons = []
        base.localAvatar.d_sendReady()

    def returnToMenu(self, uiObj):
        if uiObj:
            uiObj.destroy()

        self.load()

    def customizePlayer(self):
        self.unload()

        c = CustomizeScreen(callback=self.returnToMenu)
        c.load()

    def enterOptions(self):
        pass  # TODO

    def _createProgressBar(self):
        if self.beltProgress:
            self.beltProgress.destroy()

        if self.ourRank:
            self.ourRank.destroy()

        if self.nextRank:
            self.nextRank.destroy()

        dot = loader.loadModel('phase_6/models/golf/checker_marble')
        ourSkillLevel = base.localAvatar.getBeltLevel()

        if not self.progressFrame:
            geom = loader.loadModel('phase_3/models/gui/tt_m_gui_ups_panelBg')
            self.progressFrame = DirectFrame(parent=base.a2dBottomLeft, relief=None, geom=geom, text='Progress:',
                                             text_font=FONT, text_pos=(0.75, 0.05), text_scale=0.1,
                                             geom_scale=(1.6, 1, 0.3), geom_pos=(0.75, 0, 0),
                                             frameSize=(0, 1.5, -0.15, 0.15), pos=(0.1, 0, 0.2))
            geom.removeNode()

        if not self.nextLabel:
            self.nextLabel = DirectLabel(parent=self.progressFrame, relief=None, text='Next Belt:', text_scale=0.05,
                                         text_font=FONT, pos=(1.32, 0, 0.03))

        if not self.currLabel:
            self.currLabel = DirectLabel(parent=self.progressFrame, relief=None, text='Current Belt:', text_scale=0.05,
                                         text_font=FONT, pos=(0.21, 0, 0.03))

        self.beltProgress = DirectWaitBar(parent=self.progressFrame, relief=DGG.SUNKEN,
                                          frameSize=(-0.5, 1.5, -0.15, 0.15),
                                          borderWidth=(0.02, 0.02), scale=0.42, pos=(0.57, 0, -0.05),
                                          range=WIN_REQUIREMENTS.get(ourSkillLevel + 1, 0),
                                          value=base.localAvatar.winCount,
                                          barColor=(0, 0.7, 0, 1))

        currColor = RANK_COLORS.get(ourSkillLevel, None)
        if currColor:
            self.ourRank = DirectLabel(parent=self.beltProgress, relief=None, geom=dot, geom_scale=1,
                                       sortOrder=DGG.GEOM_SORT_INDEX, geom_color=currColor, geom_hpr=(0, 90, 0),
                                       geom_pos=(-0.85, 0, 0))

        nextColor = RANK_COLORS.get(ourSkillLevel + 1, None)
        if nextColor:
            self.nextRank = DirectLabel(parent=self.beltProgress, relief=None, geom=dot, geom_scale=1,
                                        sortOrder=DGG.GEOM_SORT_INDEX, geom_color=nextColor, geom_hpr=(0, 90, 0),
                                        geom_pos=(1.8, 0, 0))

        dot.removeNode()

    def load(self):
        if self.logo.isStashed():
            self.logo.unstash()

        self._createProgressBar()

        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')

        cmdMap = {'Queue': self.readyToQueue,
                  'Customize': self.customizePlayer,
                  'Options': self.enterOptions,
                  'Quit': base.cr.exit}

        startZ = -0.85
        for bText, bCmd in cmdMap.items():
            button = DirectButton(parent=base.a2dTopCenter, relief=None, text=bText, text_fg=(1, 1, 0.65, 1),
                                  text_font=FONT, text_pos=(0, -.23), text_scale=0.6, pos=(0.8, 0, startZ),
                                  scale=0.15, image=(upButton, downButton, rolloverButton), command=bCmd,
                                  image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), sortOrder=DGG.GEOM_SORT_INDEX)

            startZ -= 0.3
            self.buttons.append(button)

        if not self.toonFrame:
            geom = loader.loadModel('phase_6/models/gui/ui_frame')
            self.toonFrame = DirectFrame(parent=self, relief=None, geom=geom, geom_scale=1.5, pos=(-0.5, 0, 0.16),
                                         text=base.localAvatar.getName(), text_font=FONT, text_scale=0.075,
                                         text_pos=(0, 0.65), text_align=TextNode.ACenter)

            rotateGeoms = loader.loadModel('phase_6/models/gui/ui_arrow_buttons')
            leftGeom = (rotateGeoms.find('**/*ArrowLeft*Up'), rotateGeoms.find('**/*ArrowLeft*Down'),
                        rotateGeoms.find('**/*ArrowLeft*Rollover'))

            rightGeom = (rotateGeoms.find('**/*ArrowRight*Up'), rotateGeoms.find('**/*ArrowRight*Down'),
                         rotateGeoms.find('**/*ArrowRight*Rollover'))
            self.leftButton = DirectButton(parent=self, relief=None, image=leftGeom, pos=(-0.53, 0, 0.1))
            self.rightButton = DirectButton(parent=self, relief=None, image=rightGeom, pos=(-0.5, 0, 0.1))

            self.leftButton.bind(DGG.B1PRESS, self.__rotateToon, [-3])
            self.leftButton.bind(DGG.B1RELEASE, self.__stopRotation)
            self.rightButton.bind(DGG.B1PRESS, self.__rotateToon, [3])
            self.rightButton.bind(DGG.B1RELEASE, self.__stopRotation)

            geom.removeNode()

            self.toon = Toon()
            dna = ToonDNA()
            dna.makeFromNetString(base.localAvatar.getDNAString())
            self.toon.setDNA(dna)

            self.toon.getGeomNode().setDepthWrite(1)
            self.toon.getGeomNode().setDepthTest(1)
            self.toon.setHpr(180, 0, 0)
            self.toon.setZ(-0.45)
            self.pitch = self.toonFrame.attachNewNode('pitch')
            self.rotate = self.pitch.attachNewNode('rotate')
            self.scale = self.rotate.attachNewNode('scale')
            self.pitch.setP(0)

            scaleFactor = 0.2
            if dna.legs == 'l':
                scaleFactor = 0.19

            self.toon.setScale(scaleFactor)
            self.toon.reparentTo(self.scale)

        buttonModels.removeNode()

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

    def unload(self):
        self.notify.debug('unload')

        if self.beltProgress:
            self.beltProgress.destroy()
            self.beltProgress = None

        if self.ourRank:
            self.ourRank.destroy()
            self.ourRank = None

        if self.nextRank:
            self.nextRank.destroy()
            self.nextRank = None

        if self.currLabel:
            self.currLabel.destroy()
            self.currLabel = None

        if self.nextLabel:
            self.nextLabel.destroy()
            self.nextLabel = None

        if self.progressFrame:
            self.progressFrame.destroy()
            self.progressFrame = None

        if self.leftButton:
            self.leftButton.destroy()
            self.leftButton = None

        if self.rightButton:
            self.rightButton.destroy()
            self.rightButton = None

        if self.toon:
            self.toon.cleanup()
            self.toon.delete()
            self.toon.removeNode()
            self.toon = None

        if self.pitch:
            self.pitch.removeNode()
            self.pitch = None

        if self.rotate:
            self.rotate.removeNode()
            self.rotate = None

        if self.scale:
            self.scale.removeNode()
            self.scale = None

        if self.toonFrame:
            self.toonFrame.destroy()
            self.toonFrame = None

        for button in self.buttons:
            button.destroy()

        if self.logo:
            self.logo.stash()

        self.buttons = []
