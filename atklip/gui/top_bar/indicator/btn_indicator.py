from typing import TYPE_CHECKING,List
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QWidget

from atklip.gui.qfluentwidgets.common import isDarkTheme
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF

from .indicator_menu import IndicatorMenu

if TYPE_CHECKING:
    from views.mainlayout import MainWidget

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
        self.setMaximumWidth(120)
        self.setContentsMargins(5,2,5,2)
    
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

        #super().enterEvent(event)
    def leaveEvent(self, event):
        #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        super().leaveEvent(event)


class IndicatorButton(_PushButton):
    sig_remove_menu = Signal()
    def __init__(self,sig_add_indicator_to_chart, parent):
        _icon = QIcon(FIF.INDICATOR.path())
        super().__init__(_icon, "Indicators", parent)
        self._parent:MainWidget = parent
        self.setIconSize(QSize(30, 30))
        self._pre_x_pos = None
        self._pre_y_pos = None
        self._menu = None
        self.sig_add_indicator_to_chart = sig_add_indicator_to_chart
        self.clicked.connect(self.show_menu)
        self.sig_remove_menu.connect(self.remove_menu,Qt.ConnectionType.AutoConnection)
    def symbol(self) -> str:
        return self._symbol
        
    def set_text(self, text):
        super().setText(text)
    def icon(self):
        return super().icon()
    
    def set_symbol(self,args):
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path,_mode)"""
        icon =  args[4] 
        symbol = args[1]
        self._symbol = symbol
        self.set_text(symbol)
        _icon = QIcon(icon)
        self.setIcon(_icon)

    def setup_menu(self):
        if self._menu is None:
            self._menu = IndicatorMenu(self.sig_remove_menu,self.sig_add_indicator_to_chart,self._parent)
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/2
            self._menu.move(QPoint(x, y))
            self._menu.hide()
    
    def show_menu(self)->None:
        if self._menu is None:
            self._menu = IndicatorMenu(self.sig_remove_menu,self.sig_add_indicator_to_chart,self._parent)
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/3
            self._menu.move(QPoint(x, y))
            self._menu.show()
        else:
            if self._menu.isVisible():
                self._menu.hide() 
            else:
                _x = self._parent.width()
                _y = self._parent.height()
                x = (_x-self._menu.width())/2
                y = (_y-self._menu.height())/3
                self._menu.move(QPoint(x, y))
                self._menu.show()
    def remove_menu(self)->None:
        if self._menu != None:
            self._menu.hide()
    