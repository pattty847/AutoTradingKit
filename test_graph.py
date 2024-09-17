import asyncio
import sys
import random
import time
from PySide6.QtCore import QProcess, QRunnable, QThreadPool,Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit



import ccxt.pro as exchange_pro
# import ccxt.async_support as exchange
import ccxt as exchange

from atklip.appmanager.worker.threadings import FastStartThread

class RandomNumberTask(QRunnable):
    """Task to print random numbers"""
    def __init__(self,_ccxt_client,emit_signal) -> None:
        super().__init__()
        self._ccxt_client = _ccxt_client
        self.emit_signal=emit_signal
    def run(self):
        _ohlcv = self._ccxt_client.fetch_ohlcv("BTC/USDT","1m",limit=2)
        self.emit_signal.emit(f"from client____{str(_ohlcv[-1])}")
        print(_ohlcv)
    

class MainWindow(QMainWindow):
    emit_signal = Signal(str)
    def __init__(self):
        super().__init__()

        self.initUI()

        # Initialize QThreadPool
        self.thread_pool = QThreadPool()

    def initUI(self):
        self.setWindowTitle("QProcess and QThreadPool Example")
        
        # Layout and widgets
        layout = QVBoxLayout()

        self.worker = None

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.run_process_button = QPushButton("Run QProcess")
        self.run_process_button.clicked.connect(self.run_process)
        layout.addWidget(self.run_process_button)

        self.run_threadpool_button = QPushButton("Run QThreadPool Task")
        self.run_threadpool_button.clicked.connect(self.run_threadpool_task)
        layout.addWidget(self.run_threadpool_button)

        self.is_runing = False
        self.emit_signal.connect(self.handle_stdout)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self._ccxt_client = exchange.binanceusdm()
        self._ccxt_pro = exchange_pro.binanceusdm()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_process(self):
        self.is_runing = False
        if isinstance(self.worker, FastStartThread):
            self.worker.stop_thread()
        self.worker = None
        self.worker = FastStartThread("crypto_ex",self.loop_watch_ohlcv,self._ccxt_pro,"BTC/USDT","1m")
        self.worker.start_thread()

        
    async def function(self):
        #while True:
        # event_loop = self._ccxt_client.get_event_loop()

        if sys.version_info >= (3, 7):
            event_loop = asyncio.get_running_loop()
        else:
            event_loop = asyncio.get_event_loop()

        _ohlcv = self._ccxt_client.fetch_ohlcv("BTC/USDT","1m",limit=2)
        self.emit_signal.emit(f"from client____{str(_ohlcv[-1])}")
        print(_ohlcv)

    async def loop_watch_ohlcv(self,exchange,symbol,interval):
        firt_run = False
        self.is_runing = True
        _ohlcv = []
        while self.is_runing:
            if exchange != None:
                if "watchOHLCV" in list(exchange.has.keys()):
                    if _ohlcv == []:
                        _ohlcv = self._ccxt_client.fetch_ohlcv(symbol,interval,limit=2)
                        # _ohlcv[-1] = ohlcv[-1]
                    else:
                        ohlcv = await exchange.watch_ohlcv(symbol,interval,limit=2)
                        if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                            _ohlcv[-1] = ohlcv[-1]
                        else:
                            _ohlcv.append(ohlcv[-1])
                            _ohlcv = _ohlcv[-2:]
                            #_ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)    
                elif "fetchOHLCV" in list(exchange.has.keys()):
                    _ohlcv = self._ccxt_client.fetch_ohlcv(symbol,interval,limit=2)
                else:
                    await asyncio.sleep(0.3)
                    continue
          
                self.emit_signal.emit(f"from pro____{str(_ohlcv[-1])}")

            else:
                break
            try:
                await asyncio.sleep(0.3)
            except:
                pass
        try:
            await exchange.close()
        except Exception as e:
            pass
        print("turn-off")

    def handle_stdout(self,output):
        self.text_edit.append(output)

    def run_threadpool_task(self):
        self.worker_ = None
        self.worker_ = FastStartThread("crypto_ex",self.function)
        self.worker_.start_thread()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
