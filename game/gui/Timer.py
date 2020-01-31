from pandac.PandaModules import Vec4
from direct.gui.DirectGui import DirectFrame, DGG
from direct.task import Task
from direct.showbase.PythonUtil import bound


class Timer(DirectFrame):
    ClockImage = None
    TimerId = 0

    def __init__(self, font):
        image = self.getImage()
        DirectFrame.__init__(self, state=DGG.DISABLED, relief=None, scale=0.45, image=image, image_pos=(0, 0, 0),
                             text='0', text_fg=(0, 0, 0, 1), text_font=font, text_pos=(-0.01, -0.15), text_scale=0.35)
        self.initialiseoptions(Timer)
        self.timerId = Timer.TimerId
        Timer.TimerId += 1
        self.countdownTask = None
        self.currentTime = 0
        self.taskTime = 0.0
        self.vFontColor = Vec4(0, 0, 0, 1)

    def getImage(self):
        if Timer.ClockImage is None:
            model = loader.loadModel('phase_3.5/models/gui/clock_gui')
            Timer.ClockImage = model.find('**/alarm_clock')
            model.removeNode()
        return Timer.ClockImage

    def setTime(self, time):
        time = bound(time, 0, 999)
        if time == self.currentTime:
            return
        self.currentTime = time
        timeStr = str(time)
        timeStrLen = len(timeStr)
        if timeStrLen == 1:
            if time <= 5:
                self.setTimeStr(timeStr, 0.34, (-0.025, -0.125), Vec4(1, 0, 0, 1))
            else:
                self.setTimeStr(timeStr, 0.34, (-0.025, -0.125))
        elif timeStrLen == 2:
            self.setTimeStr(timeStr, 0.27, (-0.025, -0.1))
        elif timeStrLen == 3:
            self.setTimeStr(timeStr, 0.2, (-0.01, -0.08))

    def setTimeStr(self, timeStr, scale=0.2, pos=(-0.01, -0.08), fg=None):
        self['text'] = ''
        self['text_fg'] = fg or self.vFontColor
        self['text_scale'] = scale
        self['text_pos'] = pos
        self['text'] = timeStr

    def getElapsedTime(self):
        return self.taskTime

    def _timerTask(self, task):
        countdownTime = int(task.duration - task.time)
        self.setTime(countdownTime)
        self.taskTime = task.time
        if task.time >= task.duration:
            self.timerExpired()
            if task.callback:
                task.callback()
            return Task.done
        else:
            return Task.cont

    def countdown(self, duration, callback=None):
        self.countdownTask = Task.Task(self._timerTask)
        self.countdownTask.duration = duration
        self.countdownTask.callback = callback
        taskMgr.remove('timerTask%s' % self.timerId)
        return taskMgr.add(self.countdownTask, 'timerTask%s' % self.timerId)

    def timerExpired(self):
        pass

    def stop(self):
        if self.countdownTask:
            taskMgr.remove(self.countdownTask)

    def reset(self):
        self.stop()
        self.setTime(0)
        taskMgr.remove('timerTask%s' % self.timerId)
        self.taskTime = 0.0

    def destroy(self):
        self.reset()
        self.countdownTask = None
        DirectFrame.destroy(self)

    def cleanup(self):
        self.destroy()
        self.notify.warning('Call destroy, not cleanup')
