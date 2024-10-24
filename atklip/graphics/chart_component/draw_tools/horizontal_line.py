from atklip.graphics.pyqtgraph import InfiniteLine
from atklip.graphics.pyqtgraph import functions as fn
from PySide6 import QtCore
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal,QObject,Qt,QPointF


class Horizontal_line(InfiniteLine):
    
    on_click = Signal(QObject)
    change_pen_signal = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    
    def __init__(self, parent=None, chart=None, id=None, pos=None, angle=90, pen=None, movable=False, bounds=None,
                 hoverPen=None, label=None, labelOpts=None, span=(0, 1), markers=None, 
                 name=None):
        super(Horizontal_line,self).__init__(pos, angle, pen, movable, bounds, hoverPen, label, labelOpts, span, markers, name)
        self.chart = chart
        self.id = id
        self.chart = parent      # mapchart
        self.popup_setting_tool = None
        self.isSelected = False
        self.has = {
            "y_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id
        }
        # self.on_click.connect(self.chart.main.show_popup_setting_tool)
        self.change_pen_signal.connect(self.chart.yAxis.change_value)
        self.locked = False
        self.color = "#2962ff"
        self.width = 1
        self.style = Qt.SolidLine
        self.addMarker('o', size=6)
        self.change_pen_signal.emit(("#363a45",pos))
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)

    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            self.addMarker('o', size=6)
        else:
            self.isSelected = False
            self.clearMarkers()

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

    def get_pos_point(self):
        print(self.getYPos())
    
    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.price_axis.kwargs["horizontal_ray"].remove(self.id)
        self.deleteLater()

    def setPen(self, *args, **kwargs):
        """Set the pen for drawing the line. Allowable arguments are any that are valid
        for :func:`mkPen <pyqtgraph.mkPen>`."""
        if "color" in kwargs.keys():
            self.color = kwargs["color"]
        if "width" in kwargs.keys():
            self.width = kwargs["width"]
        if "style" in kwargs.keys():
            self.style = kwargs["style"]
        
        self.pen = fn.mkPen(*args, **kwargs)
        if not self.mouseHovering:
            self.currentPen = self.pen
            self.update()

    def mouseClickEvent(self, ev):
        self.sigClicked.emit(self, ev)
        if self.moving and ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.accept()
            self.setPos(self.startPosition)
            self.moving = False
            self.sigDragged.emit(self)
            self.sigPositionChangeFinished.emit(self)
        elif ev.button() == Qt.MouseButton.LeftButton:
            
            self.on_click.emit(self)
            
    def mouseDragEvent(self, ev):
        if self.movable and not self.locked and ev.button() == QtCore.Qt.MouseButton.LeftButton:
            if ev.isStart():
                self.moving = True
                self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                self.startPosition = self.pos()
            ev.accept()

            if not self.moving:
                return
            if self.chart.magnet_on:
                pos_y = self.chart.hLine.getYPos()
                self.setPos(QPointF((self.cursorOffset + self.mapToParent(ev.pos())).x(), pos_y))
            else:
                self.setPos(self.cursorOffset + self.mapToParent(ev.pos()))
            self.sigDragged.emit(self)
            if ev.isFinish():
                self.moving = False
                self.sigPositionChangeFinished.emit(self)
        self.change_pen_signal.emit(("#363a45",float(self.getYPos())))

    def hoverEvent(self, ev):
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            # self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            # self.setCursor(Qt.CursorShape.CrossCursor)
        
        if not self.isSelected:
            if (not ev.isExit()) and self.movable and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
                self.setMouseHover(True)
                self.addMarker('o', size=6)
            else:
                self.setMouseHover(False)
                self.clearMarkers()

    def setMouseHover(self, hover):
        ## Inform the item that the mouse is (not) hovering over it
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        if hover:
            # self.currentPen = self.hoverPen
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            # self.currentPen = self.pen
            self.setCursor(Qt.CursorShape.CrossCursor)
        self.update()
