
from typing import Union
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from atklip.gui_components.qfluentwidgets.common import isDarkTheme

class _PushButton(QPushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self, icon, text, parent):
        super().__init__(icon=icon, text=text, parent=parent)
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

class ReplayButton(_PushButton):
    def __init__(self, sig_replay,icon, text, parent):
        _icon = QIcon(icon.path())
        super().__init__(_icon, text, parent)
        self.setIconSize(QSize(30, 30))
        #self._symbol = args[0]
        #print(args)
        self.clicked.connect(self.on_clicked)
    
    def __str__(self) -> str:
        return self._symbol
        
    def set_text(self, text:Union[None,str])->None:
        if isinstance(text, str):
            raise TypeError("Cannot set text for a SymbolButton")
        super().setText(text)
    def icon(self):
        return super().icon()
    
    def set_symbol(self,symbol,icon):
        self._symbol = symbol
        self.setText(symbol)
        self.setIcon(icon)
    def on_clicked(self)->None:
        #self.clicked.emit(self._symbol)
        print(self.sender())