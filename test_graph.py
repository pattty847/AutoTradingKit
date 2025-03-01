import sys
import random
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtWidgets import QApplication, QTableView, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel


class PositionModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._original_data = self._data.copy()  # Lưu trữ dữ liệu gốc để lọc

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

    def setData(self, new_data):
        # Xóa toàn bộ dữ liệu cũ và thay thế bằng dữ liệu mới
        self.beginResetModel()
        self._data = new_data
        self._original_data = new_data.copy()  # Cập nhật dữ liệu gốc
        self.endResetModel()

    def filterData(self, keyword):
        # Lọc dữ liệu dựa trên từ khóa (cột Name)
        filtered_data = [
            row for row in self._original_data
            if keyword.lower() in row[1].lower()  # Lọc theo cột Name (index 1)
        ]
        self.beginResetModel()
        self._data = filtered_data
        self.endResetModel()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableView with Search Box")
        self.resize(600, 400)

        # Tạo model với dữ liệu ban đầu là rỗng
        self.model = PositionModel()

        # Tạo QTableView và gán model vào
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Tạo search box (QLineEdit)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by Name...")
        self.search_box.textChanged.connect(self.filter_table)

        # Tạo nút để thay thế toàn bộ dữ liệu bằng dữ liệu ngẫu nhiên
        self.button = QPushButton("Replace with Random Data")
        self.button.clicked.connect(self.replace_with_random_data)

        # Sắp xếp layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.table_view)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def replace_with_random_data(self):
        # Tạo danh sách dữ liệu ngẫu nhiên
        new_data = []
        for _ in range(10):  # Tạo 10 hàng dữ liệu ngẫu nhiên
            random_id = random.randint(1, 100)
            random_name = f"User{random_id}"
            random_age = random.randint(18, 60)
            random_status = random.choice(["Active", "Inactive"])
            random_score = random.randint(0, 100)
            new_data.append([random_id, random_name, random_age, random_status, random_score])

        # Thay thế toàn bộ dữ liệu cũ bằng dữ liệu mới
        self.model.setData(new_data)

    def filter_table(self):
        # Lấy từ khóa từ search box và lọc dữ liệu
        keyword = self.search_box.text()
        self.model.filterData(keyword)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())