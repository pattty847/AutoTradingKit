# ruff: noqa: D100, D101, D102, D103, D104, D107
from __future__ import annotations
import asyncio
import threading
from typing import Coroutine
import inspect


def ensure_async(func):
    if inspect.iscoroutinefunction(func):
        return func
    else:
        async def async_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
        return async_wrapper

# Ví dụ về các hàm

async def async_function():
    print("Async function is running")
    await asyncio.sleep(1)

def sync_function():
    import time
    time.sleep(1)
    return "This is a sync function"

# Kiểm tra và sử dụng hàm ensure_async

async_func = ensure_async(async_function)
sync_func = ensure_async(sync_function)

# Chạy các hàm để kiểm tra kết quả

class LoopThread(threading.Thread):
    def __init__(self: LoopThread) -> None:
        super().__init__()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def run(self: LoopThread) -> None:
        self.loop.run_forever()

    def stop(self: LoopThread) -> None:
        asyncio.set_event_loop(None)
        self.loop.call_soon_threadsafe(self.loop.stop)

    def create_task(self: LoopThread, coro: Coroutine) -> None:
        self.loop.call_soon_threadsafe(self.loop.create_task, coro)



loop_thread = LoopThread()
loop_thread.create_task(async_function())
loop_thread.start()
loop_thread.stop()