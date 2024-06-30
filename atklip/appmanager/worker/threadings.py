from threading import Thread
import traceback
import asyncio
from PySide6.QtCore import Signal, QObject, QCoreApplication, Slot,QThread,Qt


class ThreadingAsyncWorker(QObject):
    "Worker này dùng để emit candle data"
    finished = Signal()
    error = Signal(str)
    update_signal = Signal() # dùng để emit toàn bộ candle data khi có nến mới
    lastcandle = Signal(list) # dùng để emit 2 nến cuối cùng
    def __init__(self,parent:None, fn, *args, **kwargs):
        super(ThreadingAsyncWorker, self).__init__(None)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._thread = Thread(target=self.run, daemon=True, args=())
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.finished.connect(self.stop_thread)
        self.destroyed.connect(self.stop_thread)
        #self.parent().destroyed.connect(self.stop_thread)
    
    def start_thread(self):
        self._thread.start()
    
    def stop_thread(self):
        if self.loop != None:
            try:
                self.loop.stop()
                self.loop.close()
            except Exception as e:
                traceback.print_exception(e)
        self.deleteLater()
        
    @Slot()
    def run(self):
        try:
            #asyncio.run(self.fn(*self.args, **self.kwargs))
            self.loop.run_until_complete(self.fn(*self.args, **self.kwargs))
            # self.loop.run_forever()
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class RequestAsyncWorker(QObject):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal(str)
    finished = Signal(bool)
    update_signal = Signal(list)
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,parent, fn, *args, **kwargs):
        super(RequestAsyncWorker, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['update_signal'] = self.update_signal
        self._thread = Thread(target=self.run, daemon=True, args=())
        
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.finished.connect(self.stop_thread)
        self.destroyed.connect(self.stop_thread)
        self.parent().destroyed.connect(self.stop_thread)
    
    def start_thread(self):
        self._thread.start()
    
    def stop_thread(self):
        if self.loop != None:
            try:
                self.loop.stop()
                self.loop.close()
            except Exception as e:
                traceback.print_exception(e)
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
            self.finished.emit(True)
 
class FastStartThread(QObject):
    error = Signal(str)
    finished = Signal()
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,parent, fn, *args, **kwargs):
        super(FastStartThread, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._thread = QThread()
        self._thread.started.connect(self.run, Qt.ConnectionType.AutoConnection)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.finished.connect(self.stop_thread)
        self.destroyed.connect(self.stop_thread)
        self.parent().destroyed.connect(self.stop_thread)
    
    def start_thread(self):
        self._thread.start()
    
    def stop_thread(self):
        if self.loop != None:
            try:
                self.loop.stop()
                self.loop.close()
            except Exception as e:
                pass
        self._thread.deleteLater()
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
            try:
                self.finished.emit()
            except:
                pass

class SimpleWorker(QObject):
    "Worker này dùng để emit candle data"
    finished = Signal()
    error = Signal(str)
    def __init__(self,parent, fn, *args, **kwargs):
        super(SimpleWorker, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._thread = Thread(target=self.run, daemon=True, args=())
        self.finished.connect(self.stop_thread)
        self.destroyed.connect(self.stop_thread)

    def start_thread(self):
        self._thread.start()
    def stop_thread(self):
        self.deleteLater()
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()
