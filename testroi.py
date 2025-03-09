import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

class TextDrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vẽ văn bản với QPainter")
        self.setGeometry(100, 100, 400, 300)  # Đặt kích thước cửa sổ

    def paintEvent(self, event):
        # Tạo một QPainter để vẽ lên widget
        painter = QPainter(self)

        # Đặt màu sắc và font chữ
        painter.setPen(QColor(0, 0, 0))  # Màu đen
        painter.setFont(QFont("Arial", 20))  # Font Arial, kích thước 20

        # Vẽ văn bản tại vị trí (x, y)
        text = "Hello, PySide6!"
        painter.drawText(50, 100, text)  # Vẽ văn bản tại (50, 100)

        # Vẽ thêm một văn bản khác với màu và font khác
        painter.setPen(QColor(255, 0, 0))  # Màu đỏ
        painter.setFont(QFont("Times New Roman", 30, QFont.Bold))  # Font Times New Roman, kích thước 30, in đậm
        painter.drawText(50, 200, "This is a QPainter example!")

        # Kết thúc vẽ
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextDrawingWidget()
    window.show()
    sys.exit(app.exec())