from PySide6.QtWidgets import QWidget, QSizePolicy

from atklip.gui.qfluentwidgets.components.container import VWIDGET

from .title_bar_widget import TitleBar


class MovingWidget(VWIDGET):
    def __init__(self, parent:QWidget=None, name:str="Indicators, Metrics, Strategies"):
        super(MovingWidget, self).__init__(parent,name)
        self._parent = parent
        self.setObjectName(name)
        self.startPos = None
        self.title = TitleBar(self,name)
        self.addWidget(self.title)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)

