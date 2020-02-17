from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui import DirectGuiGlobals as DGG
from ..jitsu.CardJitsuGlobals import FONT


class OptionsPage(DirectFrame):
    notify = directNotify.newCategory('OptionsPage')

    def __init__(self, **kw):
        fade = loader.loadModel('phase_13/models/gui/fade')
        dialog_box = loader.loadModel('phase_3/models/gui/dialog_box_gui')
        optiondefs = (
            ('relief', None, None),
            ('image', fade, None),
            ('image_scale', (5, 2, 2), None),
            ('image_color', (0, 0, 0, 0.3), None),
            ('text', 'Options', None),
            ('text_font', FONT, None),
            ('text_scale', 0.08, None),
            ('text_pos', (0, 0.4), None),
            ('state', DGG.NORMAL, None),
            ('geom', dialog_box, None),
            ('sortOrder', 20, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, aspect2d)
        self.initialiseoptions(OptionsPage)
        self._optionButtons = []
        self.saveButton = None
        fade.removeNode()
        dialog_box.removeNode()

    def toggleMusic(self, enabled):
        options['want-music'] = bool(enabled)

    def toggleSFX(self, enabled):
        options['want-sfx'] = bool(enabled)

    def toggleRankView(self, enabled):
        options['show-player-ranks'] = bool(enabled)

    def togglePlayerNames(self, enabled):
        options['show-player-names'] = bool(enabled)

    def load(self):
        cmdMap = {'Toggle Music': [2.65, self.toggleMusic, options['want-music']],
                  'Toggle Sound Effects': [1.27, self.toggleSFX, options['want-sfx']],
                  'Toggle Rank Visibility': [1.27, self.toggleRankView, options['show-player-ranks']],
                  'Toggle Player Names': [1.3, self.togglePlayerNames, options['show-player-names']]}
        startZ = 0.25
        for bText, bOptions in cmdMap.items():
            border, callback, configVal = bOptions
            checkbox = DirectCheckButton(parent=self, relief=None, text=bText, text_font=FONT, command=callback,
                                         text_scale=0.8, boxPlacement='right', boxBorder=border, scale=0.1,
                                         pos=(-0.1, 0, startZ), indicatorValue=configVal)
            startZ -= 0.17
            self._optionButtons.append(checkbox)

        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**//InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.saveButton = DirectButton(parent=self, text_font=FONT, text='Save', text_pos=(0, -.17), scale=0.2,
                                       text_scale=0.68, command=self.unload,
                                       image=(upButton, downButton, rolloverButton), relief=None,
                                       text_fg=(0, 0, 0, 1), pos=(0, 0, -0.39), image_color=(1, 0.94, 0, 1),
                                       image_scale=(17, 1, 7), sortOrder=DGG.GEOM_SORT_INDEX)
        buttonModels.removeNode()

    def unload(self):
        if base.cr.mainMenu:
            base.cr.mainMenu.configReload()

        options.reload()
        for checkbox in self._optionButtons:
            checkbox.destroy()

        self._optionButtons = []

        if self.saveButton:
            self.saveButton.destroy()
            self.saveButton = None

        self.destroy()
