from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from game.objects.AuthManagerUD import AuthManagerUD


class UDRepository(AstronInternalRepository):

    def __init__(self, threadedNet=True):
        self.baseChannel = 100000000
        self.GameGlobalsId = 1000
        self.serverId = 4002

        AstronInternalRepository.__init__(self, self.baseChannel, self.serverId,
                                          dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                          dcSuffix='UD', connectMethod=self.CM_NET, threadedNet=threadedNet)

        tcpPort = base.config.GetInt('ai-base-port', 7199)
        hostname = base.config.GetString('ai-base-host', '127.0.0.1')
        self.acceptOnce('airConnected', self.connectSuccess)
        self.connect(hostname, tcpPort)

    def connectSuccess(self):
        rootObj = DistributedObjectGlobalUD(self)
        rootObj.generateWithRequiredAndId(self.GameGlobalsId, 0, 0)
        self.setAI(self.GameGlobalsId, self.baseChannel)

        authManager = AuthManagerUD(self)
        authManager.generateWithRequiredAndId(1001, self.GameGlobalsId, 0)
        print('Connected successfully!')

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF
