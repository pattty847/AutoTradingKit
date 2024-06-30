
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui_components.components import Tradingview_Button
from atklip.gui_components import FluentIcon as FIF
# from atklip.gui_components.draw_bar import *
from atklip.gui_components.qfluentwidgets.common import *

class RECIRCLEBIN(QFrame):
    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)
        self.splitToolButton = Tradingview_Button(FIF.CYCLEBIN,self.parent)
   

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
