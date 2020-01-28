from direct.distributed.DistributedNodeUD import DistributedNodeUD


class DistributedPlayerUD(DistributedNodeUD):

    def postGenerateMessage(self):
        print('ud post gen')
        DistributedNodeUD.postGenerateMessage(self)
