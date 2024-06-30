import asyncio
import traceback
from PySide6.QtCore import QThread, Signal, QCoreApplication, Slot

class QtheadAsyncWorker(QThread):
    update_signal = Signal(object)
    finished = Signal()
    error = Signal(str)
    def __init__(self,parent, fn, *args, **kwargs):
        super(QtheadAsyncWorker, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['update_signal'] = self.update_signal
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.started.connect(self.run)
        self.finished.connect(self.stop_thread)
        self.parent().destroyed.connect(self.stop_thread)
    
    def start_thread(self):
        self.start()
    
    def stop_thread(self):
        self.loop.stop()
        self.loop.close()
        self.deleteLater()

    @Slot()
    def run(self):
        try:
            self.loop.create_task(self.fn(*self.args, **self.kwargs))
            self.loop.run_forever()
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()
            self.loop.stop()
            self.loop.close()

class RequestAsyncWorker(QThread):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal(str)
    finished = Signal()
    update_signal = Signal(list)
    def __init__(self,parent, fn, *args, **kwargs):
        super(RequestAsyncWorker, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['update_signal'] = self.update_signal
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.started.connect(self.run)
        self.finished.connect(self.stop_thread)
        self.parent().destroyed.connect(self.stop_thread)
    
    def start_thread(self):
        self.start()
    
    def stop_thread(self):
        self.loop.stop()
        self.loop.close()
        self.deleteLater()

    @Slot()
    def run(self):
        try:
            #self.loop.create_task()
            self.loop.run_until_complete(self.fn(*self.args, **self.kwargs))
            #asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            try:
                self.finished.emit()
            except:
                pass
            # self.loop.stop()
            # self.loop.close()

class SimpleWorker(QThread):
    "Worker này dùng để emit candle data"
    finished = Signal()
    error = Signal()
    def __init__(self,parent, fn, *args, **kwargs):
        super(SimpleWorker, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.started.connect(self.run)
        self.finished.connect(self.stop_thread)
        self.destroyed.connect(self.stop_thread)

    def start_thread(self):
        self.start()
    def stop_thread(self):
        self.deleteLater()
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit()
        finally:
            try:
                self.finished.emit()
            except:
                pass
