from typing import TYPE_CHECKING
from PySide6.QtCore import Qt, QSize,QPoint,Signal,QRectF
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import ToolButton,FastCalendarPicker
from atklip.gui.qfluentwidgets.common import FluentIcon as FIF,isDarkTheme
from atklip.gui.components import _PushButton
from atklip.gui.components._pushbutton import IconTextChangeButton

from .goto_menu import DateTimeMenu



if TYPE_CHECKING:
    from views.mainlayout import MainWidget


class _Button(ToolButton):
    """ Transparent push button
    Constructors
    ------------
    * ToolButton(`icon`: QIcon | FluentIcon, `parent`: QWidget = None)
    """
    def __init__(self, *args,**kwargs):
        #_icon = QIcon(icon.path())
        super().__init__(*args,**kwargs)
        color = "transparent"
        self.set_stylesheet(color)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(35,35)
        self.setIconSize(QSize(30,30))
        self.setContentsMargins(5,2,5,2)
        self.clicked.connect(self.printsth)
    def printsth(self):
        print(self.sender())
    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,background_color):
        self.setStyleSheet(f"""QToolButton {{
                        background-color: {background_color};
                        border: none;
                        border-radius: 4px;
                    }}""")
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.set_stylesheet(background_color)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().enterEvent(event)
    def leaveEvent(self, event):
        color = "transparent"
        self.set_stylesheet(color)
        super().leaveEvent(event)


class GotoButton(IconTextChangeButton):
    # clicked = Signal()
    sig_remove_menu = Signal()
    def __init__(self,parent:QWidget=None):
        super().__init__(FIF.GOTO_DATE,parent=parent)
        self._parent:MainWidget = parent
        self.setFixedSize(35,35)
        self.setIconSize(QSize(30,30))
        self._menu = None
        self.clicked.connect(self.show_menu)
        self.sig_remove_menu.connect(self.remove_menu)

    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)

    def setupcalendar(self):
        self._menu = DateTimeMenu(self.sig_remove_menu,self._parent)
        #self._menu.moveToThread(QApplication.instance().thread())
        _x = self._parent.width()
        _y = self._parent.height()
        x = (_x-self._menu.width())/2
        y = (_y-self._menu.height())/2
        self._menu.move(QPoint(x, y))
        self._menu.hide()
    def show_menu(self)->None:
        if self._menu is None:
            self._menu = DateTimeMenu(self.sig_remove_menu,self._parent)
            #self._menu.moveToThread(QApplication.instance().thread())
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
    
    def delete(self,ev):
        try:
            ev_pos = ev.position()
        except:
            ev_pos = ev.pos()
        self.remove_menu(ev_pos)
    
    def remove_menu(self,pos=None)->None:
        if self._menu != None:
            if pos!=None:
                _pos = self.mapFromParent(QPoint(pos.x(),pos.y()))
                _rect = QRectF(self._menu.x(),self._menu.y(),self._menu.width(),self._menu.height())
                if not _rect.contains(QPoint(pos.x(),pos.y())):
                    self._menu.hide()
            else:
                self._menu.hide()
  