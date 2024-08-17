import sys
import time
from PySide6.QtCore import Qt
from PySide6.QtConcurrent import QtConcurrent
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


# Hàm thực hiện công việc nặng
def heavy_computation():
    time.sleep(5)  # Giả lập công việc nặng bằng cách ngủ trong 5 giây
    return "Kết quả từ tác vụ nền"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("QtConcurrent Example")

        # Layout và widget
        layout = QVBoxLayout()

        self.label = QLabel("Nhấn nút để bắt đầu tác vụ")
        layout.addWidget(self.label)

        self.button = QPushButton("Bắt đầu tác vụ")
        self.button.clicked.connect(self.start_task)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_task(self):
        self.label.setText("Đang thực hiện tác vụ...")

        # Sử dụng QtConcurrent.run để thực hiện tác vụ nặng trong nền
        future = QtConcurrent.ThreadFunctionResult(heavy_computation)

        # Khi tác vụ hoàn thành, cập nhật giao diện
        future.resultReady.connect(self.task_finished)

    def task_finished(self):
        # Cập nhật kết quả sau khi tác vụ hoàn thành
        self.label.setText("Tác vụ hoàn thành! Kết quả: " + future.result())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
