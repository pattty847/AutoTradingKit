import time
import traceback
from typing import TYPE_CHECKING, Callable
from subprocess import CREATE_NO_WINDOW, Popen

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QItemSelection, QCoreApplication
from PySide6.QtGui import QMovie, QMouseEvent
from PySide6.QtWidgets import QHeaderView, QPushButton, QLabel, QTreeView, QAbstractItemView, QTableView, QProxyStyle, \
  QStyleOption, QTableWidgetItem, QStackedLayout, QStyledItemDelegate

from PySide6.QtCore import QAbstractTableModel, Qt, QCoreApplication, QModelIndex
from PySide6.QtGui import QColor

# from asyncqt import QtCore


from typing import Callable
from PySide6.QtCore import QSize, QCoreApplication, QEvent, Signal, QRect
from PySide6.QtGui import QMovie, QIcon, Qt, QColor, QBrush
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QApplication, QStyleOptionButton, QPushButton
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QPixmap

icon_chrome_closed = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAdhAAAHYQGVw7i2AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAA31JREFUWIXt1l2IlFUYB/Dfef2I0t0ICspuIvq2T91KKKMPoiQMY+siRQ0DoQuhnXWFPqgJorKcmQWxbiIiKMEo+jDySiGTUtrSzVIMsygiImPbDay2ndPFzO7M7sz7zq7sXf2vznme/3n+//fjPOfwX0eYEnt9vFnZEizEFZhVzfyFfvSJPlQKu6fPQD7ONGSNaB0un1TVqF9iszavyIfyyRvoivMFr+OqSQk3YrfoAaXw7dQNdMebRNvRdpLio/gD9yuG7c2SSeqy6KVpEIe5eNv6eNfUDHDuNIiPYpayrTbEeVMx8ME0GoA2Iy6YGJw5bpaPsw2Ypzd8Z4YnjOjEKU2KjaBfdEzib2WDLeWDzxXCR43hmnhi0D4sFOQUQkl3fF7UM2HFNtF6xfBDS9FJoGYgF2/BzurshOBSMw0Y9g3OqsafUgx5a+Np5lgluLEa/0zZq3rDwLjq3fFe0RLjf+Zjoo1K4TfqP0G0tM7OqaJnbQzLdcUHBb2CtxRCXi5ehA9xfl3RFRIbdMelCqGvKt4lKqY89jAen/gGPsGiOlpUtlhv2DMWycfZhvSLLm5amJ+UzdcbBuTiIVySwtulGG5l/C6Y+IcGic3yscYZ0pkhDvMkVlXHWS14TKvewBlNiNcYHCtI2bUZRUdR4UTfZ3DObGYgDc/YENuq7MyDpYoKJ4gZnLFcvYFfU8jnGPZotfS+lvJxbCddlsE63szAkVR6kNMTL3S6d/B1RuFD2ObhuADnZZg82mgg2tOUXMFsI7bgH9FSHE4RX6YUTkgqWywVoaZVMzDD1sxF3G5QQckxw67GSmwRvChaod0CxXBELt6Ge1oYeLc2rEdXPCC4soWRHRI9NoWDDZm1cZa59sv6/sF+BQsIkcZd0NtCHO5U9qVc3NFwvM61LlMcyh4ZFW808KPX0DcJE3CHYZvHZj3xbDzZYs0upbCjPjDewJthRLRa5RrVGqGuMZU9h/YM9s9YPTHY2IhK4SvRcgxPwkLlbXXFDtHKDN6fEsuaHeHpl9JcvBtvYE4Koyy4TpsvDNqLjhTegESnTWFns2R6Ky6G9yQW4UDTfPSyQugzZE2G+Kdm6EgTzzYAm8JB7TpED6F2tw+OSzxWNXJfk5WHsVq7G7wQjjbJ15WaLPIx8bvFEtdju0KotORc7MTT+EWwV9n7Sj6u32r/Iwv/Aq69Co9bkWfdAAAAAElFTkSuQmCC"

