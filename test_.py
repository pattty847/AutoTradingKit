from PySide6.QtCore import Qt, QAbstractTableModel, QTimer, QModelIndex
from PySide6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget,QTableWidget
import random
import sys

class RealTimeTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def updateRows(self, rows_to_update):
        """Cập nhật dữ liệu của các hàng cụ thể."""
        for row in rows_to_update:
            if 0 <= row < self.rowCount(None):  # Kiểm tra nếu hàng nằm trong phạm vi hợp lệ
                # Cập nhật dữ liệu cho từng cột trong hàng
                for column in range(self.columnCount(None)):
                    new_value = random.randint(0, 100)  # Giá trị mới ngẫu nhiên
                    index = self.index(row, column)
                    self.setData(index, new_value, Qt.EditRole)

        # Thông báo cập nhật dữ liệu cho các hàng cụ thể
        first_row = min(rows_to_update)
        last_row = max(rows_to_update)
        top_left_index = self.index(first_row, 0)
        bottom_right_index = self.index(last_row, self.columnCount(None) - 1)
        # self.dataChanged.emit(top_left_index, bottom_right_index)
class RealTimeTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Update Table Example")

        # Dữ liệu khởi tạo
        data = [
            [random.randint(0, 100) for _ in range(5)] for _ in range(10)
        ]

        # Tạo mô hình dữ liệu
        self.model = RealTimeTableModel(data)

        # Tạo QTableView và gán mô hình dữ liệu
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Layout chính
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        # Tạo QTimer để cập nhật dữ liệu theo thời gian thực
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(1000)  # Cập nhật mỗi 1 giây

    def update_table(self):
        """Cập nhật dữ liệu của các hàng cụ thể trong bảng."""
        # Ví dụ chỉ cập nhật các hàng 2, 4 và 6
        rows_to_update = [2, 4, 6]
        self.model.updateRows(rows_to_update)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimeTable()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
