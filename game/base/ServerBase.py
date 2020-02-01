from direct.interval.IntervalManager import ivalMgr
from direct.showbase import DConfig
from direct.showbase.MessengerGlobal import *
from direct.distributed.ClockDelta import *
from direct.task.TaskManagerGlobal import *
from direct.task import Task

from panda3d.core import GraphicsEngine, TrueClock, VirtualFileSystem


class ServerBase:

    def __init__(self):
        self.config = DConfig
        self.graphicsEngine = GraphicsEngine()
        globalClock = ClockObject.getGlobalClock()
        self.trueClock = TrueClock.getGlobalPtr()
        globalClock.setRealTime(self.trueClock.getShortTime())
        globalClock.setAverageFrameRateInterval(30.0)
        globalClock.tick()
        __builtins__['globalClock'] = globalClock
        taskMgr.globalClock = globalClock
        self.vfs = VirtualFileSystem.getGlobalPtr()
        __builtins__['vfs'] = self.vfs

    def __ivalLoop(self, state):
        ivalMgr.step()
        return Task.cont

    def __igLoop(self, state):
        self.graphicsEngine.renderFrame()
        return Task.cont

    def run(self):
        taskMgr.add(self.__ivalLoop, 'ivalLoop', priority=20)
        taskMgr.add(self.__igLoop, 'igLoop', priority=50)
        taskMgr.run()


__builtins__['taskMgr'] = taskMgr
__builtins__['simbase'] = ServerBase()
__builtins__['messenger'] = messenger


