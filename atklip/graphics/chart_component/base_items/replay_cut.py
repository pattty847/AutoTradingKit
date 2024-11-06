from typing import Dict, Tuple, List,TYPE_CHECKING
import numpy as np

from PySide6.QtCore import Signal, QRect, QRectF, QPointF,QThreadPool,Qt,QLineF,QCoreApplication
from PySide6.QtGui import QPainter, QPicture,QPainterPath,QColor
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget
from atklip.graphics.pyqtgraph import mkPen, GraphicsObject, mkBrush

from atklip.app_utils.functions import mkColor

draw_line_color = '#2962ff'

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_chart import SubChart
    
class ReplayObject(GraphicsObject):
    sigPlotChanged = Signal(object)
    def __init__(self,chart) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.chart: Chart = chart
        self.has = {
            "name": "rectangle",
            "type": "drawtool",
            "id": id
        }
        self.picture = QPicture()
        self.colorline = 'white'
        
        self._x,self._y = self.chart.get_position_crosshair()
        self.x_left,self.x_right = float(self.chart.xAxis.range[0]),float(self.chart.xAxis.range[1])
        self.y_bottom,self.y_top = float(self.chart.yAxis.range[0]),float(self.chart.yAxis.range[1])
        
        self.setAcceptHoverEvents(True)
        
    def paint(self, p: QPainter, *args) -> None:
        
        # print(QRectF(self._x, self.y_top, self.x_right-self._x, self.y_top-self.y_bottom))
        self._x, self._y = self.chart.get_position_crosshair()
        self.x_left,self.x_right = float(self.chart.xAxis.range[0]),float(self.chart.xAxis.range[1])
        self.y_bottom,self.y_top = float(self.chart.yAxis.range[0]),float(self.chart.yAxis.range[1])
        
        vr = self.viewRect()
        rect = QRectF(self._x, self.y_bottom, self.x_right-self._x, self.y_top-self.y_bottom)
        print(vr,rect)
        
        p.setPen(mkPen('#2962ff'))
        # p.setBrush(mkBrush((43, 106, 255, 40)))
        # p.drawRect(QRectF(self._x, self.y_bottom, self.x_right-self._x, self.y_top-self.y_bottom))
        p.fillRect(rect,mkColor((43, 106, 255, 40)))
        p.drawLine(QPointF(self._x, self.y_top),QPointF(self._x, self.y_bottom))
        

    def boundingRect(self) -> QRectF:
        return QRectF(self._x, self.y_top, self.x_right-self._x, self.y_top-self.y_bottom)
    
    def setPoint(self,pos_x, pos_y):
        self._x, self._y = self.chart.get_position_crosshair()
        self.x_left,self.x_right = float(self.chart.xAxis.range[0]),float(self.chart.xAxis.range[1])
        self.y_bottom,self.y_top = float(self.chart.yAxis.range[0]),float(self.chart.yAxis.range[1])
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def hoverEnterEvent(self, ev):
        ev.accept()
        
    def hoverLeaveEvent(self, ev):
        self.brush = mkBrush('g')
        self.update()
        ev.accept()

        """ _summary_
    mousePressEvent(ev): Sự kiện này được gọi khi người dùng nhấn chuột trái, phải hoặc giữa trên GraphicsObject.

    mouseMoveEvent(ev): Sự kiện này được gọi khi chuột di chuyển trên GraphicsObject.

    mouseReleaseEvent(ev): Sự kiện này được gọi khi người dùng nhả chuột trái, phải hoặc giữa trên GraphicsObject.

    wheelEvent(ev): Sự kiện này được gọi khi người dùng cuộn chuột trên GraphicsObject.

    keyPressEvent(ev): Sự kiện này được gọi khi người dùng nhấn một phím trên bàn phím khi GraphicsObject đang được chọn.

    keyReleaseEvent(ev): Sự kiện này được gọi khi người dùng nhả phím trên bàn phím khi GraphicsObject đang được chọn.
        _extended_summary_
        """



