
from typing import Union
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from atklip.gui.qfluentwidgets.common import isDarkTheme
from atklip.gui.qfluentwidgets.common.config import Theme
from atklip.gui.qfluentwidgets.common.icon import FluentIcon, change_svg_color
from atklip.gui.components._pushbutton import IconTextChangeButton


class ReplayButton(IconTextChangeButton):
    def __init__(self,icon, text, parent):
        super().__init__(icon, text, parent)
        self.setIconSize(QSize(30, 30))
        
    def set_text(self, text:Union[None,str])->None:
        if isinstance(text, str):
            raise TypeError("Cannot set text for a SymbolButton")
        super().setText(text)
        
    def icon(self):
        return super().icon()
    

