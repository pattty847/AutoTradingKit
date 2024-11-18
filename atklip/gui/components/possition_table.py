# coding: utf-8
import random
import sys
from typing import List, Union

from PySide6.QtCore import Qt, QMargins, QModelIndex, QItemSelectionModel, Property, QRectF,Qt, \
    QAbstractTableModel, QTimer, QModelIndex
from PySide6.QtGui import QPainter, QColor, QKeyEvent, QPalette, QBrush
from PySide6.QtWidgets import (QStyledItemDelegate, QApplication, QStyleOptionViewItem,QHeaderView,
                             QTableView, QTableWidget, QWidget, QTableWidgetItem, QStyle,QVBoxLayout,
                             QStyleOptionButton)

from qfluentwidgets import TableWidget, isDarkTheme, setTheme, Theme, TableView,\
    TableItemDelegate, setCustomStyleSheet,SmoothScrollDelegate\
    ,getFont,themeColor
from qfluentwidgets.components.widgets.check_box import CheckBoxIcon
from qfluentwidgets.components.widgets.line_edit import LineEdit
from qfluentwidgets.components.widgets.label import TitleLabel

from atklip.controls.position import Position


class PositionItemDelegate(QStyledItemDelegate):

    def __init__(self, parent: QTableView):
        super().__init__(parent)
        self.margin = 2
        self.hoverRow = -1
        self.pressedRow = -1
        self.selectedRows = set()

    def setHoverRow(self, row: int):
        self.hoverRow = row

    def setPressedRow(self, row: int):
        self.pressedRow = row

    def setSelectedRows(self, indexes: List[QModelIndex]):
        self.selectedRows.clear()
        for index in indexes:
            self.selectedRows.add(index.row())
            if index.row() == self.pressedRow:
                self.pressedRow = -1

    def sizeHint(self, option, index):
        # increase original sizeHint to accommodate space needed for border
        size = super().sizeHint(option, index)
        size = size.grownBy(QMargins(0, self.margin, 0, self.margin))
        return size

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        lineEdit = TitleLabel(parent)
        # lineEdit = LineEdit(parent)
        lineEdit.setProperty("transparent", False)
        lineEdit.setStyle(QApplication.style())
        lineEdit.setText(option.text)
        # lineEdit.setClearButtonEnabled(True)
        return lineEdit

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        rect = option.rect
        y = rect.y() + (rect.height() - editor.height()) // 2
        x, w = max(8, rect.x()), rect.width()
        if index.column() == 0:
            w -= 8

        editor.setGeometry(x, y, w, rect.height())

    def _drawBackground(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """ draw row background """
        r = 5
        if index.column() == 0:
            rect = option.rect.adjusted(4, 0, r + 1, 0)
            painter.drawRoundedRect(rect, r, r)
        elif index.column() == index.model().columnCount(index.parent()) - 1:
            rect = option.rect.adjusted(-r - 1, 0, -4, 0)
            painter.drawRoundedRect(rect, r, r)
        else:
            rect = option.rect.adjusted(-1, 0, 1, 0)
            painter.drawRect(rect)

    def _drawIndicator(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """ draw indicator """
        y, h = option.rect.y(), option.rect.height()
        ph = round(0.35*h if self.pressedRow == index.row() else 0.257*h)
        painter.setBrush(themeColor())
        painter.drawRoundedRect(4, ph + y, 3, h - 2*ph, 1.5, 1.5)

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        # font
        option.font = index.data(Qt.FontRole) or getFont(13)
        # text color
        textColor = Qt.white if isDarkTheme() else Qt.black
        textBrush = index.data(Qt.ForegroundRole)   # type: QBrush
        if textBrush is not None:
            textColor = textBrush.color()

        option.palette.setColor(QPalette.Text, textColor)
        option.palette.setColor(QPalette.HighlightedText, textColor)

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(QPainter.Antialiasing)

        # set clipping rect of painter to avoid painting outside the borders
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # call original paint method where option.rect is adjusted to account for border
        option.rect.adjust(0, self.margin, 0, -self.margin)

        # draw highlight background
        isHover = self.hoverRow == index.row()
        isPressed = self.pressedRow == index.row()
        isAlternate = index.row() % 2 == 0 and self.parent().alternatingRowColors()
        isDark = isDarkTheme()

        c = 255 if isDark else 0
        alpha = 0

        if index.row() not in self.selectedRows:
            if isPressed:
                alpha = 9 if isDark else 6
            elif isHover:
                alpha = 12
            elif isAlternate:
                alpha = 5
        else:
            if isPressed:
                alpha = 15 if isDark else 9
            elif isHover:
                alpha = 25
            else:
                alpha = 17

        if index.data(Qt.ItemDataRole.BackgroundRole):
            painter.setBrush(index.data(Qt.ItemDataRole.BackgroundRole))
        else:
            painter.setBrush(QColor(c, c, c, alpha))

        self._drawBackground(painter, option, index)

        # draw indicator
        if index.row() in self.selectedRows and index.column() == 0 and self.parent().horizontalScrollBar().value() == 0:
            self._drawIndicator(painter, option, index)

        if index.data(Qt.CheckStateRole) is not None:
            self._drawCheckBox(painter, option, index)

        painter.restore()
        super().paint(painter, option, index)

    def _drawCheckBox(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))

        isDark = isDarkTheme()

        r = 4.5
        x = option.rect.x() + 15
        y = option.rect.center().y() - 9.5
        rect = QRectF(x, y, 19, 19)

        if checkState == Qt.CheckState.Unchecked:
            painter.setBrush(QColor(0, 0, 0, 26) if isDark else QColor(0, 0, 0, 6))
            painter.setPen(QColor(255, 255, 255, 142) if isDark else QColor(0, 0, 0, 122))
            painter.drawRoundedRect(rect, r, r)
        else:
            painter.setPen(themeColor())
            painter.setBrush(themeColor())
            painter.drawRoundedRect(rect, r, r)

            if checkState == Qt.CheckState.Checked:
                CheckBoxIcon.ACCEPT.render(painter, rect)
            else:
                CheckBoxIcon.PARTIAL_ACCEPT.render(painter, rect)

        painter.restore()
        
    # def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
    #     super().initStyleOption(option, index)
    #     if index.column() != 1:
    #         return

    #     if isDarkTheme():
    #         option.palette.setColor(QPalette.Text, Qt.white)
    #         option.palette.setColor(QPalette.HighlightedText, Qt.white)
    #     else:
    #         option.palette.setColor(QPalette.Text, Qt.red)
    #         option.palette.setColor(QPalette.HighlightedText, Qt.red)
    

class PositionModel(QAbstractTableModel):
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

    def update_row(self,row,column, value):
        index = self.index(row, column)
        self.setData(index, value, Qt.EditRole)
    
    def updateRows(self, rows_to_update):
        """Cập nhật dữ liệu của các hàng cụ thể."""
        for row in rows_to_update:
            if 0 <= row < self.rowCount(None):  # Kiểm tra nếu hàng nằm trong phạm vi hợp lệ
                # Cập nhật dữ liệu cho từng cột trong hàng
                for column in range(self.columnCount(None)):
                    new_value = random.randint(0, 100)  # Giá trị mới ngẫu nhiên
                    index = self.index(row, column)
                    self.setData(index, new_value, Qt.EditRole)
    
    def setData(self, index, value, role):
        if index.column() == 1:
            print("column side pos long/short")
        elif index.column() == 2:
            print("column type pos buy/sell")
        elif index.column() == 3:
            print("column entry time pos")
        elif index.column() == 4:
            print("column close time pos")
        elif index.column() == 5:
            print("column entry price")
        elif index.column() == 6:
            print("column close price")
        elif index.column() == 6:
            print("column quanty pos")
        elif index.column() == 6:
            print("column lavarate price")
        elif index.column() == 6:
            print("column PnL pos")
        elif index.column() == 6:
            print("column MaxDrawdown pos")
        elif index.column() == 6:
            print("column Fee pos")
        elif index.column() == 6:
            print("column Balance")
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        "NoItemFlags"
        return Qt.ItemIsEnabled


class PositionTable(TableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        
        self.verticalHeader().setDefaultSectionSize(45)
        self.setItemDelegate(PositionItemDelegate(self))
        
        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSortingEnabled(True)
        
        data = [
            ['かばん', 'aiko', 'かばん', '2004', '5:04'],
            ['爱你', '王心凌', '爱你', '2004', '3:39'],
            ['星のない世界', 'aiko', '星のない世界/横顔', '2007', '5:30'],
            ['横顔', 'aiko', '星のない世界/横顔', '2007', '5:06'],
            ['秘密', 'aiko', '秘密', '2008', '6:27'],
            ['シアワセ', 'aiko', '秘密', '2008', '5:25'],
            ['二人', 'aiko', '二人', '2008', '5:00'],
            ['スパークル', 'RADWIMPS', '君の名は。', '2016', '8:54'],
            ['なんでもないや', 'RADWIMPS', '君の名は。', '2016', '3:16'],
            ['前前前世', 'RADWIMPS', '人間開花', '2016', '4:35'],
            ['恋をしたのは', 'aiko', '恋をしたのは', '2016', '6:02'],
            ['夏バテ', 'aiko', '恋をしたのは', '2016', '4:41'],
            ['もっと', 'aiko', 'もっと', '2016', '4:50'],
            ['問題集', 'aiko', 'もっと', '2016', '4:18'],
            ['半袖', 'aiko', 'もっと', '2016', '5:50'],
            ['ひねくれ', '鎖那', 'Hush a by little girl', '2017', '3:54'],
            ['シュテルン', '鎖那', 'Hush a by little girl', '2017', '3:16'],
            ['愛は勝手', 'aiko', '湿った夏の始まり', '2018', '5:31'],
            ['ドライブモード', 'aiko', '湿った夏の始まり', '2018', '3:37'],
            ['うん。', 'aiko', '湿った夏の始まり', '2018', '5:48'],
            ['キラキラ', 'aikoの詩。', '2019', '5:08', 'aiko'],
            ['恋のスーパーボール', 'aiko', 'aikoの詩。', '2019', '4:31'],
            ['磁石', 'aiko', 'どうしたって伝えられないから', '2021', '4:24'],
            ['食べた愛', 'aiko', '食べた愛/あたしたち', '2021', '5:17'],
            ['列車', 'aiko', '食べた愛/あたしたち', '2021', '4:18'],
            ['花の塔', 'さユり', '花の塔', '2022', '4:35'],
            ['夏恋のライフ', 'aiko', '夏恋のライフ', '2022', '5:03'],
            ['あかときリロード', 'aiko', 'あかときリロード', '2023', '4:04'],
            ['荒れた唇は恋を失くす', 'aiko', '今の二人をお互いが見てる', '2023', '4:07'],
            ['ワンツースリー', 'aiko', '今の二人をお互いが見てる', '2023', '4:47'],
        ]
        
        self.pos_model = PositionModel(data)
        
        self.setModel(self.pos_model)

class RealTimeTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Update Table Example")
        self.setStyleSheet("""
                           QWidget {
                                border: 1px solid rgba(255, 255, 255, 13);
                                border-radius: 5px;
                                background-color: transparent;
                            }""")
        # Layout chính
        layout = QVBoxLayout()
        self.table_view = PositionTable(self)
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
        self.table_view.model().updateRows(rows_to_update)

if __name__ == "__main__":
    setTheme(Theme.DARK,True,True)
    app = QApplication(sys.argv)
    
    window = RealTimeTable()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

