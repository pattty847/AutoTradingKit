import sys
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Tạo QProcess
        self.process = QProcess(self)

        # Tạo giao diện đơn giản với một nút bấm
        self.button = QPushButton("Run Python Script")
        self.button.clicked.connect(self.run_script)

        # Layout cho giao diện
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def run_script(self):
        # Chạy script Python trong một tiến trình riêng biệt
        self.process.start("uvicorn", ["test_.py", "--workers"])

        # Kết nối tín hiệu khi có dữ liệu output
        self.process.readyReadStandardOutput.connect(self.handle_stdout)

    def handle_stdout(self):
        # Đọc output từ script và hiển thị
        output = self.process.readAllStandardOutput().data().decode()
        print(output)

# Khởi tạo ứng dụng PySide6
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
