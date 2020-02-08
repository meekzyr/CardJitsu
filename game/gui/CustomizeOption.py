from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from panda3d.core import VBase3
from ..jitsu.CardJitsuGlobals import FONT
from ..player.ToonDNA import NumToColor, ClothesColorNames


class CustomizeOption(DirectOptionMenu):

    def __init__(self, parent, **kw):
        self._parent = parent
        buttonModels = loader.loadModel('phase_3/models/gui/quit_button')
        self.upButton = buttonModels.find('**/QuitBtn_UP')
        self.downButton = buttonModels.find('**/QuitBtn_DN')
        self.rolloverButton = buttonModels.find('**/QuitBtn_RLVR')
        buttonModels.removeNode()

        self.image_scale = kw.get('bimg_scale', (9, 1, 15))
        self.btext_scale = kw.get('btext_scale', 0.75)
        self.btext_pos = kw.get('btext_pos', (0.65, -0.05))
        self.button_scale = kw.get('button_scale', 1)
        self.button_pos = kw.get('button_pos', (0.8, 0, 0.0))

        for key in ['btext_scale', 'btext_pos', 'button_scale', 'button_pos', 'bimg_scale']:
            if key in kw:
                del kw[key]

        geom_pos = kw.get('image_pos', (1.5, 0, 0.15))
        text_pos = kw.get('text_pos', (0.34, -.1))
        optiondefs = (
            ('relief', None, None),
            ('popupMarker_relief', None, None),
            ('scale', 0.07, None),
            ('highlightColor', (0.65, 0.65, 0.65, 1), None),
            ('highlightScale', (self.btext_scale + 0.07,)*2, None),
            ('text_font', FONT, None),
            ('text_pos', text_pos, None),
            ('text_scale', self.btext_scale, None),
            ('geom', (self.upButton, self.downButton, self.rolloverButton), None),
            ('geom_scale', self.image_scale, None),
            ('geom_pos', geom_pos, None)
        )
        self.defineoptions(kw, optiondefs)
        DirectOptionMenu.__init__(self, parent=parent)
        self.initialiseoptions(CustomizeOption)

    def showPopupMenu(self, event=None):
        self.popupMenu.show()
        self.popupMenu.setScale(self, VBase3(1))
        b = self.getBounds()
        fb = self.popupMenu.getBounds()

        xPos = (b[1] - b[0])/2.0 - fb[0]
        self.popupMenu.setX(self, xPos)

        items = self['items']
        if len(items) in (len(NumToColor), len(ClothesColorNames)- 1):
            self.popupMenu.setZ(self._parent, 0.8)
        else:
            self.popupMenu.setZ(self, self.minZ + (self.selectedIndex + 1) * self.maxHeight)

        pos = self.popupMenu.getPos(render2d)
        scale = self.popupMenu.getScale(render2d)
        maxX = pos[0] + fb[1] * scale[0]
        if maxX > 1.0:
            self.popupMenu.setX(render2d, pos[0] + (1.0 - maxX))

        minZ = pos[2] + fb[2] * scale[2]
        maxZ = pos[2] + fb[3] * scale[2]
        if minZ < -1.0:
            self.popupMenu.setZ(render2d, pos[2] + (-1.0 - minZ))
        elif maxZ > 1.0:
            self.popupMenu.setZ(render2d, pos[2] + (1.0 - maxZ))

        self.cancelFrame.show()
        self.cancelFrame.setPos(render2d, 0, 0, 0)
        self.cancelFrame.setScale(render2d, 1, 1, 1)

    def setItems(self):
        if self.popupMenu is not None:
            self.destroycomponent('popupMenu')
        self.popupMenu = self.createcomponent('popupMenu', (), None, DirectFrame, (self,), relief=None,)
        self.popupMenu.setBin('gui-popup', 0)
        if not self['items']:
            return

        itemIndex = 0
        self.minX = self.maxX = self.minZ = self.maxZ = None
        self.maxX = 3.79
        self.minX = -1 * self.maxX
        colors = len(self['items']) in (len(NumToColor), len(ClothesColorNames) - 1)
        if colors:
            self['highlightScale'] = (0.5, 0.5, 0.6, 0.5)

        for item in self['items']:
            if colors:
                scale = 0.5
                geom_scale = (9, 1, 10)
            else:
                scale = self.btext_scale
                geom_scale = self.image_scale

            c = self.createcomponent('item%d' % itemIndex, (), 'item', DirectButton, (self.popupMenu,), relief=None,
                                     text_font=FONT, text=item, text_pos=self.btext_pos,
                                     geom=(self.upButton, self.downButton, self.rolloverButton), scale=self.button_scale,
                                     geom_scale=geom_scale, geom_pos=self.button_pos, text_scale=scale,
                                     command=lambda i=itemIndex: self.set(i))
            bounds = c.getBounds()
            if self.minX is None:
                self.minX = bounds[0]
            elif bounds[0] < self.minX:
                self.minX = bounds[0]

            if self.maxX is None:
                self.maxX = bounds[1]
            elif bounds[1] > self.maxX:
                self.maxX = bounds[1]

            if self.minZ is None:
                self.minZ = bounds[2]
            elif bounds[2] < self.minZ:
                self.minZ = bounds[2]

            if self.maxZ is None:
                self.maxZ = bounds[3]
            elif bounds[3] > self.maxZ:
                self.maxZ = bounds[3]
            itemIndex += 1

        if colors:
            self.maxZ = 0.47
        self.maxWidth = self.maxX - self.minX
        self.maxHeight = self.maxZ - self.minZ

        for i in range(itemIndex):
            item = self.component('item%d' % i)
            item['frameSize'] = (self.minX, self.maxX, self.minZ, self.maxZ)
            item.setPos(-self.minX, 0, -self.maxZ - i * self.maxHeight)
            item.bind(DGG.B1RELEASE, self.hidePopupMenu)
            item.bind(DGG.WITHIN, lambda x, i=i, item=item: self._highlightItem(item, i))
            fc = item['frameColor']
            item.bind(DGG.WITHOUT, lambda x, item=item, fc=fc: self._unhighlightItem(item, fc))

        f = self.component('popupMenu')
        f['frameSize'] = (0, self.maxWidth, -self.maxHeight * itemIndex, 0)

        if self['initialitem']:
            self.set(self['initialitem'], fCommand=0)
        else:
            self.set(0, fCommand=0)

        pm = self.popupMarker
        pmw = (pm.getWidth() * pm.getScale()[0] + 2 * self['popupMarkerBorder'][0])
        if self.initFrameSize:
            bounds = list(self.initFrameSize)
        else:
            bounds = [self.minX, self.maxX, self.minZ, self.maxZ]
        if self.initPopupMarkerPos:
            pmPos = list(self.initPopupMarkerPos)
        else:
            pmPos = [bounds[1] + pmw / 2.0, 0, bounds[2] + (bounds[3] - bounds[2]) / 2.0]

        pm.setPos(pmPos[0], pmPos[1], pmPos[2])

        bounds[1] += pmw
        self['frameSize'] = (bounds[0], bounds[1], bounds[2], bounds[3])
        self.hidePopupMenu()
