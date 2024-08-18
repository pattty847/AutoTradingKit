import asyncio,os
from PySide6.QtCore import QThreadPool

# global QThreadPool_global
QThreadPool_view = QThreadPool()
cpu_count = QThreadPool_view.maxThreadCount()
QThreadPool_view.setMaxThreadCount(int(cpu_count)-1)

QThreadPool_sub = QThreadPool()
QThreadPool_sub.setMaxThreadCount(int(cpu_count)-1)
