from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal


class DustCloud(NodePath):
    dustCloudCount = 0
    notify = DirectNotifyGlobal.directNotify.newCategory('DustCloud')

    def __init__(self, parent=hidden, wantSound=0):
        NodePath.__init__(self)
        model = loader.loadModel('phase_3.5/models/props/dust_cloud')
        self.assign(model)
        model.removeNode()
        self.reparentTo(parent)
        self.seqNode = self.find('**/+SequenceNode').node()
        self.seqNode.setFrameRate(0)
        self.wantSound = wantSound
        self.poofSound = loader.loadSfx('audio/sfx/poof.ogg')
        self.track = None
        self.trackId = DustCloud.dustCloudCount
        DustCloud.dustCloudCount += 1
        self.setBin('gui-popup', 100, 1)
        self.hide()

    def playSound(self):
        if self.wantSound:
            self.poofSound.play()

    def createTrack(self, rate=24):
        tflipDuration = self.seqNode.getNumChildren() / float(rate)
        self.track = Sequence(Func(self.show), Func(self.messaging),
                              Func(self.seqNode.play, 0, self.seqNode.getNumFrames() - 1),
                              Func(self.seqNode.setFrameRate, rate), Func(self.playSound),
                              Wait(tflipDuration), Func(self._resetTrack), name='dustCloud-track-%d' % self.trackId)

    def _resetTrack(self):
        self.seqNode.setFrameRate(0)
        self.hide()

    def messaging(self):
        self.notify.debug('CREATING TRACK ID: %s' % self.trackId)

    def isPlaying(self):
        if self.track and self.track.isPlaying():
            return True
        return False

    def play(self, rate=24):
        self.stop()
        self.createTrack(rate)
        self.track.start()

    def loop(self, rate=24):
        self.stop()
        self.createTrack(rate)
        self.track.loop()

    def stop(self):
        if self.track:
            self.track.finish()
            self.track.clearToInitial()

    def destroy(self):
        self.notify.debug('DESTROYING TRACK ID: %s' % self.trackId)
        if self.track:
            self._resetTrack()
            self.track.clearToInitial()
        del self.track
        del self.seqNode
        self.removeNode()
