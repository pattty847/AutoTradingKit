from multiprocessing import freeze_support
import time
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Task nặng cần nhiều CPU
def cpu_bound_task(n):
    print(f"Starting CPU-bound task {n} in process")
    result = math.factorial(n)
    print(f"Completed CPU-bound task {n} in process")
    return result

# Task I/O-bound cần nhiều thời gian chờ I/O
def io_bound_task(n):
    print(f"Starting I/O-bound task {n} in thread")
    time.sleep(2)  # Giả lập tác vụ chờ I/O
    print(f"Completed I/O-bound task {n} in thread")
    
    # Bây giờ sử dụng ProcessPoolExecutor để xử lý tính toán CPU-bound
    with ProcessPoolExecutor(max_workers=2) as process_executor:
        future = process_executor.submit(cpu_bound_task, 100000)
        return future

# Chạy ThreadPoolExecutor để xử lý các tác vụ I/O-bound
def main():
    with ThreadPoolExecutor(max_workers=3) as thread_executor:
        futures = [thread_executor.submit(io_bound_task, i) for i in range(3)]
        for future in futures:
            print(f"Result: {future.result()}")
if __name__ == '__main__':
    freeze_support()
    main()