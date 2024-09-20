import concurrent.futures
import multiprocessing
import time

# Hàm thực hiện task chạy trong process riêng
def task(queue, n):
    count = 0
    while count < n:
        # Giả lập công việc, ví dụ đợi 1 giây
        time.sleep(1)
        count += 1
        print(f"Main thread received: {count}")
        # Gửi kết quả mỗi vòng lặp về hàng đợi
        queue.put(f"Result from loop {count}")
        time.sleep(1)
    
    queue.put("Done")  # Gửi tín hiệu hoàn thành

# Hàm nhận kết quả từ hàng đợi
def result_listener(queue):
    while True:
        result = queue.get()
        print(f"Main thread received: {result}")
        if result == "Done":
            break
        

# Main function
if __name__ == "__main__":
    # Tạo hàng đợi để truyền dữ liệu giữa các tiến trình
    queue = multiprocessing.Queue()
    # Sử dụng ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(1) as executor:
        # Tạo future task và chạy trong process riêng
        future = executor.submit(task, queue, 5)
        future = executor.submit(result_listener, queue)
        
        # Nhận kết quả trong main thread

