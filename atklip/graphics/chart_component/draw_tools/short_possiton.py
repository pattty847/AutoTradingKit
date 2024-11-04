
from PySide6.QtCore import Signal, Qt,QRectF,QPointF
from PySide6.QtGui import QPainter
from atklip.app_utils.functions import mkBrush, mkPen
from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.TextItem import TextItem

from .base_rectangle import BaseRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool


class Shortposition(BaseRect):
    
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
                    'above_brush': mkBrush((180, 0, 0, 60)),
                    'under_brush': mkBrush((0, 180, 90, 60)),
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
        self.under_part.mouseClickEvent = self.mouseClickEvent
        self.under_part.mouseReleaseEvent = self.mouseReleaseEvent
        self.under_part.addScaleHandle([1, 0], [0, 0], lockAspect=True,item=right_handle)
        self.under_part.addScaleHandle([0, 0], [0, 1], lockAspect=True)
        
        
        self.textitem_up = TextItem("",color="#FFF")
        self.textitem_up.setParentItem(self)
        self.textitem_up.setAnchor((1,1))
        self.textitem_center = TextItem("",color="#7876")
        self.textitem_center.setParentItem(self)
        self.textitem_center.setAnchor((1,1))
        self.textitem_under = TextItem("",color="#0468")
        self.textitem_under.setParentItem(self.under_part)
        self.textitem_under.setAnchor((1,0))
        
        
        self.setbrushs()
    
    def update_text(self):
        h0 = self.handles[0]['item'].pos()
        h1 = self.handles[2]['item'].pos()
        diff = h1 - h0
        point0 = self.mapFromParent(Point(h0))
        point1 = self.mapFromParent(Point(h1))

        
        diff_y, percent,fsecs,ts = "244324",3423424,4324324,4234234
        
        
        html=f"""<div style="text-align: center"><span style="color: #d1d4dc; font-size: 11pt;">{diff_y} ({percent}%)</span><br><span style="color: #d1d4dc; font-size: 11pt;">{fsecs} bars, {ts}</span></div>"""
        
        
        self.textitem_up.setHtml(html)
        self.textitem_center.setHtml(html)
        self.textitem_under.setHtml(html)

        r = self.textitem_up.textItem.boundingRect()
        tl = self.textitem_up.textItem.mapToParent(r.topLeft())
        br = self.textitem_up.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem_up.anchor
        
        _pointf = Point(h1.x() - diff.x()/2, h1.y())
        _x = _pointf.x() +r.width()/2
        _y = _pointf.y() + offset.y()/2
        self.textitem_up.setPos(Point(_x,_y))
        
        
        r = self.textitem_center.textItem.boundingRect()
        tl = self.textitem_center.textItem.mapToParent(r.topLeft())
        br = self.textitem_center.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem_center.anchor
        
        _pointf = Point(h1.x() - diff.x()/2, h0.y())
        _x = _pointf.x() +r.width()/2
        _y = _pointf.y() + offset.y()/8
        self.textitem_center.setPos(Point(_x,_y))
        
        
        h0 = self.under_part.handles[0]['item'].pos()
        h1 = self.under_part.handles[1]['item'].pos()
        diff = h1 - h0
        point0 = self.mapFromParent(Point(h0))
        point1 = self.mapFromParent(Point(h1))
                 
        r = self.textitem_under.textItem.boundingRect()
        tl = self.textitem_under.textItem.mapToParent(r.topLeft())
        br = self.textitem_under.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem_under.anchor
        _pointf = Point(h1.x() - diff.x()/2, h1.y())
        _x = _pointf.x() +r.width()/2
        _y = _pointf.y() - offset.y()/2
        self.textitem_under.setPos(Point(_x,_y))
        

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
        self.setbrushs() 

    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)
        if ev.button() == Qt.MouseButton.LeftButton:
            self.drawtool.drawing_object =None 
    
    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent()
        if ev.button() == Qt.MouseButton.LeftButton:
            self.drawtool.drawing_object =None  
    
    def boundingRect(self):
        return QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
    
    def paint(self, p:QPainter, opt, widget):
        super().paint(p, opt, widget)
        p.setPen(mkPen("red",width=1))
        p.drawLine(QPointF(0,1), QPointF(1,1))
        self.update_text()
        
    def mouseDragEvent(self, ev, axis=None):
        self.setSelected(True)
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.chart.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            return super().mouseDragEvent(ev)
        elif self.locked:
            ev.ignore()
        ev.ignore()