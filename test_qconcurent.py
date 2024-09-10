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
        yield result

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

    # Thu thập kết quả từ queue trong main_thread
    while True:
        for _ in range(num_processes):
            # print(queue)
            result = queue.get()  # Lấy kết quả từ queue
            print(f"Xử lý kết quả trong main_thread: {result}")

    # Đợi tất cả tiến trình kết thúc
    for p in processes:
        p.join()

    print("Tất cả tiến trình đã hoàn thành.")

# Gọi hàm main để chạy chương trình
if __name__ == "__main__":
    main()
