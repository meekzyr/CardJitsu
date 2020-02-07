from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode
from ..jitsu.CardJitsuGlobals import FONT


class CustomizeOption(DirectOptionMenu):

    def __init__(self, parent, **kw):
        optiondefs = (
            #('relief', None, None),
            ('popupMarker_relief', None, None),
            ('scale', 0.07, None),
            ('highlightColor', (0.65, 0.65, 0.65, 1), None),
            ('text_font', FONT, None)
        )
        self.defineoptions(kw, optiondefs)
        DirectOptionMenu.__init__(self, parent=parent)
        self.initialiseoptions(CustomizeOption)

    def setItems(self):
        if self.popupMenu is not None:
            self.destroycomponent('popupMenu')
        self.popupMenu = self.createcomponent('popupMenu', (), None, DirectFrame, (self,), relief='raised',)
        self.popupMenu.setBin('gui-popup', 0)
        if not self['items']:
            return

        itemIndex = 0
        self.minX = self.maxX = self.minZ = self.maxZ = None
        for item in self['items']:
            c = self.createcomponent('item%d' % itemIndex, (), 'item', DirectButton, (self.popupMenu,),
                                     text_font=FONT, text=item, text_align=TextNode.ALeft, text_pos=(0.1, 0),
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
