from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Signal, QPointF, Qt, QRectF, QCoreApplication
from PySide6.QtGui import QPainter, QColor
from atklip.graphics.pyqtgraph import mkPen
from atklip.graphics.pyqtgraph.Point import Point

from .roi import SpecialROI, BaseHandle, _FiboLineSegment
from .base_textitem import BaseTextItem
from atklip.app_utils.calculate import cal_line_price_fibo

DEFAULTS_FIBO = [1.0, 0.786, 0.618, 0.5, 0.382, 0.236, 0.0]
DEFAULTS_COLOR = [(120,123,134,200),(242,54,69,200),(255,152,0,200),(76,175,80,200),(8,153,129,200),(0,188,212,200),(120,123,134,200),(41, 98, 255,200),(242, 54, 69, 200),(156,39,176,200),(233, 30, 99,200),(206,147,216,200),(159,168,218,200),(255,204,128,200),
                        (229,115,115,200),(244,142,177,200),(66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200)]
LEFT_FAR_TIMESTAMP = 1562990041
RIGHT_FAR_TIMESTAMP = 1783728000


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool

class FiboROI(SpecialROI):
    on_click = Signal(object)
    draw_rec = Signal()


    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    signal_update_text = Signal(list)

    def __init__(self, pos, size=..., angle=0, invertible=True, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, rotatable=True, resizable=True, removable=False, aspectLocked=False, drawtool=None, fibo_level=None, color_rect=None, color_line=None, color_borders=None,):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked)
        #self.generate_lines()
        self.id = None
        self.has = {
            "x_axis_show":False,
            "name": "fibo retracements",
            "type": "fibo_1",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    "lock":True,
                    "setting": True,
                    "delete":True,}
        }
        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart  # plot mapchart
        self.vb = self.chart.vb
        

        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 1], [0, 0])
        self.segments = []
        self.isSelected = False
        self.popup_setting_tool = None
       
        self.precision = self.chart._precision


        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)
        
        self.signal_update_text.connect(self.update_text_percentage)

        self.last_left_pos = None
        self.last_right_pos = None
        self.reverse = False #if self.chart.fibo_reverse else False
        self.movable = movable
        self.locked = False
        self.trend_line = True
        self.extend_left = False
        self.extend_right = False
        # self.installEventFilter(self)
        self.temp_config = {}
        self.list_lines = []
        self.fibonacci_levels = DEFAULTS_FIBO 
        self.colors_rect = [QColor(242,54,69,40),QColor(242,54,69,40),QColor(255,152,0,40),QColor(76,175,80,40),QColor(8,153,129,40),QColor(0,188,212,40),QColor(120,123,134,40),QColor(41, 98, 255,40),QColor(242, 54, 69,40),QColor(156,39,176,40),QColor(233, 30, 99,40),QColor(61,90,254,40),QColor(230,81,0,40),QColor(255,23,68,40),QColor(255,64,129,40),QColor(170,0,255,40)]
                        # xam , do, cam, xanh chuoi, xanh la dam, xanh duong, xanh lam dam, do nhat , tim rgb(156 39 176)
        self.colors_lines = DEFAULTS_COLOR
        self.colors_borders = [(120,123,134,0),(242,54,69,0),(255,152,0,0),(76,175,80,0),(8,153,129,0),(0,188,212,0),(120,123,134,0),(41, 98, 255,0),(242, 54, 69, 0),(156,39,176,0),(233, 30, 99,0),(206,147,216,0),(159,168,218,0),(255,204,128,0),
                        (229,115,115,0),(244,142,177,0),(66, 135, 245,0), (66, 135, 245,0), (66, 135, 245,0), (66, 135, 245,0), (66, 135, 245,0), (66, 135, 245,0)]
        
        if fibo_level:
            self.fibonacci_levels = fibo_level
        if color_line:
            self.colors_lines = color_line
        if color_borders:
            self.colors_borders = color_borders
        if color_rect:
            self.colors_rect = color_rect
        self.counts = len(self.fibonacci_levels)

        while self.counts > len(self.colors_lines):
            self.colors_lines.append(DEFAULTS_COLOR[-1])
        if self.counts > len(self.colors_borders):
            self.colors_borders = self.colors_lines
        while self.counts > len(self.colors_rect):
            adding = self.colors_rect[-1]
            self.colors_rect.append(adding)
        for i in range(self.counts):
            target = BaseTextItem("", anchor=(1, 0))
            self.list_lines.append(target)
            target.setParentItem(self)
        
        try:
            self.addSegment(self.handles[0]['item'], self.handles[1]['item'])
        except:
            import traceback
            traceback.print_exc()
        self.lastMousePos = pos
        self.finished = False
        self.first_click = False
        self.drawed = False
        # self.on_click.connect(self.chart.show_popup_setting_tool)

    def get_inputs(self):
        inputs =  {}
        return inputs
    
    def get_styles(self):
        styles =  {
                    "lock":self.has["styles"]["lock"],
                    "delete":self.has["styles"]["delete"],
                    "setting":self.has["styles"]["setting"],}
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        self.update()


    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            # self.setSelected(True)
            self.change_size_handle(3)
        else:
            self.isSelected = False
            # self.setSelected(False)
            self.change_size_handle(4)

    def setSelected(self, s):
        QtWidgets.QGraphicsItem.setSelected(self, s)
        #print "select", self, s
        if s:
            [h['item'].show() for h in self.handles]
            [h.show() for h in self.segments]

        else:
            [h['item'].hide() for h in self.handles]
            [h.hide() for h in self.segments]

    def hoverEvent(self, ev: QtCore.QEvent):
        hover = False
        
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            if not self.locked:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            if not self.isMoving:
                hover = False
                self.setCursor(Qt.CursorShape.CrossCursor)
        
                
        if not self.isSelected:
            if hover:
                self.setSelected(True)
                ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)
    
    def addHandle(self, info, index=None):
        ## If a Handle was not supplied, create it now
        if 'item' not in info or info['item'] is None:
            h = BaseHandle(self.handleSize, typ=info['type'], pen=self.handlePen,
                       hoverPen=self.handleHoverPen, parent=self)
            info['item'] = h
            # info["yoff"] = True
        else:
            h = info['item']
            # info["yoff"] = True
            if info['pos'] is None:
                info['pos'] = h.pos()
        h.setPos(info['pos'] * self.state['size'])

        ## connect the handle to this ROI
        #iid = len(self.handles)
        h.connectROI(self)
        if index is None:
            self.handles.append(info)
        else:
            self.handles.insert(index, info)
        
        h.setZValue(self.zValue()+1)
        self.stateChanged()
        h.mousePressEvent = self.mousePressEvent
        return h
    
    def update_text_percentage(self, data):
        i, price, x, direct = data[0], data[1], data[2], data[3]
        pointf = self.mapFromParent(Point(x,price))
        # y_line_pointf = mapFromParent.y()
        # x_line_pointf = mapFromParent.x()
        text:BaseTextItem = self.list_lines[i]
        text.updatePos(pointf)
        if direct == 1:
            text.percent = self.fibonacci_levels[i]
            text.setColor(self.colors_lines[self.counts - i - 1])
            text.setText(f"{text.percent} ({str(price)})  ")
        else:
            text.percent = self.fibonacci_levels[self.counts - i - 1] 
            text.setColor(self.colors_lines[i])
            text.setText(f"{text.percent} ({str(price)})  ")


    def setPoint(self,pos_x, pos_y):
        if not self.finished:
            if self.chart.magnet_on:
                pos_x, pos_y = self.chart.get_position_crosshair()
            if self.reverse:
                self.movePoint(0, QPointF(pos_x, pos_y))
            else:
                self.movePoint(-1, QPointF(pos_x, pos_y))
            self.stateChanged()
    
    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name

    def change_type(self, type_):
        self.setPen(style=type_)
        self.update()

    def change_width(self, width):
        self.setPen(width=width)
        self.update()

    def change_color(self, color):
        #print(318, "change_color", color)
        r, g, b = color[0], color[1], color[2]
        color = QColor(r, g, b)
        self.setPen(color=color)
        self.update()

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()

    def get_fibo_level(self):
        return self.fibonacci_levels
    
    def get_fibo_color(self):
        return self.colors_lines
    
    def get_pos_point(self):
        pos = self.state["pos"]
        size = self.state["size"]
        if pos.x() < pos.x() + size[0]:
            first_point = [pos.x(), pos.y()]
            second_point = [pos.x() + size[0], pos.y() + size[1]]
        else:
            second_point = [pos.x(), pos.y()]
            first_point = [pos.x() + size[0], pos.y() + size[1]]
        
        return first_point, second_point
    
    def delete(self):
        "xoa hien thi gia truc y"
        #self.price_axis.kwargs["horizontal_ray"].remove(self.id)
        self.deleteLater()

    def addSegment(self, h1, h2, index=None):
        seg = _FiboLineSegment(handles=(h1, h2), pen=mkPen(color="#9598a1",width= 1,style= Qt.DashLine), hoverPen=self.hoverPen,
                               parent=self, movable=False)
        if index is None:
            self.segments.append(seg)
        else:
            self.segments.insert(index, seg)
        seg.sigClicked.connect(self.segmentClicked)
        seg.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        seg.setZValue(self.zValue()+1)
        # for h in seg.handles:
            # h['item'].setDeletable(True)
            # h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | Qt.MouseButton.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if not self.boundingRect().contains(ev.pos()):
                ev.accept()
                self.on_click.emit(self)
            self.finished = True
            self.chart.drawtool.drawing_object =None
        ev.ignore()
    
    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        if ev is not None:
            pos = segment.mapToParent(ev.pos())
        elif pos is None:
            raise Exception("Either an event or a position must be given.")
        # h2 = segment.handles[1]['item']
        print(598, pos, self)
        if not self.finished:
            self.finished = True
            self.chart.drawtool.drawing_object =None
        self.on_click.emit(self)

    def set_lock(self,btn):
        print(btn,btn.isChecked())
        if btn.isChecked():
            self.locked_handle()
        else:
            self.unlocked_handle()
            
    def locked_handle(self):
        self.yoff = True
        self.xoff = True
        self.locked = True
        self.change_size_handle(2)

    def unlocked_handle(self):
        self.yoff = False
        self.xoff =False
        self.locked = False
        self.change_size_handle(4)
    
    def change_size_handle(self, size):
        for handle in self.endpoints:
            handle.change_size_handle(size)

    def extend_to_left(self, checked):
        pos = self.state["pos"]
        size = self.state["size"]
        if checked:
            self.extend_left = True
            first_time = pos.x()
            second_time = pos.x() + size.x()
            first_price = pos.y()
            second_price = pos.y() + size.y()
            if self.last_left_pos is None:
                if first_time > second_time:
                    self.last_left_pos = second_time
                    print(715, "left extend 1")
                    self.movePoint(1, QPointF(LEFT_FAR_TIMESTAMP, second_price))
                else:
                    print(718, "left extend 0", first_price, first_time)
                    self.last_left_pos = first_time
                    self.movePoint(0, QPointF(LEFT_FAR_TIMESTAMP, first_price))
            
        else:
            self.extend_left = False
            if self.last_left_pos:
                first_time = pos.x()
                second_time = pos.x() + size.x()
                first_price = pos.y()
                second_price = pos.y() + size.y()
                if first_time > second_time:
                    self.movePoint(1, QPointF(self.last_left_pos, second_price))
                else:
                    self.movePoint(0, QPointF(self.last_left_pos, first_price))
                self.last_left_pos = None

    def extend_to_right(self, checked):
        pos = self.state["pos"]
        size = self.state["size"]
        if checked:
            self.extend_right = True
            first_time = pos.x()
            second_time = pos.x() + size.x()
            first_price = pos.y()
            second_price = pos.y() + size.y()
            if self.last_right_pos is None:
                if first_time < second_time:
                    self.last_right_pos = second_time
                    self.movePoint(1, QPointF(RIGHT_FAR_TIMESTAMP, second_price))
                else:
                    self.last_right_pos = first_time
                    self.movePoint(0, QPointF(RIGHT_FAR_TIMESTAMP, first_price))
            
        else:
            self.extend_right = False
            if self.last_right_pos:
                first_time = pos.x()
                second_time = pos.x() + size.x()
                first_price = pos.y()
                second_price = pos.y() + size.y()
                if first_time < second_time:
                    self.movePoint(1, QPointF(self.last_right_pos, second_price))
                else:
                    self.movePoint(0, QPointF(self.last_right_pos, first_price))
                self.last_right_pos = None

    def mouseDragEvent(self, ev, axis=None, line=None):
        self.setSelected(True)
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.chart.vb.mouseDragEvent(ev, axis)

        if not self.locked and line:
            return super().mouseDragEvent(ev)
        elif self.locked and line:
            ev.ignore()
        ev.ignore()
    
    def remove(self):
        for item in self.list_lines:
            # print(156, "remove", item)
            self.chart.removeItem(item)
        self.chart.removeItem(self)

    def hide(self):
        super().hide()
        for item in self.list_lines:
            item.hide()

    def show(self):
        super().show()
        for item in self.list_lines:
            item.show()

    def boundingRect(self):
        y_size = self.state['size'][1]
        top = -y_size*self.fibonacci_levels[0] + y_size
        height = y_size
        if self.fibonacci_levels[0] > 1:
            height += y_size*(self.fibonacci_levels[0]-1)
        if self.fibonacci_levels[-1] < 0:
            height += y_size*abs(self.fibonacci_levels[-1])
        # print("height", height, y_size)
        
        return QRectF(0, top, self.state['size'][0], height).normalized()
    
    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
    
    def paint(self, p: QPainter, opt, widget):
        # print(576, self.state)
        # max_percent = max(self.fibonacci_levels)
        # min_percent = min(self.fibonacci_levels)
        r = self.boundingRect()
        parentbound = self.parentBounds()
        f = self.precision
        unit = 1/(self.fibonacci_levels[0]-self.fibonacci_levels[-1])
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())
        # h0 = self.handles[0]['item']
        # h1 = self.handles[1]['item']
        # diff = h1.pos() - h0.pos()
        # di xuong
        if self.size().y() < 0: # or (self.size().y() > 0 and self.reverse):
            # print(556, self.size().y(), self.reverse)
            # direction = 1 if self.reverse  else -1
            top = self.mapToView(Point(0,0)).y()
            bot = top + self.size().y()
            for i in range(self.counts):
                price = round(cal_line_price_fibo(top, bot, self.fibonacci_levels[self.counts - i - 1], -1),f)
                self.signal_update_text.emit([i, price, parentbound.x(), -1])
                p.setPen(mkPen(self.colors_lines[i],width=1))
                y_line_pointf = (self.fibonacci_levels[self.counts-i-1]-self.fibonacci_levels[-1])*unit
                p.drawLine(QPointF(0,y_line_pointf), QPointF(1,y_line_pointf))
                if i >0:
                    pre_y_line_pointf = (self.fibonacci_levels[self.counts-i]-self.fibonacci_levels[-1])*unit
                    p.setPen(mkPen(self.colors_borders[i]))
                    p.setBrush(self.colors_rect[i]) #QBrush(mkBrush(color))
                    rect =  QRectF(0,y_line_pointf, 1, pre_y_line_pointf - y_line_pointf)
                    p.fillRect(rect, self.colors_rect[i])
        # di len
        else:
            # direction = -1 if self.reverse else 1
            bot = self.mapToView(Point(0,0)).y()
            top = bot + self.size().y()
            for i in range(self.counts):
                price = round(cal_line_price_fibo(top, bot, self.fibonacci_levels[i]),f)
                self.signal_update_text.emit([i, price, parentbound.x(), 1])
                p.setPen(mkPen(self.colors_lines[i],width=1))
                y_line_pointf = (-self.fibonacci_levels[self.counts-i-1]+self.fibonacci_levels[0])*unit
                p.drawLine(QPointF(0,y_line_pointf), QPointF(1,y_line_pointf))
                if i >0:
                    pre_y_line_pointf = (-self.fibonacci_levels[self.counts-i]+self.fibonacci_levels[0])*unit
                    p.setPen(mkPen(self.colors_borders[i]))
                    p.setBrush(self.colors_rect[i]) #QBrush(mkBrush(color))
                    rect =  QRectF(0,pre_y_line_pointf, 1, -pre_y_line_pointf+y_line_pointf)
                    p.fillRect(rect, self.colors_rect[i])
        # p.end()
    # def keyPressEvent(self, event: QKeyEvent) -> None:
    #     print(325, "keyPressEvent", event)
    #     return super().keyPressEvent(event)

#########################################################
