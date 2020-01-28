from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.TimeManagerAI import TimeManagerAI
from pandac.PandaModules import *
import sys
from game.objects import DistributedToonManagerAI


class ToonAIRepository(AstronInternalRepository):
    def __init__(self, baseChannel, serverId, threadedNet=True):
        dcFileNames = ['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc']

        self.GameGlobalsId = 1000

        AstronInternalRepository.__init__(self, baseChannel, serverId, dcFileNames=dcFileNames,
                                          dcSuffix='AI', connectMethod=self.CM_NET,
                                          threadedNet=threadedNet)

        # Allow some time for other processes.
        #base.setSleep(0.01)

        self.games = []
        self.zoneTable = {}
        self.hoodArray = []
        self.hoods = []

        self.managerId = self.allocateChannel()
        self.toonMgrID = self.allocateChannel()

        self.zoneAllocator = UniqueIdAllocator(3, 1000000)

        tcpPort = base.config.GetInt('ai-server-port', 7199)
        hostname = base.config.GetString('ai-server-host', '127.0.0.1')
        self.acceptOnce('airConnected', self.connectSuccess)
        self.connect(hostname, tcpPort)

    def connectSuccess(self):
        """ Successfully connected to the Message Director.
            Now to generate the TimeManagerAI """
        print('Connected successfully!')

        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequiredAndId(self.managerId, self.GameGlobalsId, 1)
        self.timeManager.setAI(self.ourChannel)
        self.districtId = self.timeManager.doId
        print("GENERATING TOON MANAGER", self.districtId)
        self.toonManager = DistributedToonManagerAI.DistributedToonManagerAI(self)
        self.toonManager.generateWithRequiredAndId(self.toonMgrID, self.GameGlobalsId, 1)
        self.toonManager.setAI(self.ourChannel)

    def lostConnection(self):
        # This should be overridden by a derived class to handle an
        # unexpectedly lost connection to the gameserver.
        self.notify.warning("Lost connection to gameserver.")
        sys.exit()

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF

    def getAccountIdFromSender(self):
        return (self.getMsgSender() >> 32) & 0xFFFFFFFF

    def createObject(self, fields):
        self.dbInterface.createObject(4003,
                                      self.dclassesByName['DistributedPlayerAI'],
                                      fields)
