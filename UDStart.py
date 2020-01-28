from panda3d.core import *

loadPrcFile("config/Config.prc")

loadPrcFileData('', 'window-type none\naudio-library-name null')
from direct.showbase import ShowBase
from ToonUDRepository import ToonUDRepository
base = ShowBase.ShowBase()
base.air = ToonUDRepository(threadedNet = True)
base.run()
