from PySide6.QtCore import QThreadPool
import multiprocessing
num_threads = multiprocessing.cpu_count()
# global QThreadPool_global
QThreadPool_global = QThreadPool.globalInstance()
cpu_count = QThreadPool_global.maxThreadCount()

print(num_threads,cpu_count)
QThreadPool_global.setMaxThreadCount(num_threads)
