# coding:utf-8
from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy

import random
import sys
from typing import List, Union

from PySide6.QtCore import Qt, QMargins, QModelIndex, QItemSelectionModel, Property, QRectF,Qt, \
    QAbstractTableModel, QTimer, QModelIndex,QPointF,QPoint
from PySide6.QtGui import QPainter, QColor, QKeyEvent, QPalette, QBrush, QStandardItemModel,QMouseEvent
from PySide6.QtWidgets import (QStyledItemDelegate, QApplication, QStyleOptionViewItem,QHeaderView,
                             QTableView, QTableWidget, QWidget, QTableWidgetItem, QStyle,QVBoxLayout,
                             QStyleOptionButton)


from app.common.style_sheet import StyleSheet
from atklip.gui.qfluentwidgets.common.router import qrouter
from atklip.gui.qfluentwidgets.components import  TabBar

from atklip.gui.qfluentwidgets.common.config import Theme
from atklip.gui.qfluentwidgets.common.style_sheet import setTheme


class TabInterface(QWidget):
    """ Tab interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tabCount = 1

        self.tabBar = TabBar(self)
        self.tabBar.addButton.hide()
        self.stackedWidget = QStackedWidget(self)
        self.tabView = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.tabView)
        self.songInterface = QLabel('Song Interface', self)
        self.albumInterface = QLabel('Album Interface', self)
        self.artistInterface = QLabel('Artist Interface', self)

        # add items to pivot
        self.__initWidget()

    def __initWidget(self):
        self.initLayout()

        self.tabBar.setCloseButtonDisplayMode(2)
        self.addSubInterface(self.songInterface,
                             'tabSongInterface', self.tr('Song'))
        self.addSubInterface(self.albumInterface,
                             'tabAlbumInterface', self.tr('Album'))
        self.addSubInterface(self.artistInterface,
                             'tabArtistInterface', self.tr('Artist'))

        # StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

        self.connectSignalToSlot()

        qrouter.setDefaultRouteKey(
            self.stackedWidget, self.songInterface.objectName())

    def connectSignalToSlot(self):
        # self.tabBar.tabAddRequested.connect(self.addTab)
        # self.tabBar.tabCloseRequested.connect(self.removeTab)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

    def initLayout(self):
        self.tabBar.setTabMaximumWidth(200)
        self.tabBar.setTabMinimumWidth(150)
        self.setFixedHeight(280)
        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)


    def addSubInterface(self, widget: QLabel, objectName, text, icon=None):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.tabBar.addTab(
            routeKey=objectName,
            text=text,
            icon=icon,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onDisplayModeChanged(self, index):
        mode = self.closeDisplayModeComboBox.itemData(index)
        self.tabBar.setCloseButtonDisplayMode(mode)

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        if not widget:
            return

        self.tabBar.setCurrentTab(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

    def addTab(self):
        text = f'硝子酱一级棒卡哇伊×{self.tabCount}'
        self.addSubInterface(QLabel('🥰 ' + text), text, text, ':/gallery/images/Smiling_with_heart.png')
        self.tabCount += 1

    def removeTab(self, index):
        item = self.tabBar.tabItem(index)
        widget = self.findChild(QLabel, item.routeKey())

        self.stackedWidget.removeWidget(widget)
        self.tabBar.removeTab(index)
        widget.deleteLater()


if __name__ == "__main__":
    setTheme(Theme.DARK,True,True)
    app = QApplication(sys.argv)
    
    window = TabInterface()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

