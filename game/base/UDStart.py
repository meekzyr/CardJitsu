from panda3d.core import *

loadPrcFile("config/Config.prc")

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify
__builtins__.process = 'server'

loadPrcFileData('', 'window-type none\naudio-library-name null')
from direct.showbase import ShowBase
from game.base.UDRepository import UDRepository

base = ShowBase.ShowBase()
base.air = UDRepository(threadedNet=True)
base.run()
