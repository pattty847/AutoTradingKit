import sys
import random
from PySide6.QtCore import QProcess, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit

class RandomNumberTask(QRunnable):
    """Task to print random numbers"""
    def run(self):
        for _ in range(5):
            print(f"Random Number: {random.randint(0, 100)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        # Initialize QThreadPool
        self.thread_pool = QThreadPool()

    def initUI(self):
        self.setWindowTitle("QProcess and QThreadPool Example")
        
        # Layout and widgets
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.run_process_button = QPushButton("Run QProcess")
        self.run_process_button.clicked.connect(self.run_process)
        layout.addWidget(self.run_process_button)

        self.run_threadpool_button = QPushButton("Run QThreadPool Task")
        self.run_threadpool_button.clicked.connect(self.run_threadpool_task)
        layout.addWidget(self.run_threadpool_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_process(self):
        # Initialize QProcess
        self.process = QProcess(self)

        # Connect output to text_edit widget
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

        # Start the process (running 'ping' command)
        self.process.start("ping", ["-t","8.8.8.8"])

    def handle_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.text_edit.append(output)

    def handle_stderr(self):
        error_output = self.process.readAllStandardError().data().decode()
        self.text_edit.append(f"Error: {error_output}")

    def run_threadpool_task(self):
        # Create and start a new task in the thread pool
        task = RandomNumberTask()
        self.thread_pool.start(task)

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
