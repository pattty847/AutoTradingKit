from PySide6.QtCore import QObject,QEvent
from typing import TYPE_CHECKING

from atklip.app_utils import *

from .roi import FiboSpecialROI, DEFAULTS_COLOR, DEFAULTS_FIBO,\
TextBoxROI, SpecialROI, CustomLineSegmentROI
from .horizontal_line import Horizontal_line
from .horizontal_ray import Horizontal_ray, HorizontalRayNoHandle
from .brush_path import PathROI
from .rectangle import Rectangle
from .rotate_rectangle import RotateRectangle
from .fibo_retracement_1 import FiboROI
from .fibo_retracement_2 import FiboROI2
from .trend_lines import TrendlinesROI
from .vertical_line import Vertical_line
from .polylines import RangePolyLine
from .base_arrow import BaseArrowItem

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class DrawTool(QObject):
    def __init__(self, chart=None):
        super().__init__(chart)
        self.chart :Chart= chart
        
        self.custom_fibonacci_levels = None
        self.custom_colors_rect = None
        self.custom_colors_lines = None
        self.custom_colors_borders = None
        self.fibo_reverse = False
        
        self.num_fibo = 0
        self.num_fibo2 = 0
        self.num_trendline = 0
        self.num_vertical_line = 0
        self.num_dateprice_range = 0
        self.num_horizontal_line = 0
        self.num_horizontal_ray = 0
        self.num_path = 0
        self.num_rectangle = 0
        self.num_textbox = 0
        self.drawing_object = None
        self.draw_object_name = None
        
    def draw_trenlines(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = TrendlinesROI(positions=[[pos_x, pos_y],[pos_x, pos_y]], pen=("#2962ff"),drawtool=self)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_trendline += 1
        module_name = "Trend Line " + str(self.num_trendline)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        self.draw_object_name = "drawed_trenlines"

    def draw_verticallines(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj = Vertical_line(pos=pos_x, movable=True,angle=90,pen=mkPen("#2962ff"), chart=self.chart)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_vertical_line += 1
        module_name = "Vertital Line " + str(self.num_vertical_line)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None
    def get_position_crosshair(self):
        return self.chart.vLine.getXPos(), self.chart.hLine.getYPos()
    
    def get_position_mouse_on_chart(self, ev: QEvent):
        if self.chart.magnet_on:
            pos_x, pos_y = self.get_position_crosshair()
        else:
            ev_pos = ev.position()
            pos_x = self.chart.vb.mapSceneToView(ev_pos).x()
            pos_y = self.chart.vb.mapSceneToView(ev_pos).y()
        return pos_x, pos_y

    def draw_horizontal_line(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = Horizontal_line(parent=self.chart,pos=pos_y, movable=True,angle=0,pen=mkPen("#2962ff"), chart=self.chart)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_horizontal_line += 1
        module_name = "Horizontal Line " + str(self.num_horizontal_line)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None
    
    def draw_horizontal_ray(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj = Horizontal_ray(positions=[[pos_x, pos_y]], pen=("#2962ff"), chart=self.chart)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_horizontal_ray += 1
        module_name = "Horizontal Ray " + str(self.num_horizontal_ray)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None

    def draw_fibo(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj =FiboROI([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("green",width=1), fibo_level=self.custom_fibonacci_levels, color_rect=self.custom_colors_rect, color_line=self.custom_colors_lines, color_borders=self.custom_colors_borders,parent=self.chart.vb, main=self.chart)
    
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_fibo += 1
        module_name = "Fibo Retracement(I) " + str(self.num_fibo)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_fibo_retracement"

    def draw_fibo_2(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj =FiboROI2([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("green",width=1), 
                          parent=self.chart.vb, main=self.chart)

        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_fibo2 += 1
        module_name = "Fibo Retracement(II) " + str(self.num_fibo2)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_fibo_retracement_2"

    def draw_path(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =PathROI(positions=[(pos_x, pos_y), (pos_x, pos_y)], pen=mkPen("#2962ff"), drawtool=self)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_path += 1
        module_name = "Path " + str(self.num_path)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_path"

    def draw_rectangle(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =Rectangle([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("#2962ff",width=1),parent=self.chart.vb, drawtool=self)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Rectangle " + str(self.num_rectangle)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_rectangle"
    
    def draw_rotate_rectangle(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =RotateRectangle([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("#2962ff",width=1),parent=self.chart.vb, drawtool=self)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Rotate_rectangle " + str(self.num_rectangle)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_rotate_rectangle"

    def draw_text(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green",parent=self.chart.vb, main=self.chart)
        obj.setPos(pos_x, pos_y)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_textbox += 1
        module_name = "TextBox " + str(self.num_textbox)
        obj.setObjectName(module_name)
        self.draw_object_name = None
        uid_obj = self.chart.objmanager.add(obj)

    def draw_date_price_range(self, ev):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = RangePolyLine([pos_x, pos_y], [0, 0],drawtool=self, pen=mkPen('#2962ff'), movable=True)
        # obj.setPos(pos_x, pos_y)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "DatePrice Range " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        self.drawing_object = obj
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_date_price_range"
    
    def draw_up_arrow(self, ev):
        pos_x, pos_y = self.get_position_crosshair()
        obj = BaseArrowItem(chart=self.chart,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
        obj.setPos(pos_x, pos_y)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "ArrowItem " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_draw_up_arrow"
    
    def draw_down_arrow(self, ev):
        pos_x, pos_y = self.get_position_crosshair()
        obj = BaseArrowItem(chart=self.chart,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
        obj.setPos(pos_x, pos_y)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "ArrowItem " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_draw_down_arrow"
    
    def draw_arrow(self, ev):
        pos_x, pos_y = self.get_position_crosshair()
        obj = BaseArrowItem(chart=self.chart,angle=180, tipAngle=60, headLen=5, tailLen=2, tailWidth=2, pen=None, brush='red')
        obj.setPos(pos_x, pos_y)
        self.chart.addItem(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "ArrowItem " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_draw_down_arrow"