class StyledOptionButton(QPushButton):
    def __init__(
            self, 
            parent=None,
            name: str = None,
            iconBase64: object = None,
            size: QSize = QSize(50, 50),
            iconSize: QSize = QSize(15, 15)
            ):
        super(StyledOptionButton, self).__init__(parent)

        # self.setLayout(QHBoxLayout())
        self.setFixedSize(size)

        self.option = QStyleOptionButton()
        self.option.icon.addPixmap(icon_base64_to_pixmap(iconBase64), QIcon.Normal, QIcon.Off)
        self.option.iconSize = iconSize
        

        # rgb(227, 227, 227)
        
        self.setStyleSheet("""
            QPushButton{
                background-color: rgb(237, 237, 237);
                max-height: 30px;
                min-height: 30px;
                border: 0px solid transparent;
                border-radius: 4px;
                margin-left: 2px;
                color: #6b6b6b;
            }
            QPushButton::hover {
                border: 2px solid red;
                background-color: red;
            }
            """)
        self.option.initFrom(self)



def icon_base64_to_pixmap(icon_base64):
    data = QByteArray.fromBase64(icon_base64.encode())
    pixmap = QPixmap()
    pixmap.loadFromData(data)
    return pixmap

BUTTON_SIZE_X = 100  # Size of each button
BUTTON_SIZE_Y = 25  # Size of each button

class StyledItemDelegate(QStyledItemDelegate):
    
    """
    Stack
    Base container

    Args:
        column: index of column
        gap: int
        sx: str = QSS string
            {
                color: red;
                backroud: none;
            }
        alignItems: "space-around" | "space-between" | "space-evenly" | "stretch" | "center" | "end" | "flex-end" | "flex-start" | "start"
        justifyContent: "space-around" | "space-between" | "space-evenly" | "stretch" | "center" | "end" | "flex-end" | "flex-start" | "start"
        flexWrap: "wrap" | "no-wrap"

    Returns:
        new instance of PySyde6.QtWidgets.QFrame
    """

    mousePressedSignal = Signal(str)

    def __init__(self, 
                 parent=None,
                 column: int = None,
                 styledOption: object = None,
                 styledOptions: list = None,
                 onMousePressed: Callable = None
                 ):
        super(StyledItemDelegate, self).__init__(parent)
        if onMousePressed is not None:
            self.mousePressedSignal.connect(onMousePressed)
        self.column = column
        self.styledOption = styledOption
        self.styledOptions = styledOptions


    def split_rect(self, rect, num_divisions):
        # Tính toán chiều rộng của mỗi phần chia
        width_per_division = rect.width() // num_divisions
        
        # Tạo danh sách chứa các hình chữ nhật con
        sub_rects = []
        
        # Tạo các hình chữ nhật con
        for i in range(num_divisions):
            if i == 0:
                sub_rect = QRect((rect.left() + i * width_per_division) - 1, rect.top(), width_per_division + 1, rect.height() - 4)
                sub_rects.append(sub_rect)
            if i == 1:
                sub_rect = QRect(rect.left() + i * width_per_division, rect.top(), width_per_division + 1, rect.height() - 4)
                sub_rects.append(sub_rect)
            if i == 2:
                sub_rect = QRect((rect.left() + i * width_per_division) + 1, rect.top(), width_per_division + 1, rect.height() - 4)
                sub_rects.append(sub_rect)
        return sub_rects

    def point_in_rects(self, point, rects):
        for i, rect in enumerate(rects):
            if rect.contains(point):
                return i
        return -1

    def editorEvent(self, event, model, option, index):
        super().editorEvent(event, model, option, index)
        
        print( event.type())
        sub_rects = self.split_rect(option.rect, 3)
        test_point = event.pos()

        # print('sub_rects___', sub_rects)

        # Kiểm tra xem test_point có nằm trong hình chữ nhật nào không
        result = self.point_in_rects(test_point, sub_rects)

        if option.state & QStyle.State_MouseOver:
            print('eoooooooooooooooooooooooooooeeeeeeeeeeee')
            option.backgroundBrush = QBrush(QColor(211, 211, 211))  # LightGray color

        if index.column() == 2 and event.type() == QEvent.HoverEnter:
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            option.backgroundBrush = QBrush(QColor(211, 211, 211))  # LightGray color
        if index.column() == 2 and event.type() == QEvent.HoverLeave:
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeegggggggggeeeee')
            option.backgroundBrush = QBrush(QColor(0, 0, 0))  # LightGray color
        
        if index.column() == 2 and event.type() == QEvent.MouseButtonRelease:
            if result != -1:
                if result == 0:
                    self.mousePressedSignal.emit(f"openclose_{index.row()}_{index.column()}")
                if result == 1:
                    self.mousePressedSignal.emit(f"edit_{index.row()}_{index.column()}")
                if result == 2:
                    self.mousePressedSignal.emit(f"delete_{index.row()}_{index.column()}")
                return True
            else:
                print("The point is not in any sub-rectangle.")

        # return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        if index.column() == self.column:  # Assuming the button column is the third column
            # buttons = [("Open", "Blac.png"), ("Edit", "Blac.png"), ("Delete", "Blac.png")]  # Define your button labels and icons
            items_count = len(self.styledOptions)
            total_button_width = items_count * BUTTON_SIZE_X
            width = option.rect.width()
            start_x = option.rect.x() + (width - total_button_width) // 2

            profile_state = index.data()

            for i, styledOption in enumerate(self.styledOptions):

                _rect = QRect(start_x + i * BUTTON_SIZE_X, option.rect.y(), BUTTON_SIZE_X, BUTTON_SIZE_Y)
                
                styledOption.option.rect = _rect

                styledOption.rect = _rect
                styledOption.option.icon = QIcon()
                styledOption.option.iconSize = QSize(15, 15)
                styledOption.option.state |= QStyle.State_Enabled
                # styledOption.features = QStyleOptionButton.DefaultButton
                # option.features = QStyleOptionButton.DefaultButton
                
                if i == 0:
                    if profile_state.find('cbrowser') != -1:
                        if profile_state.find('|') != -1:
                            profile_state = profile_state.split("|")[1]
                        if profile_state == "opening":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Opening"
                        elif profile_state == "closing":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Closing"
                        elif profile_state == "closed":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Open"
                        elif profile_state == "opened":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Close"
                        elif profile_state == "opened_other_device":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Open"
                        else:
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Open"
                    else:
                        if profile_state.find('|') != -1:
                            profile_state = profile_state.split("|")[1]
                        if profile_state == "opening":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Opening"
                        elif profile_state == "closing":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Closing"
                        elif profile_state == "closed":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Open"
                        elif profile_state == "opened":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Close"
                        elif profile_state == "opened_other_device":
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Open"
                        else:
                            styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                            styledOption.option.text = "Open"
                elif i == 1:
                        styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                        styledOption.option.text = "Edit"
                elif i == 2:
                        styledOption.option.icon.addPixmap(icon_base64_to_pixmap(icon_chrome_closed), QIcon.Normal, QIcon.Off)
                        styledOption.option.text = "Delete"
                painter.save()
                styledOption.style().drawControl(QStyle.CE_PushButton, styledOption.option, painter, styledOption)
                # QApplication.style().drawControl(QStyle.CE_PushButton, opt, painter, self.button)
                painter.restore()
            return

        super(StyledItemDelegate, self).paint(painter, option, index)

