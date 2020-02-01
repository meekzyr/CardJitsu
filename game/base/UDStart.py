from panda3d.core import loadPrcFile

loadPrcFile("config/Config.prc")

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify
__builtins__.process = 'server'

from .ServerBase import *
from game.base.UDRepository import UDRepository

hostname = simbase.config.GetString('astron-hostname', '127.0.0.1')
port = simbase.config.GetInt('astron-md-port', 7199)

simbase.air = UDRepository()
simbase.air.connect(hostname, port)

simbase.run()
