from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject
import traceback
import sys


class ThreadSignals(QObject):
    # send error status to log
    error = pyqtSignal(str)
    # update log
    log = pyqtSignal(str)
    # update progression
    progress = pyqtSignal()
    # process finished
    finish = pyqtSignal()


class Thread(QRunnable):
    # inherited from QRunnable,

    def __init__(self, func, *args, **kwargs):
        super(Thread, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()

        self.kwargs['signal_progress'] = self.signals.progress
        self.kwargs['signal_log'] = self.signals.log
        self.kwargs['signal_error'] = self.signals.error

    @pyqtSlot()
    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except:     # handle all the exceptions in the running
            error_type, value = sys.exc_info()[:2]
            self.signals.error.emit("{} has occurred, error value:{}\nError detail:\n{}".format(error_type,
                                                                                                value,
                                                                                                traceback.format_exc()))
        finally:
            self.signals.finish.emit()
