
from PySide6.QtCore import Signal, Qt,QRectF,QPointF
from PySide6.QtGui import QPainter
from atklip.app_utils.functions import mkBrush, mkPen

from .base_rectangle import BaseRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool


class Longposition(BaseRect):
    
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    
    def __init__(self, pos, size, centered=False, sideScalers=False,drawtool=None,is_short=False,is_long=False, **args):
        super().__init__(pos, size, centered, sideScalers,is_short,is_long, **args)

        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart
        
        self.has = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    'pen': None,
                    'brush': mkBrush((43, 106, 255, 40)),
                    'above_brush': mkBrush((0, 180, 90, 60)),
                    'under_brush': mkBrush((180, 0, 0, 60)),
                    "lock":True,
                    "setting": False,
                    "delete":True,}
        }
        
        right_handle = self.addScaleHandle([1, 0], [0, 0], lockAspect=True)
        self.addTranslateHandle([0, 0], [1, 0])
        self.addScaleHandle([0, 1], [0, 0], lockAspect=True)
        
        self.under_part = BaseRect([0,-self.size().y()], size,is_short=True)
        self.under_part.setParentItem(self)

        self.under_part.mouseDragEvent = self.mouseDragEvent
        self.under_part.addScaleHandle([1, 0], [0, 0], lockAspect=True,item=right_handle)
        self.under_part.addScaleHandle([0, 0], [0, 1], lockAspect=True)
        
        self.yoff = False
        self.xoff =False
        self.locked = False
        self.setbrushs()
        
    def setbrushs(self):
        self.setBrush(self.has["styles"]["above_brush"])
        self.under_part.setBrush(self.has["styles"]["under_brush"])
        self.under_part.update()
        self.update()
    
    def get_inputs(self):
        inputs =  {}
        return inputs
    
    def get_styles(self):
        styles =  {"above_brush":self.has["styles"]["above_brush"],
                    "under_brush":self.has["styles"]["under_brush"],
                    "lock":self.has["styles"]["lock"],
                    "delete":self.has["styles"]["delete"],
                    "setting":self.has["styles"]["setting"],}
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        print(self.get_styles())
        self.setbrushs()
        
    def set_lock(self,btn):
        if btn.isChecked():
            self.locked_handle()
        else:
            self.unlocked_handle()
            
    def locked_handle(self):
        self.yoff = True
        self.xoff = True
        self.locked = True

    def unlocked_handle(self):
        self.yoff = False
        self.xoff =False
        self.locked = False

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # if not self.boundingRect().contains(ev.pos()): 
            self.on_click.emit(self)
            self.finished = True
            self.drawtool.drawing_object =None
            ev.accept()
        ev.ignore()
        super().mouseClickEvent(ev)
    
    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # if not self.boundingRect().contains(ev.pos()): 
            self.on_click.emit(self)
            self.finished = True
            self.drawtool.drawing_object =None
            ev.accept()
        ev.ignore()        
        super().mouseReleaseEvent()
    
    def boundingRect(self):
        return QRectF(0, 0, self.state['size'][0]+self.under_part.state['size'][0], self.state['size'][1]+self.under_part.state['size'][1]).normalized()
    
    def paint(self, p:QPainter, opt, widget):
        super().paint(p, opt, widget)
        p.setPen(mkPen("green",width=1))
        p.drawLine(QPointF(0,1), QPointF(1,1))
