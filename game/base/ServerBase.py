from direct.interval.IntervalManager import ivalMgr
from direct.showbase import DConfig
from direct.showbase.MessengerGlobal import *
from direct.task.TaskManagerGlobal import *
from direct.task import Task

from panda3d.core import VirtualFileSystem


class ServerBase:

    def __init__(self):
        self.config = DConfig

    def __ivalLoop(self, state):
        ivalMgr.step()
        return Task.cont

    def run(self):
        taskMgr.add(self.__ivalLoop, 'ivalLoop', priority=20)
        taskMgr.run()


__builtins__['taskMgr'] = taskMgr
__builtins__['vfs'] = VirtualFileSystem.getGlobalPtr()
__builtins__['simbase'] = ServerBase()
__builtins__['messenger'] = messenger