class AbstractTableModel(QAbstractTableModel):
  # https://stackoverflow.com/questions/64287713/how-can-you-set-header-labels-for-qtableview-columns
  def headerData(self, section: int, orientation: Qt.Orientation, role: int):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      # return f"Column {section + 1}"
      return self._tableHead[section]
    if orientation == Qt.Vertical and role == Qt.DisplayRole:
      return f"{section + 1}"

  def __init__(self, 
               parent=None, 
               tableHead=None, 
               data=None):
    # self.setRowCount(0)
    self._tableHead = [item.get('label') if item.get('label') is not None else ""  for item in tableHead]
    
    super(AbstractTableModel, self).__init__(parent)
    self._row = len(data)
    self._column = len(tableHead)
    self._context = parent
    self._data = data
    self.colors = dict()

  def restranUi(self):
    pass
    # QCoreApplication.translate("MainWindow", u"Form", None)

  def rowCount(self, n=None):
    return self._row or len(self._data)

  def columnCount(self, n=None):
    return self._column or len(self._data[0])

  def flags(self, index: QModelIndex) -> Qt.ItemFlags:
    return Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

  def supportedDropActions(self) -> bool:
    return Qt.MoveAction | Qt.CopyAction

  def data(self, index, role=Qt.ForegroundRole):
    if index.isValid():
      if role == Qt.ItemDataRole.DisplayRole or role == Qt.EditRole:
        # if index.column() == 9:
        #   return 
        try:
          value = str(self._data[index.row()][index.column()])
        except:
          value = None
          pass
        return value or ""

      if role == Qt.BackgroundRole:
        color = self.colors.get((index.row(), index.column()))
        if color is not None:
          return "black"
        # return QColor(133, 155, 228)

      if role == Qt.ForegroundRole:
        try:
          value = str(self._data[index.row()][index.column()])
        except IndexError:
          value = ""
          pass
        return QColor(216, 122, 142)
        if index.column() == 7:
          if value.lower() == "expired":
            return QColor(216, 122, 142)
          elif value.lower() == "alive":
            return QColor(0, 150, 136)

        if value == "live":
          return QColor(18, 219, 187)
        elif value == 'blocked':
          return QColor(243, 156, 18)
        elif value == "no_check":
          return QColor(200, 214, 229)
        elif value == "dis":
          return QColor(227, 190, 195)
        elif value == "ver":
          return QColor(255, 139, 67)
        elif value == "pass_wrong":
          return QColor(133, 155, 228)
        elif value == "not_signin":
          return QColor(225, 112, 90)
        elif value == "acc_deleted":
          return QColor(225, 112, 90)
        elif value == "not_exists":
          return QColor(225, 255, 255)
        

      if role == Qt.TextAlignmentRole:
        return int(Qt.AlignLeft | Qt.AlignVCenter)

  def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
    # QModelIndex(1, 2)
    try:
      curentValue = self._data[index.row()][index.column()]
    except IndexError:
      curentValue = ' '
    if not index.isValid():
      return False

    if role == Qt.ItemDataRole.EditRole:
      #print(377, 'setData tableView')
      if value == "":
        return False
      if value != curentValue and value != "":
        try:
          self._data[index.row()][index.column()] = value
        except:
          return False
      else:
        self._data[index.row()][index.column()] = curentValue
      return True

    return False

  # @QtCore.Slot(int, int, QtCore.QVariant)
  def update_item(self, row, col, value):
    ix = self.index(row, col)
    self.setData(ix, value)
    
  def change_color(self, row, column, color):
    ix = self.index(row, column)
    self.colors[(row, column)] = color
    self.dataChanged.emit(ix, ix, (Qt.BackgroundRole,))


