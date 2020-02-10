from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectLabel import DirectLabel
from direct.gui import DirectGuiGlobals as DGG

from panda3d.core import TextNode


class TextDisplay(DirectObject):
    DEFAULT_COLOR = (1, 0, 0, 1)

    def __init__(self, font, parent=aspect2d):
        DirectObject.__init__(self)
        self.text = DirectLabel(parent=parent, relief=None, text='', text_align=TextNode.A_center, text_pos=(0, -0.35),
                                text_scale=0.15, text_wordwrap=15, text_fg=self.DEFAULT_COLOR, textMayChange=1,
                                state=DGG.DISABLED, sortOrder=80)
        self.FONT = font

    def destroy(self):
        self.ignoreAll()
        taskMgr.remove('clearDisplayedText')
        if self.text:
            self.text.destroy()
            self.text = None

    def displayText(self, text, color=None, timeout=5):
        if not color:
            color = self.DEFAULT_COLOR

        self.text['text'] = text
        self.text.show()

        self.text['text_font'] = self.FONT
        self.text['text_scale'] = 0.15
        self.text['text_pos'] = (0, -0.35)
        self.text['text_fg'] = color

        taskMgr.doMethodLater(timeout, self.clearText, 'clearDisplayedText')

    def clearText(self, task=None):
        self.text['text'] = ''
        self.text['text_fg'] = self.DEFAULT_COLOR
        self.text.hide()

        if task:
            return task.done
