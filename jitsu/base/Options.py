import json
import os

from panda3d.core import loadPrcFileData


class Options:
    notify = directNotify.newCategory('Options')
    preferences_path = 'etc/options.json'

    def __init__(self):
        self._preferences = {}
        self.__defaults = {'want-sfx': True, 'want-music': True, 'show-player-names': True, 'show-player-ranks': True}
        self.read()

    def __setitem__(self, key, value):
        self._preferences[key] = value

        self.write()

    def reload(self):
        for pref_key, pref_val in self._preferences.items():
            if pref_val is True:
                pref_val = '#t'
            else:
                pref_val = '#f'
            loadPrcFileData(f'Settings: {pref_key}', f'{pref_key} {pref_val}')

    def __getitem__(self, item):
        return self._preferences[item]

    def read(self):
        if not os.path.exists(self.preferences_path):
            self.notify.debug('Preferences file not found, creating..')
            self.write()
        else:
            self.notify.debug('Preference file found, loading..')
            with open(self.preferences_path, 'r') as options:
                self._preferences = json.load(options)
            if not self._preferences:
                self.notify.debug('Preferences were empty, generating new file..')
                self.write()
            else:
                for pref_key, pref_val in self._preferences.items():
                    if pref_key not in self.__defaults:
                        continue

                    if pref_val is True:
                        pref_val = '#t'
                    else:
                        pref_val = '#f'

                    loadPrcFileData(f'Settings: {pref_key}', f'{pref_key} {pref_val}')

    def write(self):
        self.notify.debug('Writing preference file..')
        if self._preferences:
            saving = self._preferences
        else:
            saving = self.__defaults

        with open(self.preferences_path, 'w') as options:
            json.dump(saving, options, sort_keys=True, indent=2)
