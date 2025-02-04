import sys
import time
from concurrent.futures import Future
from typing import Optional
from psygnal import Signal
from .threadpool import ProcessPoolExecutor_global, ThreadPoolExecutor_global

class ReturnProcess():
    update_signal = Signal(object)
    finished_signal = Signal()
    def __init__(self,fn:callable=None,callback:Optional[callable]=None, *args, **kwargs):
        self.fn = fn
        self.callback = callback
        self.args = args
        self.kwargs = kwargs.copy()
        self.executor = ProcessPoolExecutor_global
        self.thread = ThreadPoolExecutor_global

    def start(self):
        self.thread.submit(
            self.process
        )
    def process(self):
        self.future = ProcessPoolExecutor_global.submit(
            self.fn,
            *self.args, 
            **self.kwargs
        )
        if self.callback:
            self.future.add_done_callback(self.callback)
        else:
            self.future.add_done_callback(self._callback)
            
    def _callback(self, future: Future):
        # print(future.result())
        self.update_signal.emit(future.result())
        return future.result()

    def close(self):
        self.executor.shutdown(wait=False)
 