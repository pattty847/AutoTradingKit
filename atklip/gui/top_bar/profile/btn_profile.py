
import os
from typing import Union
from PySide6.QtWidgets import QWidget,QVBoxLayout
from PySide6.QtGui import QIcon,Qt
from atklip.gui.components.exchange_icon import ExchangeICon
# from atklip.gui.components.readme import ReadmeViewer
from atklip.gui.qfluentwidgets.common.icon import get_real_path
from atklip.gui.qfluentwidgets.components.widgets.tool_tip import ToolTipFilter, ToolTipPosition
from atklip.gui.qfluentwidgets.components import MaskDialogBase
from .profile_menu import ProfileWindow
class AvatarButton(QWidget):
    def __init__(self, parent=None,icon_path=u":/qfluentwidgets/images/profiles/profile2.png"): #u":/qfluentwidgets/images/profiles/profile2.png"
        super().__init__(parent)
        self.parent = parent

        self.setStyleSheet("background-color:transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.setMouseTracking(True)
        self.btn = ExchangeICon(self)
        self.btn.setToolTip("About ATK")
        layout.addWidget(self.btn)
        self.btn.set_pixmap_icon(icon_path,35)
        self.Readme = None
        
        self.btn.clicked.connect(self.showDialog)
    
    def set_text(self, text:Union[None,str])->None:
        self.btn.setText(text)
    
    def showDialog(self):
        w = ProfileWindow(self.parent)
        ICON_PATH = os.path.join("atklip", "appdata", "appico.ico")
        icon = QIcon(get_real_path(ICON_PATH))
        w.setWindowTitle("About ATK")
        w.setWindowIcon(icon)
        w.setAttribute(Qt.WA_DeleteOnClose)
        if w.exec():
            w.deleteLater()

    