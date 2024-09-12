# coding:utf-8
from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy
from atklip.gui.qfluentwidgets import (Pivot, SegmentedWidget, TabBar, CheckBox, ComboBox,
                            TabCloseButtonDisplayMode, BodyLabel, SpinBox, BreadcrumbBar,
                            SegmentedToggleToolWidget, FluentIcon)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QSizePolicy, QSpacerItem

from atklip.gui.qfluentwidgets.components import SmoothScrollArea,VBoxLayout,HorizontalSeparator,VerticalSeparator
from atklip.gui.qfluentwidgets.common import *
# from .scroll_interface import ScrollInterface


class PivotInterface(QWidget):
    """ Pivot interface """

    Nav = Pivot
    sig_change_widget = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.setFixedSize(300, 140)
        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        # FluentStyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        
    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        _height_widget = widget.height() 
        self.sig_change_widget.emit(_height_widget)
        self.setFixedHeight(_height_widget)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

