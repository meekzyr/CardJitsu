from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DistributedDistrictAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
