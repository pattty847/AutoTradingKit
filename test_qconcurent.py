from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from multiprocessing import Process, Queue

# Hàm giả lập nhiệm vụ xử lý trong tiến trình con
def worker_function(i, q):
    n = 0
    while True:
        time.sleep(0.01)  # Giả lập công việc tốn thời gian
        result = f"Kết quả từ tiến trình {i} -- {n} "
        n+=1
        q.put(result)  # Đưa kết quả vào queue
        # yield result

def listen(num_processes,queue):
    while True:
        time.sleep(0.01)
        
        for _ in range(num_processes):
            # print(queue)
            result = queue.get()  # Lấy kết quả từ queue
            print(f"Xử lý kết quả trong main_thread: {result}")
            

def main():
    # Tạo một Queue để chia sẻ dữ liệu giữa các tiến trình
    queue = Queue()

    # Tạo danh sách các tiến trình
    processes = []
    num_processes = 5  # Số tiến trình cần chạy

    # Khởi tạo và chạy các tiến trình
    for i in range(num_processes):
        p = Process(target=worker_function, args=(i, queue))
        processes.append(p)
        p.start()
    with ProcessPoolExecutor(5) as executor:
        # Tạo future task và chạy trong process riêng
        # future = executor.submit(worker_function(5, queue))
        future = executor.submit(listen(num_processes, queue))

    # Thu thập kết quả từ queue trong main_thread
    

    # Đợi tất cả tiến trình kết thúc
    for p in processes:
        p.join()

    print("Tất cả tiến trình đã hoàn thành.")

# Gọi hàm main để chạy chương trình
if __name__ == "__main__":
    main()
