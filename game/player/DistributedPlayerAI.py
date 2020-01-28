from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify


class DistributedPlayerAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedPlayerAI')
    interestId = 0

    def readyToPlay(self):
        avId = self.air.getAvatarIdFromSender()
        self.notify.warning('ready to play %s' % avId)

    def postGenerateMessage(self):
        self.notify.warning('postGenerate')
        channel = self.GetPuppetConnectionChannel(self.doId)
        self.air.clientAddInterest(channel, self.interestId, self.air.districtId, 2)
