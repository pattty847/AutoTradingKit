from PySide6.QtWidgets import QApplication, QTableView , QHeaderView
from PySide6.QtGui import QStandardItemModel,QStandardItem
from PySide6.QtCore import Qt

# Tạo ứng dụng
app = QApplication([])

# Tạo QTableView và model
tableView = QTableView()
model = QStandardItemModel()

# Thêm dữ liệu vào model
for row in range(5):
    for col in range(5):
        item = QStandardItem(f"Row {row}, Col {col}")
        model.setItem(row, col, item)

# Đặt model cho QTableView
tableView.setModel(model)

# Lấy header ngang (horizontal header)
hor_header = tableView.horizontalHeader()
ver_header = tableView.verticalHeader()

# Đặt chế độ resize cho cột đầu tiên (cột 0)
hor_header.setSectionResizeMode(0, QHeaderView.Fixed)  # Cố định kích thước
ver_header.setSectionResizeMode(0, QHeaderView.Fixed)  # Cố định kích thước
hor_header.resizeSection(0, 35)  # Đặt chiều rộng là 100 pixel
ver_header.resizeSection(0, 35)  # Đặt chiều rộng là 100 pixel

hor_header.setSectionResizeMode(1, QHeaderView.Fixed)  # Cố định kích thước
ver_header.setSectionResizeMode(1, QHeaderView.Fixed)  # Cố định kích thước
hor_header.resizeSection(1, 35)  # Đặt chiều rộng là 100 pixel
ver_header.resizeSection(1, 35)  # Đặt chiều rộng là 100 pixel


hor_header.setSectionResizeMode(4, QHeaderView.Fixed)  # Cố định kích thước
ver_header.setSectionResizeMode(4, QHeaderView.Fixed)  # Cố định kích thước
hor_header.resizeSection(4, 35)  # Đặt chiều rộng là 100 pixel
ver_header.resizeSection(4, 35)  # Đặt chiều rộng là 100 pixel


# Cho phép các cột khác thay đổi kích thước
for col in range(1, model.columnCount()):
    if col in [0,1,4]:
        continue
    hor_header.setSectionResizeMode(col, QHeaderView.Stretch)  # Hoặc QHeaderView.ResizeToContents

# Hiển thị QTableView
tableView.show()

# Chạy ứng dụng
app.exec()