from typing import TYPE_CHECKING
from PySide6.QtCore import Qt, QSize,QPoint,Signal,QRectF
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import ToolButton,FastCalendarPicker
from atklip.gui.qfluentwidgets.common import FluentIcon as FIF,isDarkTheme
from atklip.gui.components import _PushButton
from atklip.gui.components._pushbutton import IconTextChangeButton


if TYPE_CHECKING:
    from views.mainlayout import MainWidget


class PlayButton(IconTextChangeButton):
    # clicked = Signal()
    sig_remove_menu = Signal()
    def __init__(self,parent:QWidget=None):
        super().__init__(FIF.PLAY,parent=parent)
        self._parent:MainWidget = parent
        self.setFixedSize(30,30)
        self.setIconSize(QSize(15,15))
        self._menu = None


    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
