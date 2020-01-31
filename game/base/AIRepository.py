from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.TimeManagerAI import TimeManagerAI
from pandac.PandaModules import *
import sys
from game.objects.DistributedDistrictAI import DistributedDistrictAI
from game.jitsu.DistributedCardJitsuAI import DistributedCardJitsuAI
from game.jitsu.JitsuMatchmakerAI import JitsuMatchmakerAI


class AIRepository(AstronInternalRepository):

    def __init__(self, baseChannel, serverId, threadedNet=True):
        self.GameGlobalsId = 1000
        AstronInternalRepository.__init__(self, baseChannel, serverId,
                                          dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                          dcSuffix='AI', connectMethod=self.CM_NET, threadedNet=threadedNet)

        # Allow some time for other processes.
        base.setSleep(0.01)

        self.games = []

        self.district = None
        self.districtId = self.allocateChannel()
        self.timeManager = None
        self.matchmaker = None
        self.game = None

        self.zoneAllocator = UniqueIdAllocator(3, 1048576)

        tcpPort = base.config.GetInt('ai-base-port', 7199)
        hostname = base.config.GetString('ai-base-host', '127.0.0.1')
        self.acceptOnce('airConnected', self.connectSuccess)
        self.connect(hostname, tcpPort)

    def getAvatarExitEvent(self, doId):
        return 'distObjDelete-%s' % doId

    def connectSuccess(self):
        print('Connected successfully!', self.districtId)

        self.district = DistributedDistrictAI(self)
        self.district.generateWithRequiredAndId(self.districtId, self.GameGlobalsId, 3)
        self.district.setAI(self.ourChannel)

        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)

        self.matchmaker = JitsuMatchmakerAI(self)
        self.matchmaker.startMatchmake()

    def lostConnection(self):
        # This should be overridden by a derived class to handle an
        # unexpectedly lost connection to the gameserver.
        self.notify.warning("Lost connection to gameserver.")
        sys.exit()

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF

    def getAccountIdFromSender(self):
        return (self.getMsgSender() >> 32) & 0xFFFFFFFF
