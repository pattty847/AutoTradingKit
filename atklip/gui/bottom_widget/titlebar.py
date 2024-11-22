
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QWidget, QSpacerItem,QSizePolicy

from atklip.gui import (TabBar, isDarkTheme)
from atklip.gui import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton
from atklip.gui.qfluentwidgets.common.style_sheet import FluentStyleSheet

class TitleBar(QWidget):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add buttons
        self.setStyleSheet("""
                           QWidget {
                                background-color: transparent;
                            }""")
        self._parent = self.parent()
        self.setFixedHeight(40)
        self.toolButtonLayout = QHBoxLayout()
        self.toolButtonLayout.setContentsMargins(5, 0, 5, 0)
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
        self.tabBar.__initWidget = self.__initWidget
        self.tabBar.setMovable(False)
        self.tabBar.setTabMaximumWidth(150)
        self.tabBar.setTabShadowEnabled(True)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))

        self.tabBar.setScrollable(False)
        self.tabBar.setFixedHeight(40)

        self.toolButtonLayout.addWidget(self.tabBar,0,Qt.AlignmentFlag.AlignLeft)
        item = QSpacerItem(380, 1, QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolButtonLayout.addSpacerItem(item)
        self.toolButtonLayout.addWidget(self.minbtn,0,Qt.AlignmentFlag.AlignRight)
        self.toolButtonLayout.addWidget(self.maxbtn,0,Qt.AlignmentFlag.AlignRight)
        
    def __initWidget(self):
        self.tabBar.setFixedHeight(40)
        self.tabBar.setWidget(self.view)
        self.tabBar.setWidgetResizable(True)
        self.tabBar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabBar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # self.hBoxLayout.setSizeConstraint(QHBoxLayout.SetMaximumSize)

        self.tabBar.addButton.clicked.connect(self.tabAddRequested)

        self.tabBar.view.setObjectName('view')
        FluentStyleSheet.TAB_VIEW.apply(self.tabBar)
        FluentStyleSheet.TAB_VIEW.apply(self.tabBar.view)

        self.__initLayout()
    
    def __initLayout(self):
        self.tabBar.hBoxLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.tabBar.itemLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tabBar.widgetLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tabBar.itemLayout.setContentsMargins(5, 5, 5, 5)
        self.tabBar.widgetLayout.setContentsMargins(0, 0, 0, 0)
        self.tabBar.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.tabBar.itemLayout.setSizeConstraint(QHBoxLayout.SetMinAndMaxSize)

        self.tabBar.hBoxLayout.setSpacing(0)
        self.tabBar.itemLayout.setSpacing(0)

        self.tabBar.hBoxLayout.addLayout(self.tabBar.itemLayout)
        self.tabBar.hBoxLayout.addSpacing(3)

        self.tabBar.widgetLayout.addWidget(self.tabBar.addButton, 0, Qt.AlignLeft)
        self.tabBar.hBoxLayout.addLayout(self.tabBar.widgetLayout)
        self.tabBar.hBoxLayout.addStretch(1)