class TableView(QTableView):
  class DropmarkerStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
      """Draw a line across the entire row rather than just the column we're hovering over.
      This may not always work depending on global style - for instance I think it won't
      work on OSX."""
      if str(
        element) == "PrimitiveElement.PE_IndicatorItemViewItemDrop" and not option.rect.isNull():  # element == self.PE_IndicatorItemViewItemDrop and
        option_new = QStyleOption(option)
        option_new.rect.setLeft(0)
        if widget:
          option_new.rect.setRight(widget.width())
        option = option_new
      super().drawPrimitive(element, option, painter, widget)

  def __init__(
      self, 
      context=None,
      id: str = None,
      isDense: bool = None,
      isManyRows: bool = None,
      tableHead: list = None,
      singleSelection: bool = False,
      stretchLastSection: bool = False,
      model=None,
      selectionChanged: Callable = None,
      itemDelegates=None,
      backgroundColor: str = "#ffffff",
      isFrozenLastColumn=None
      ):
    super(TableView, self).__init__()
    if id is not None:
      self.setObjectName(id)
    
    self._background_color = "transparent"
    self._isDense = isDense
    self._isManyRows = isManyRows
    self._tableHead = tableHead
    self._model = model
    self._stretchLastSection = stretchLastSection
    self._isFrozenLastColumn = isFrozenLastColumn
    self._itemDelegates = itemDelegates
    self._selectionChanged = selectionChanged
    self._singleSelection = singleSelection

    self._is_filter_mode = False
    self._column_count = len(tableHead)

    self.last_drop_row = None
    self.lastCol = len(tableHead) - 1

    # if self._selectionChanged is not None:
    #   # self.pressed.connect(self._selectionChanged)
    #   self.selectionModel().selectionChanged.connect(self._selectionChanged)

    self.setAttribute(Qt.WA_Hover, True)

    self.setupUi()

    # if self._model:
    #   self._model.dataChanged.connect(self.update_model)

  def setupUi(self):
    self.setDragEnabled(True)
    self.setAcceptDrops(True)
    self.setDragDropOverwriteMode(False)
    # self.setStyle(self.DropmarkerStyle())

    self.update_model(self._model)

    self._horizontalHeader = self.horizontalHeader()
    self._horizontalHeader.setMinimumWidth(200)

    self.horizontalHeader().sectionResized.connect(self.updateSectionWidth)
    self.verticalHeader().sectionResized.connect(self.updateSectionHeight)

    if self._stretchLastSection == True:
      self.horizontalHeader().setStretchLastSection(True)

    if self._singleSelection:
      self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    else:
      self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
      self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    if self._isFrozenLastColumn == True:
      self.viewport().stackUnder(self._frozenColumn)
    self.viewport().setContentsMargins(0, 0, 0, 0)

    self.header = self.horizontalHeader()
    self.header.setDefaultAlignment(Qt.AlignLeft)
    
    self.verticalHeader().hide()

    self.setViewportMargins(0, 0, 0, 0)
    self.setSortingEnabled(True)
    self.setDragEnabled(True)

  def update_model(self, model=None):
    print('update_model______________', self._model._data)
    if model == None:
      model = self._model

    self.setModel(model)
    # self.update(model)

    if isinstance(self._itemDelegates, list):
      for item in self._itemDelegates:
        item.parent = self
        # item.clicked.connect(self.cellButtonClicked)
        self.setItemDelegateForColumn(item.column, item)

    if self._selectionChanged is not None:
      # self.pressed.connect(self._selectionChanged)
      self.selectionModel().selectionChanged.connect(self._selectionChanged)

    self.configUiTableView()

  def configUiTableView(self):
    self.verticalHeader().hide()

    self.setViewportMargins(0, 0, 0, 0)
    
    self._horizontalHeader = self.horizontalHeader()

    for index, item in enumerate(self._tableHead):
      if item.get('resizeMode') == "ResizeToContents":
        self._horizontalHeader.setSectionResizeMode(index, QHeaderView.ResizeToContents)
      if item.get('resizeMode') == "Fixed":
        self._horizontalHeader.setSectionResizeMode(index, QHeaderView.Fixed)
        self.setColumnWidth(index, item.get('width'))
      if item.get('resizeMode') == "Stretch":
        self._horizontalHeader.setSectionResizeMode(index, QHeaderView.Stretch)
      if item.get('columnHidden') == True:
        self.setColumnHidden(index, True)


    self.setStyleSheet(f"""
                QWidget {{
                       background-color: transparent;
                }}
                QTableView {{
                    background-color: transparent;
                    padding: 0px;
                    border: none;
                    gridline-color: transparent;
                    color: #6b6b6b;
                }}

                QTableView::item {{
                    padding-left: 0px;
                    padding-right: 5px;
                }}

                QTableView::item:selected {{
                    background-color: rgba(242, 242, 242, 0.8);
                    color: #6b6b6b;
                }}

                QTableView::section {{
                    background-color: transparent;
                    max-width: 30px;
                    text-align: left;

                }}

                QTableView::horizontalHeader {{
                    background-color: transparent;

                }}

                QTableView::section:horizontal {{
                    background-color: transparent;
                    padding: 0px;
                    border: 1px solid red !important;
                    border-bottom: 1px solid red !important;
                }}


                QTableView::section:vertical {{
                    border: 1px solid red;
                }}

                QTableView .QScrollBar:horizontal {{
                    border: none;
                    background: transparent;
                    min-height: 8px;
                    border-radius: 0px;
                    max-width: 79em;
                }}

                QTableView .QHeaderView::section {{
                    background-color: transparent!important;
                }}

        """)



  def updateSectionWidth(self, logicalIndex, oldSize, newSize):
    if self._isFrozenLastColumn is not None and logicalIndex == self.lastCol:
      self._frozenColumn.setColumnWidth(self.lastCol, newSize)
    self.updateFrozenTableGeometry()

  def updateSectionHeight(self, logicalIndex, oldSize, newSize):
    if  self._frozenColumn is not None:
      self._frozenColumn.setRowHeight(logicalIndex, newSize)

  def resizeEvent(self, event):
    super(TableView, self).resizeEvent(event)
    self.updateFrozenTableGeometry()

  def moveCursor(self, cursorAction, modifiers):
    current = super(TableView, self).moveCursor(cursorAction, modifiers)
    if (cursorAction == QAbstractItemView.MoveLeft and current.column() < self.lastCol and
      self.visualRect(current).topLeft().x() < (self._frozenColumn.columnWidth(self.lastCol))):
      newValue = (self.horizontalScrollBar().value() +
                  self.visualRect(current).topLeft().x() - self._frozenColumn.columnWidth(self.lastCol))
      self.horizontalScrollBar().setValue(newValue)
    return current

  def scrollTo(self, index, hint):
    if index.column() < self.lastCol:
      super(TableView, self).scrollTo(index, hint)

  def updateFrozenTableGeometry(self):
    x_position = self.verticalHeader().width() + self.frameWidth()
    for col in range(0, self.lastCol):
      x_position += self.columnWidth(col)
    x_viewPort = self.verticalHeader().width() + self.viewport().width() - self.columnWidth(
      self.lastCol) + self.frameWidth()
    if self._isFrozenLastColumn is not None:
      self._frozenColumn.setGeometry(x_position if x_position < x_viewPort else x_viewPort,
                                      self.frameWidth(), self.columnWidth(self.lastCol),
                                      self.viewport().height() + self.horizontalHeader().height())


  def cellButtonClicked(self, data):
    print('data_________', data)
    arr_info = data.split('_')
    btn_name = arr_info[0]
    index_row = int(arr_info[1])
    id_profile = self.model().index(index_row, 1).data()
    profile_name = self._main_window.tblProfile._model._data[index_row][3]
    self.profile_id_selected = id_profile


  def dropEvent(self, event):
    sender = event.source()
    super().dropEvent(event)
    dropRow = self.last_drop_row
    destination = self.objectName()
    to_index = self.indexAt(event.pos()).row()

    selectedRows = sender.getselectedRowsFast()

    #print('selectedRows_____________')
    #print(selectedRows)

    arr_id_profile = []

    model = sender.model()
    for srow in selectedRows:
      id = model.index(srow, 1).data()
      arr_id_profile.append(int(id))

    event.accept()


  def getselectedRowsFast(self):
    selectedRows = []
    # for item in self.selectedItems():
    for item in self.selectedIndexes():
      if item.row() not in selectedRows:
        selectedRows.append(item.row())
    selectedRows.sort()
    return selectedRows





