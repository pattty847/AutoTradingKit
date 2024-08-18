import asyncio,os
from PySide6.QtCore import QThreadPool

# global QThreadPool_global
QThreadPool_global = QThreadPool.globalInstance()
cpu_count = QThreadPool_global.maxThreadCount()
QThreadPool_global.setMaxThreadCount(cpu_count/2)
