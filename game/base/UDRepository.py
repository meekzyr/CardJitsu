from direct.distributed.AstronInternalRepository import AstronInternalRepository
from game.objects.RootObjectUD import RootObjectUD
from game.objects.AuthManagerUD import AuthManagerUD


class UDRepository(AstronInternalRepository):

    def __init__(self, threadedNet=True):
        self.baseChannel = 100000000
        self.GameGlobalsId = 1000
        self.serverId = 4002

        AstronInternalRepository.__init__(self, self.baseChannel, self.serverId,
                                          dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                          dcSuffix='UD', connectMethod=self.CM_NET, threadedNet=threadedNet)

        # Allow some time for other processes.
        base.setSleep(0.01)

        tcpPort = base.config.GetInt('ai-base-port', 7199)
        hostname = base.config.GetString('ai-base-host', '127.0.0.1')
        self.acceptOnce('airConnected', self.connectSuccess)
        self.connect(hostname, tcpPort)

    def connectSuccess(self):
        """ Successfully connected to the Message Director.
            Now to generate the AuthManagerAI """
        rootObj = RootObjectUD(self)
        rootObj.generateWithRequiredAndId(self.GameGlobalsId, 0, 0)
        self.setAI(self.GameGlobalsId, self.baseChannel)

        authManager = AuthManagerUD(self)
        authManager.generateWithRequiredAndId(1001, self.GameGlobalsId, 0)
        #self.authManager = self.generateGlobalObject(1001, 'AuthManager')

        print('Connected successfully!')

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF