from panda3d.core import loadPrcFile

loadPrcFile("etc/Configrc.prc")

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify
__builtins__.process = 'server'

from .ServerBase import *
from jitsu.base.AIRepository import AIRepository

hostname = simbase.config.GetString('astron-hostname', '127.0.0.1')
port = simbase.config.GetInt('astron-md-port', 7199)

simbase.air = AIRepository(baseChannel=301000000, stateserverId=4002)
simbase.air.connect(hostname, port)

simbase.run()
