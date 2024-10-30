
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.components import Favorite_Draw_Button
from atklip.gui import FluentIcon as FIF
# from atklip.gui.draw_bar import *
from atklip.gui.qfluentwidgets.common import *
from .favorite_draw_tool_setting_wg import FavoriteSettingMenu


class FAVORITE(QFrame):
    def __init__(self,parent:QWidget=None,sig_add_to_favorite=None,sig_draw_object_name=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.sig_add_to_favorite = sig_add_to_favorite
        self.sig_draw_object_name = sig_draw_object_name
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)

        self.splitToolButton = Favorite_Draw_Button(FIF.FAVORITE,self)
        
        self.splitToolButton.clicked.connect(self.add_remove_favorite_wg)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    def add_remove_favorite_wg(self):
        if self.splitToolButton.isChecked():
            _x = self.parent.chartbox_splitter.chart.width()
            _y = self.parent.chartbox_splitter.chart.height()

            menu = FavoriteSettingMenu(self.parent,self.sig_add_to_favorite,self.sig_draw_object_name)
            
            self.parent.chartbox_splitter.chart.sig_show_pop_up_draw_tool.connect(menu.uncheck_btns)
            
            self.splitToolButton.clicked.connect(menu.deleteLater)
            x,y = self.parent.chartbox_splitter.chart.x()+(_x-menu.width()), self.parent.chartbox_splitter.chart.y()+50

            menu.move(QPoint(x, y))
            menu.show()

    
    def set_current_tool(self,tool_infor):
        tool,icon = tool_infor[0],tool_infor[1]
        self.current_tool = tool
        self.splitToolButton.change_item(icon)
        self.set_enable()
        self.sig_add_to_favorite.emit((self.current_tool,self.is_enabled,"draw_trenlines"))
        
    def set_enable(self):
        if self.splitToolButton.isChecked():
            self.is_enabled = True
        else:
            self.is_enabled = False
    
    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
