from panda3d.core import *

loadPrcFile("config/Config.prc")

loadPrcFileData('', 'window-type none\naudio-library-name null')
from direct.showbase import ShowBase
from ToonAIRepository import ToonAIRepository

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify


base = ShowBase.ShowBase()
base.air = ToonAIRepository(101000000, 4002, threadedNet=True)
base.run()
