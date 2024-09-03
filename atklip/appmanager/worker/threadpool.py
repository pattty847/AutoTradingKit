from PySide6.QtCore import QThreadPool
import multiprocessing
# global QThreadPool_global
QThreadPool_global = QThreadPool.globalInstance()
num_threads = multiprocessing.cpu_count()
# cpu_count = QThreadPool_global.maxThreadCount()
# print(num_threads,cpu_count)
QThreadPool_global.setMaxThreadCount(num_threads)
