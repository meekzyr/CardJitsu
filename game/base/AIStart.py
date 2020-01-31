from panda3d.core import *

loadPrcFile("config/Config.prc")

loadPrcFileData('', 'window-type none\naudio-library-name null')
from direct.showbase import ShowBase

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify
__builtins__.process = 'server'

from game.base.AIRepository import AIRepository

base = ShowBase.ShowBase()
base.air = AIRepository(101000000, 4002, threadedNet=True)
base.run()
