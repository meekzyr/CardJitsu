from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from game.objects.AuthManagerUD import AuthManagerUD

import pymongo


class UDRepository(AstronInternalRepository):
    notify = directNotify.newCategory('UDRepository')
    notify.setInfo(True)

    def __init__(self, threadedNet=True):
        self.baseChannel = 1000000
        self.GameGlobalsId = 1000
        self.serverId = 4002

        self.mongoCli = pymongo.MongoClient('localhost')
        self.dbCollection = self.mongoCli['jitsu']

        AstronInternalRepository.__init__(self, self.baseChannel, self.serverId,
                                          dcFileNames=['astron/dclass/direct.dc', 'astron/dclass/jitsu.dc'],
                                          dcSuffix='UD', connectMethod=self.CM_NET, threadedNet=threadedNet)

    def handleConnected(self):
        rootObj = DistributedObjectAI(self)
        rootObj.generateWithRequiredAndId(self.GameGlobalsId, 0, 0)
        self.setAI(self.GameGlobalsId, self.baseChannel)

        authManager = AuthManagerUD(self)
        authManager.generateWithRequiredAndId(1001, self.GameGlobalsId, 0)

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF
