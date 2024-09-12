from atklip.gui.qfluentwidgets.components.widgets import TabBar

from PySide6.QtWidgets import QWidget

class HeaderBar(TabBar):
    def __init__(self, parent:QWidget=None, title:str=""):
        super(HeaderBar,self).__init__(parent)
        self._title = title
        