TABLE_HEAD = [
    { 'id': 'firstName', 'label': 'First Name', 'resizeMode': 'ResizeToContents' },
    { 'id': 'userEmail', 'label': 'User Email', 'resizeMode': 'Fixed', 'width': 600 },
    { 'id': '', 'resizeMode': 'Stretch'},
]

TABLE_DATA = [
    [
        'Sang',
        'mrkonsun@gmail.com',
        'opening'
    ],
    [
        'Sang',
        'mrkonsun@gmail.com',
        'opening'
    ],
    [
        'Sang',
        'mrkonsun@gmail.com',
        'opening'
    ]
]

for i in range(100):
    TABLE_DATA.append([
        'Sang',
        'mrkonsun@gmail.com',
        'opening'
    ])
        

from PySide6.QtWidgets import QWidget, QVBoxLayout
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.layout = 
        self.setLayout(QVBoxLayout(self))

        table = TableView(
            isDense=False,
            isManyRows=True,
            tableHead=TABLE_HEAD,
            stretchLastSection=True,
            model=AbstractTableModel(self, TABLE_HEAD, TABLE_DATA),
            itemDelegates=[
                StyledItemDelegate(
                    column=2,
                    styledOptions=[
                        StyledOptionButton(iconBase64=icon_chrome_closed),
                        StyledOptionButton(iconBase64=icon_chrome_closed),
                        StyledOptionButton(iconBase64=icon_chrome_closed)
                    ]
                )
            ]
        )
        "set data cho cell"
        table.model().setData(table.model().index(1, 1), 'value', role=Qt.ItemDataRole.EditRole)
        
        # table.setModel(AbstractTableModel(self, TABLE_HEAD, TABLE_DATA))
        
        self.layout().addWidget(table)

    def start_rendering_buttons(self):
        self.thread.start()

    def add_button_to_layout(self, button):
        self.layout.addWidget(button)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
