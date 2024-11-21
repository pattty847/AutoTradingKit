
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QWidget, QSpacerItem,QSizePolicy

from atklip.gui import (TabBar, isDarkTheme)
from atklip.gui import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton

class TitleBar(QWidget):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add buttons
        self._parent = self.parent()
        self.setFixedHeight(45)
        self.toolButtonLayout = QHBoxLayout()
        self.toolButtonLayout.setContentsMargins(5, 1, 5, 1)
        self.toolButtonLayout.setSpacing(2)
        self.setLayout(self.toolButtonLayout)
        
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)

        self.minbtn = IconTextChangeButton(FIF.MINDOWN, parent=self)
        self.maxbtn = IconTextChangeButton(FIF.MAXIMUM, parent=self)
        self.minbtn.setFixedSize(30,30)
        self.minbtn.setIconSize(QSize(25,25))
        self.maxbtn.setFixedSize(30,30)
        self.maxbtn.setIconSize(QSize(25,25))
        # add tab bar
        self.tabBar = TabBar(self)

        self.tabBar.setMovable(False)
        self.tabBar.setTabMaximumWidth(150)
        # self.tabBar.setTabShadowEnabled(True)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))

        self.tabBar.setScrollable(False)

        self.toolButtonLayout.addWidget(self.tabBar,0,Qt.AlignmentFlag.AlignLeft)
        item = QSpacerItem(380, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.toolButtonLayout.addSpacerItem(item)
        self.toolButtonLayout.addWidget(self.minbtn,0,Qt.AlignmentFlag.AlignRight)
        self.toolButtonLayout.addWidget(self.maxbtn,0,Qt.AlignmentFlag.AlignRight)
        self.setStyleSheet("""
                           QWidget {
                                background-color: transparent;
                            }""")
        # FluentStyleSheet.TITLEBAR.apply(self)
        


    # def mousePressEvent(self, event):
    #     self.setCursor(Qt.CursorShape.ClosedHandCursor)
    #     return super().mousePressEvent(event)
    
    # def mouseReleaseEvent(self, event) -> None:
    #     self.setCursor(Qt.CursorShape.OpenHandCursor)
    #     return super().mouseReleaseEvent(event)
    
    # def enterEvent(self, event) -> None:
    #     self.setCursor(Qt.CursorShape.OpenHandCursor)
    #     return super().enterEvent(event)
    # def leaveEvent(self, event) -> None:
    #     self.setCursor(Qt.CursorShape.ArrowCursor)
    #     return super().leaveEvent(event)