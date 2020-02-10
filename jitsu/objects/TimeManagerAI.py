from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI


class TimeManagerAI(DistributedObjectAI):
    notify = directNotify.newCategory("TimeManagerAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def requestServerTime(self, context):
        timestamp = globalClockDelta.getRealNetworkTime(bits=32)
        requesterId = self.air.getAvatarIdFromSender()
        print("requestServerTime from %s" % requesterId)
        self.sendUpdateToAvatarId(requesterId, "serverTime", [context, timestamp])
