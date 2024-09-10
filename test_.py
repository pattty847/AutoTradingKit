import sys
import time
from PySide6.QtCore import QRunnable, QThreadPool, Signal, QObject,QThread
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar

class WorkerSignals(QObject):
    progress = Signal(int)  # Tín hiệu để truyền tiến trình (giá trị từ 0 đến 100)
    finished = Signal(str)  # Tín hiệu để báo hoàn thành tác vụ

class Worker(QRunnable):
    def __init__(self, task_number, signals):
        super().__init__()
        self.task_number = task_number
        self.signals = signals

    def run(self):
        # Mô phỏng công việc nặng và cập nhật tiến trình
        for i in range(1010):
            time.sleep(0.0001)  # Giả lập công việc
            self.signals.progress.emit(i)  # Gửi tiến trình cập nhật
        
        # Gửi tín hiệu hoàn thành khi công việc kết thúc
        self.signals.finished.emit(f"Tác vụ {self.task_number} hoàn thành")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("QThreadPool với nhiều Worker")
        
        # Thiết lập giao diện
        self.label = QLabel("Đang xử lý các tác vụ...")
        self.progress_bars = []
        self.max_workers = 10
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        
        for i in range(self.max_workers):
            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            self.progress_bars.append(progress_bar)
            layout.addWidget(progress_bar)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Tạo QThreadPool để quản lý các luồng
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(self.max_workers)  # Giới hạn số lượng luồng tối đa
        
        # Gửi nhiều tác vụ vào QThreadPool
        self.task_count = 50  # Số lượng tác vụ lớn
        
        for i in range(self.task_count):
            worker_signals = WorkerSignals()
            worker_signals.progress.connect(self.update_progress(i % self.max_workers))
            worker_signals.finished.connect(self.task_finished)
            worker = Worker(i + 1, worker_signals)
            self.thread_pool.start(worker)

    def update_progress(self, worker_index):
        def callback(progress):
            # Cập nhật tiến trình của Worker
            self.progress_bars[worker_index].setValue(progress)
        return callback

    def task_finished(self, message):
        # Cập nhật thông báo khi một tác vụ hoàn thành
        current_text = self.label.text()
        self.label.setText(current_text + "\n" + message)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
