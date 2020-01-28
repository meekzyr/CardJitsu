from direct.distributed.DistributedObjectAI import DistributedObjectAI
from game.player import DistributedPlayerAI
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *


class DistributedToonManagerAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def requestAvatar(self):
        return
        clientId = self.air.getAvatarIdFromSender()

        player = DistributedPlayerAI.DistributedPlayerAI(self.air)
        player.generateOtpObject(self.air.districtId, 2000)
        print("CREATED TOON %d" % player.doId)
        self.air.setOwner(player.doId, clientId)

        self.air.clientAddSessionObject(clientId, player.doId)

        dg = PyDatagram()
        dg.addServerHeader(clientId, self.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(self.GetPuppetConnectionChannel(player.doId))
        self.air.send(dg)
