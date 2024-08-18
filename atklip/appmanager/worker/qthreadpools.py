import asyncio,os
from asyncio import run
import sys
import traceback
from typing import Callable
from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QThreadPool

from .threadpool import QThreadPool_sub,QThreadPool_view


class WorkerSignals(QObject):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal()
    finished = Signal()
    update_signal = Signal(list)
    sig_object = Signal(object)
    sig_process_value = Signal(float)

class ProcessWorker(QRunnable):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self, fn, *args, **kwargs):
        super(ProcessWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals() 
        self.kwargs['sig_process_value'] = self.signals.sig_process_value
        self.kwargs['finished'] = self.signals.finished

        self.is_interrupted = False
        self.setAutoDelete(True)
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.signals.error.emit()
        finally:
            self.signals.finished.emit()  # Done

class FastWorker(QRunnable):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,threadpool:str|QThreadPool="view",fn:Callable=None, *args, **kwargs):
        super(FastWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs #.copy()
        self.signals = WorkerSignals() 
        if threadpool == "view":
            self.threadpool = QThreadPool_view
        elif threadpool == "sub":
            self.threadpool = QThreadPool_sub
        else:
            self.threadpool = threadpool
        self.kwargs['setdata'] = self.signals.setdata
        self.setAutoDelete(True)
    
    def start(self,prio:int=0):
        self.threadpool.start(self,prio)
    
    # def stop_worker(self):
    #     self.signals.deleteLater()

    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            # self.signals.error.emit()
        finally:
            # self.signals.finished.emit()
            self.signals.deleteLater()
            
class FastStartSignal(QObject):
    error = Signal()
    finished = Signal()

class SimpleWorker(QRunnable):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,parent,fn, *args, **kwargs):
        super(SimpleWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = FastStartSignal() 
        self.qtheadpool = QThreadPool(parent)
        self.signals.finished.connect(self.stop_thread)
        self.signals.error.connect(self.stop_thread)
        parent.destroyed.connect(self.stop_thread)
        self.setAutoDelete(True)
    def start_thread(self):
        self.qtheadpool.start(self)
    
    def stop_thread(self):
        try:
            self.qtheadpool.deleteLater()
        except Exception as e:
            self.qtheadpool = None
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.signals.error.emit()
        finally:
            try:
                self.signals.finished.emit()
            except:
                pass

class ThreadingAsyncWorker(QRunnable):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn, *args, **kwargs):
        super(ThreadingAsyncWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = FastStartSignal() 
        self.qtheadpool = QThreadPool()
        self.signals.finished.connect(self.stop_thread)
        self.signals.error.connect(self.stop_thread)
        self.setAutoDelete(True)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start_thread(self):
        self.qtheadpool.start(self)
    
    def stop_thread(self):
        if self.loop != None:
            try:
                self.loop.stop()
                self.loop.close()
            except Exception as e:
                self.loop = None
            try:
                self.qtheadpool.deleteLater()
            except Exception as e:
                self.qtheadpool = None
    @Slot()
    def run(self):
        try:
            self.loop.run_until_complete(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            traceback.print_exception(e)
            self.signals.error.emit()
        finally:
            try:
                self.signals.finished.emit()
            except:
                pass


class RequestAsyncWorker(QRunnable):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn, *args, **kwargs):
        super(RequestAsyncWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.qtheadpool = QThreadPool()
        self.signals = WorkerSignals() 
        self.kwargs['update_signal'] = self.signals.update_signal
        self.signals.finished.connect(self.stop_thread)
        self.signals.error.connect(self.stop_thread)
        self.setAutoDelete(True)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start_thread(self):
        self.qtheadpool.start(self)
    
    def stop_thread(self):
        if self.loop != None:
            try:
                self.loop.stop()
                self.loop.close()
            except Exception as e:
                self.loop = None
            try:
                self.qtheadpool.deleteLater()
            except Exception as e:
                self.qtheadpool = None
    @Slot()
    def run(self):
        try:
            self.loop.run_until_complete(self.fn(*self.args, **self.kwargs))
            #self.loop.run_forever()
        except Exception as e:
            traceback.print_exception(e)
            self.signals.error.emit()
        finally:
            try:
                self.signals.finished.emit()
            except:
                pass
