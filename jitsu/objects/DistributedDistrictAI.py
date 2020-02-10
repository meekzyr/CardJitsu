from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DistributedDistrictAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.population = 0

    def setPopulation(self, population):
        self.population = population

    def d_setPopulation(self, population):
        self.sendUpdate('setPopulation', [population])

    def b_setPopulation(self, population):
        self.setPopulation(population)
        self.d_setPopulation(population)

    def getPopulation(self):
        return self.population

    def playerOnline(self):
        self.b_setPopulation(self.population + 1)

    def playerOffline(self):
        self.b_setPopulation(self.population - 1)

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
