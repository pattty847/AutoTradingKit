
from typing import Union
from PySide6.QtCore import QSize,Signal
from PySide6.QtGui import QIcon,QMovie,QColor
from PySide6.QtWidgets import QPushButton,QLabel,QWidget,QGraphicsDropShadowEffect

from atklip.gui.qfluentwidgets.common import isDarkTheme
from atklip.gui.qfluentwidgets.components import HWIDGET
from atklip.gui.components import StreamingMode

from atklip.gui.components._pushbutton import IconTextChangeButton

class _PushButton(QPushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self,parent):
        super().__init__(parent=parent)
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        self.setFixedHeight(35)
        self.setMinimumWidth(100)
        self.setMaximumWidth(130)
        self.setContentsMargins(0,0,0,0)
    
    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                            
                        }}""")
    
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.setStyleSheet(f"""QPushButton {{
            background-color: {background_color};
            border: none;
            border-radius: 4px;
            color: {color};
            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
            
            }}""")

        super().enterEvent(event)
    def leaveEvent(self, event):
        #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        super().leaveEvent(event)

class ModeButton(HWIDGET):
    clicked = Signal()
    def __init__(self,text="Live Trading",parent:QWidget=None):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.setFixedHeight(35)
        self.label = StreamingMode(self)
        self.btn = IconTextChangeButton(text=text,parent=self)
        self.addWidget(self.btn)
        self.addWidget(self.label)
        self._is_live = False
        self.btn.clicked.connect(self.on_clicked)
    
    @property
    def is_live(self):
        return self._is_live
    @is_live.setter
    def is_live(self, value):
        self._is_live = value
    
    def set_text(self, text:Union[None,str])->None:
        self.btn.setText(text)
    
    def on_clicked(self)->None:
        self.clicked.emit()
        if self.is_live:
            self.is_live = False
        else:
            self.is_live = True
        self.label.start()