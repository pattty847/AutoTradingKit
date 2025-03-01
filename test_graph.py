import sys
import random
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QApplication, QTableView, QPushButton, QVBoxLayout, QWidget


class PositionModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 5  # Số cột trong bảng

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["ID", "Name", "Age", "Status", "Score"][section]  # Tên các cột
        return None

    def addRow(self, row_data, parent=QModelIndex()):
        # Thêm hàng mới vào cuối danh sách
        row_position = self.rowCount()
        self.beginInsertRows(parent, row_position, row_position)
        self._data.append(row_data)
        self.endInsertRows()

    def updateRow(self, row, new_data, parent=QModelIndex()):
        if row < 0 or row >= self.rowCount():
            return False
        self._data[row] = new_data
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right)
        return True


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableView with Random Data")
        self.resize(600, 400)

        # Tạo model với dữ liệu ban đầu là rỗng
        self.model = PositionModel()

        # Tạo QTableView và gán model vào
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Tạo nút để thêm dữ liệu ngẫu nhiên
        self.button = QPushButton("Add Random Data")
        self.button.clicked.connect(self.add_random_data)

        # Sắp xếp layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def add_random_data(self):
        # Tạo dữ liệu ngẫu nhiên
        random_id = random.randint(1, 100)
        random_name = f"User{random_id}"
        random_age = random.randint(18, 60)
        random_status = random.choice(["Active", "Inactive"])
        random_score = random.randint(0, 100)

        # Thêm dữ liệu vào model
        new_row = [random_id, random_name, random_age, random_status, random_score]
        self.model.addRow(new_row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())