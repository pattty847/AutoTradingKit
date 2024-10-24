from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QColor

from .roi import SpecialROI, BaseHandle


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool
    
class Rectangle(SpecialROI):
    on_click = Signal(QObject)
    draw_rec = Signal()

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)


    def __init__(self, pos, size=..., angle=0,id=None, invertible=False, maxBounds=None, \
        snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, \
            pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, \
                rotatable=True, resizable=True, removable=False, aspectLocked=False,drawtool=None):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, \
            translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen,\
                movable, rotatable, resizable, removable, aspectLocked)
        
        self.drawtool:DrawTool= drawtool
        self.indicator_name = None
        self.isSelected = False
        self.id = id
        
        self.has = {
            "name": "rectangle",
            "type": "drawtool",
            "id": id
        }

        self.addScaleHandle([1, 0.5], [0, 0.5])
        self.addScaleHandle([0, 0.5], [1, 0.5])

        ## handles scaling vertically from opposite edge
        self.addScaleHandle([0.5, 0], [0.5, 1])
        self.addScaleHandle([0.5, 1], [0.5, 0])
        ## handles scaling both vertically and horizontally
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([0, 1], [1, 0])
        self.addScaleHandle([1, 0], [0, 1])
        self.addScaleHandle([1, 1], [0, 0])

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)

        self.lastMousePos = pos
        self.finished = False
        # self.on_click.connect(self.drawtool.show_popup_setting_tool)
        # self.on_click.connect(self.get_pos_point)

    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            self.setSelected(True)
            self.change_size_handle(3)
        else:
            self.isSelected = False
            self.setSelected(False)
            self.change_size_handle(4)
       
    def hoverEvent(self, ev: QtCore.QEvent):
        hover = False
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            # self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            # self.setCursor(Qt.CursorShape.CrossCursor)
                
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
        return h

    def setPoint(self,pos_x, pos_y):
        if not self.finished:
            if self.drawtool.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()
            self.state['size'] = [pos_x-self.state['pos'][0], pos_y-self.state['pos'][1]]
            self.stateChanged()
    
    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name

    def change_type(self, type_):
        if type_ == "SolidLine":
            self.currentPen.setStyle(Qt.PenStyle.SolidLine)
        elif type_ == "DashLine":
            self.currentPen.setStyle(Qt.PenStyle.DashLine)
        elif type_ == "DotLine":
            self.currentPen.setStyle(Qt.PenStyle.DotLine)
        self.setPen(self.currentPen)
        self.update()

    def change_width(self, width):
        self.currentPen.setWidth(width)
        self.setPen(self.currentPen)
        self.update()

    def change_color(self, color):
        if isinstance(color, (tuple, list)):
            r, g, b = color[0], color[1], color[2]
            color = QColor(r, g, b)
        elif isinstance(color, str):
            color = QColor(color)
        self.currentPen.setColor(color)
        self.setPen(self.currentPen)
        self.update()

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()

    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name

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
        self.price_axis.kwargs["horizontal_ray"].remove(self.id)
        self.deleteLater()


    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
    
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

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]

    def paint(self, p, opt, widget):
        # Note: don't use self.boundingRect here, because subclasses may need to redefine it.
        r = QtCore.QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        "Custom màu viền và nền ở đây...."
        p.setPen(self.currentPen)
        p.setBrush(QColor(255,152,0,40))
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())
        #p.fillRect(r, QColor(255,152,0,40))
        p.drawRect(0, 0, 1, 1)

    def mouseDragEvent(self, ev, axis=None, line=None):
        self.setSelected(True)
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.drawtool.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            # r_out = self.boundingRect().adjusted(-4,-4,4,4)
            # r_in = self.boundingRect().adjusted(4,4,-4,-4)
            # if r_out.contains(ev.pos()) and not r_in.contains(ev.pos()):
            self._moveStarted()
            return super().mouseDragEvent(ev)
            
        elif self.locked:
            ev.ignore()
        ev.ignore()
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if not self.boundingRect().contains(ev.pos()):
                ev.accept()
                self.on_click.emit(self)
            self.finished = True
            self.drawtool.drawing_object =None
        ev.ignore()

        
       