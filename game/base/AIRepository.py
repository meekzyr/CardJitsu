from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.TimeManagerAI import TimeManagerAI
from pandac.PandaModules import *
import sys
from game.objects.DistributedDistrictAI import DistributedDistrictAI
from game.jitsu.JitsuMatchmakerAI import JitsuMatchmakerAI


class AIRepository(AstronInternalRepository):
    notify = directNotify.newCategory('AIRepository')
    notify.setInfo(True)

    def __init__(self, baseChannel, stateserverId):
        self.GameGlobalsId = 1000
        AstronInternalRepository.__init__(self, baseChannel, stateserverId,
                                          dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                          dcSuffix='AI', connectMethod=self.CM_NET, threadedNet=True)

        self.games = []

        self.district = None
        self.districtId = self.allocateChannel()
        self.timeManager = None
        self.matchmaker = None
        self.game = None

        self.zoneAllocator = UniqueIdAllocator(3, 1048576)
        self.acceptOnce('airConnected', self.connectSuccess)

    def getAvatarExitEvent(self, doId):
        return 'distObjDelete-%s' % doId

    def connectSuccess(self):
        self.district = DistributedDistrictAI(self)
        self.district.generateWithRequiredAndId(self.districtId, self.GameGlobalsId, 3)
        self.district.setAI(self.ourChannel)

        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)

        self.matchmaker = JitsuMatchmakerAI(self)
        self.matchmaker.startMatchmaking()

    def lostConnection(self):
        # This should be overridden by a derived class to handle an
        # unexpectedly lost connection to the gameserver.
        self.notify.warning("Lost connection to gameserver.")
        sys.exit()

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF

    def getAccountIdFromSender(self):
        return (self.getMsgSender() >> 32) & 0xFFFFFFFF
