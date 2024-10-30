from typing import TYPE_CHECKING

from atklip.gui.qfluentwidgets.components.container import HWIDGET,VWIDGET
from atklip.gui.components import ScrollInterface,TextButton,MovingWidget,PivotInterface, MovingParentWG
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.components.setting_element import PeriodEdit,MultiDevEdit,PriceEdit,ColorEditDrawTool,WidthEditDrawTool,StyleEditDrawTool,\
SourceEdit,TypeEdit,MaTypeEdit,MaIntervalEdit

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize, Qt,QPointF

from atklip.gui.qfluentwidgets.components.widgets import SubtitleLabel
from atklip.gui.components._pushbutton import _PushButton
from atklip.gui.qfluentwidgets.common import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.components.widgets.button import TransparentDropDownPushButton
from atklip.gui.qfluentwidgets.components.widgets.command_bar import CommandBar, CommandBarView
from atklip.gui.qfluentwidgets.components.widgets.flyout import Flyout, FlyoutAnimationType
from atklip.gui.qfluentwidgets.components.widgets.menu import CheckableMenu, MenuIndicatorType, RoundMenu
from atklip.gui.components import Tradingview_Button,Lock_Unlock_Button


if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget


class PopUpSettingMenu(CommandBarView):
    sig_mouse_move = Signal(tuple)
    def __init__(self, parent:QWidget=None, tool=None):
        super().__init__(parent)
        self._parent = parent
        self.tool = tool
        self.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.bar.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.hBoxLayout.setSpacing(0)
        self.bar.setSpacing(0)
                       
        self.moving_btn = MovingParentWG(self._parent,self)
        self.moving_btn.setFixedSize(30,30)
        self.hBoxLayout.insertWidget(0,self.moving_btn,0)
        
        inputs = self.tool.has.get("inputs")
        styles = self.tool.has.get("styles")
                
        if styles:
            for _input in list(styles.keys()):
                    if "pen" in _input:
                        pen = ColorEditDrawTool(self,self.tool, _input)
                        self.add_btn(pen)
                    elif "brush" in _input:
                        brush = ColorEditDrawTool(self,self.tool, _input)
                        self.add_btn(brush)
                        
                    elif "width" in _input:
                        width = WidthEditDrawTool(self,self.tool, _input)
                        self.add_btn(width)

                    elif "style" in _input:
                        style = StyleEditDrawTool(self,self.tool, _input)
                        self.add_btn(style)
                    
                    elif "lock" in _input:
                        if styles[_input] == True:
                            lock = Lock_Unlock_Button(FIF.CYCLEBIN,self)
                            lock.setFixedSize(30,30)
                            # delete.clicked.connect(self.delete_tool)
                            self.add_btn(lock)
                    
                    elif "setting" in _input:
                        if styles[_input] == True:
                            setting = Tradingview_Button(FIF.SETTING,self)
                            setting.setFixedSize(30,30)
                            # setting.clicked.connect(self.delete_tool)
                            self.add_btn(setting)
                        
                    elif "delete" in _input:
                        if styles[_input] == True:
                            delete = Tradingview_Button(FIF.CYCLEBIN,self)
                            delete.setFixedSize(30,30)
                            delete.clicked.connect(self.delete_tool)
                            self.add_btn(delete)

        self.resizeToSuitableWidth(self.moving_btn)
    
    def delete_tool(self):
        self._parent.remove_item(self.tool)
        self.deleteLater()
    
    def add_btn(self,btn):
        self.addWidget(btn)
        self.resizeToSuitableWidth(self.moving_btn)
    
    def delete(self,ev):
        try:
            ev_pos = ev.position()
        except:
            ev_pos = ev.pos()
        _rect = QRectF(self.x(),self.y(),self.width(),self.height())
        if not _rect.contains(QPoint(ev_pos.x(),ev_pos.y())):
            self.deleteLater()
    
    def resizeToSuitableWidth(self,moving_btn):
        self.bar.resizeToSuitableWidth()
        self.setFixedWidth(self.suitableWidth()+moving_btn.width())
    
    def createCheckableMenu(self, pos=None):
        createTimeAction = Action(FIF.CALENDAR, self.tr('Create Date'), checkable=True)
        shootTimeAction = Action(FIF.CAMERA, self.tr('Shooting Date'), checkable=True)
        modifiedTimeAction = Action(FIF.EDIT, self.tr('Modified time'), checkable=True)
        nameAction = Action(FIF.FONT, self.tr('Name'), checkable=True)

        ascendAction =  Action(FIF.UP, self.tr('Ascending'), checkable=True)
        descendAction =  Action(FIF.DOWN, self.tr('Descending'), checkable=True)
        
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)

        menu.addActions([
            createTimeAction, shootTimeAction,
            modifiedTimeAction, nameAction
        ])
        menu.addSeparator()
        menu.addActions([ascendAction, descendAction])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu



