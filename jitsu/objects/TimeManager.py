from direct.showbase.DirectObject import *
from panda3d.core import *
from direct.task import Task
from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import globalClockDelta


class TimeManager(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory("TimeManager")
    updateFreq = ConfigVariableDouble('time-manager-freq', 1800).getValue()
    minWait = ConfigVariableDouble('time-manager-min-wait', 10).getValue()
    maxUncertainty = ConfigVariableDouble('time-manager-max-uncertainty', 1).getValue()
    maxAttempts = ConfigVariableInt('time-manager-max-attempts', 5).getValue()
    extraSkew = ConfigVariableInt('time-manager-extra-skew', 0).getValue()
    if extraSkew != 0:
        notify.debug("Simulating clock skew of %0.3f s" % extraSkew)
    reportFrameRateInterval = ConfigVariableDouble('report-frame-rate-interval', 300.0).getValue()

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

        self.thisContext = -1
        self.nextContext = 0
        self.attemptCount = 0
        self.start = 0
        self.lastAttempt = -self.minWait * 2

    def generate(self):
        DistributedObject.generate(self)
        self.accept('clock_error', self.handleClockError)

        if self.updateFreq > 0:
            self.startTask()

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.cr.timeManager = self
        self.synchronize("TimeManager.announceGenerate")

    def disable(self):
        self.ignore('clock_error')
        self.stopTask()
        taskMgr.remove('frameRateMonitor')
        if self.cr.timeManager is self:
            self.cr.timeManager = None
        DistributedObject.disable(self)

    def delete(self):
        DistributedObject.delete(self)

    def startTask(self):
        self.stopTask()
        taskMgr.doMethodLater(self.updateFreq, self.doUpdate, "timeMgrTask")

    def stopTask(self):
        taskMgr.remove("timeMgrTask")

    def doUpdate(self, task):
        self.synchronize("timer")
        taskMgr.doMethodLater(self.updateFreq, self.doUpdate, "timeMgrTask")
        return Task.done

    def handleClockError(self):
        self.synchronize("clock error")

    def synchronize(self, description):
        now = globalClock.getRealTime()

        if now - self.lastAttempt < self.minWait:
            self.notify.debug("Not resyncing (too soon): %s" % description)
            return 0

        self.thisContext = self.nextContext
        self.attemptCount = 0
        self.nextContext = (self.nextContext + 1) & 255
        self.notify.debug("Clock sync: %s" % description)
        self.start = now
        self.lastAttempt = now
        self.sendUpdate("requestServerTime", [self.thisContext])
        return 1

    def serverTime(self, context, timestamp):
        end = globalClock.getRealTime()

        if context != self.thisContext:
            self.notify.debug("Ignoring TimeManager response for old context %d" % context)
            return

        elapsed = end - self.start
        self.attemptCount += 1
        self.notify.debug("Clock sync roundtrip took %0.3f ms" % (elapsed * 1000.0))

        average = (self.start + end) / 2.0 - self.extraSkew
        uncertainty = (end - self.start) / 2.0 + abs(self.extraSkew)

        globalClockDelta.resynchronize(average, timestamp, uncertainty)

        self.notify.debug("Local clock uncertainty +/- %.3f s" % (globalClockDelta.getUncertainty()))

        if globalClockDelta.getUncertainty() > self.maxUncertainty:
            if self.attemptCount < self.maxAttempts:
                self.notify.debug("Uncertainty is too high, trying again.")
                self.start = globalClock.getRealTime()
                self.sendUpdate("requestServerTime", [self.thisContext])
                return
            self.notify.debug("Giving up on uncertainty requirement.")

        messenger.send("gotTimeSync", taskChain='default')
        messenger.send(self.cr.uniqueName("gotTimeSync"), taskChain='default')
