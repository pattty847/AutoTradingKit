
from PySide6 import QtCore
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QPainter, QPainterPath, QColor
from atklip.graphics.pyqtgraph import functions as fn, ROI
from atklip.graphics.pyqtgraph.Point import Point

from .custom_roi import CustomLineSegmentROI, MyHandle


class TrendlinesROI(CustomLineSegmentROI):
    """ Draw a trend line """
    on_click = Signal(QObject)

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    
    def __init__(self, positions=None, pen=("#eaeaea"), chart=None):
        super().__init__(positions=positions,pen=pen, resizable=False)  # resizable Shift modifiers
        self.chart = chart
        self.popup_setting_tool = None
        self.on_click.connect(self.chart.change_line_color_on_click)
        self.on_click.connect(self.chart.main.show_popup_setting_tool)
        self.id = None

        self.isSelected = False
        self.drawing = True
        self.extend_left = False
        self.extend_right = False
        self.locked = False
        self.finished = False
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)
        self.chart.mousepossiton_signal.connect(self.setPoint)


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
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
                hover=True
                
            for btn in [QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton, QtCore.Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
        
        if not self.isSelected:
            if self.chart.draw_object: return
            if hover:
                self.setSelected(True)
                ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
                
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)

    # def setMouseHover(self, hover):
    #     if hover:
    #         self.setCursor(Qt.CursorShape.PointingHandCursor)
    #     else:
    #         self.setCursor(Qt.CursorShape.CrossCursor)
    #     self.update()

    def addPoint(self, point):
        self.addFreeHandle(point)
        self.stateChanged(finish=True)
        self.update()

    # def clicked_chart(self, ev):
    #     pos_x, pos_y = self.chart.get_position_mouse_on_chart(ev)
    #     if self.drawing:
    #         self.setPoint([self.chart.draw_object, pos_x, pos_y])
    #         self.chart.draw_object =None
    #         self.finished = True
    

    def setPoint(self, data):
        if not self.finished and data[0]=="drawed_trenlines":
            if self.chart.magnet_on:
                pos_x, pos_y = self.chart.get_position_crosshair()
            else:
                pos_x, pos_y = self.chart.get_position_crosshair()
                pos_y = data[2]
            point = Point(pos_x, pos_y)
            self.last_point = point
            lasthandle = self.handles[-1]['item']
            self.removeHandle(lasthandle)
            self.addPoint(self.last_point)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    

    def get_start_stop_points(self):
        point1 = self.listPoints()[0]
        point2 = self.listPoints()[-1]
        #res.append((point.x(), point.y()))
        return point1.x(),point2.x()

    def get_pos_point(self):
        res = []
        list_point = self.listPoints()
        for point in list_point:
            res.append((point.x(), point.y()))
        return res
    
    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.price_axis.kwargs["horizontal_ray"].remove(self.id)
        self.deleteLater()

    def addHandle(self, info, index=None):
        ## If a Handle was not supplied, create it now
        if 'item' not in info or info['item'] is None:
            h = MyHandle(self.handleSize, typ=info['type'], pen=self.handlePen,
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
        # h.mousePressEvent = self.mousePressEvent
        # h.
        return h
    
    def mousePressEvent(self, ev):
        print("mousePressEvent")
        if ev.button() == Qt.MouseButton.LeftButton:
            self.chart.draw_object =None
            self.finished = True
            self.on_click.emit(self)
        ev.ignore()

    def update_trend_line(self, mapchart_trading, setting_tool_menu=None):
        if setting_tool_menu is None:
            pass

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

    def mouseDragEvent(self, ev, axis=None, line=None):
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.main.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            return super().mouseDragEvent(ev)
        elif self.locked:
            ev.ignore()
        ev.ignore()

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.RightButton and self.isMoving:
            ev.accept()
            self.cancelMove()
        if ev.button() == Qt.MouseButton.RightButton and self.contextMenuEnabled():
            self.raiseContextMenu(ev)
            ev.accept()
        elif self.acceptedMouseButtons() & ev.button():
            ev.accept()
            self.sigClicked.emit(self, ev)
        elif ev.button() == Qt.MouseButton.LeftButton:
            # ev.ignore()
            self.on_click.emit(self)
        else:
            ev.ignore()
            
    def mouseHandleReleaseEvent(self, ev):
        print("zooo day___release___",ev)
        if ev.button() == Qt.MouseButton.LeftButton:
            self.parentItem().on_click.emit(self)
        ev.accept()

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
        
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def getState(self):
        state = ROI.getState(self)
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = ROI.saveState(self)
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        ROI.setState(self, state)
        p1 = [state['points'][0][0]+state['pos'][0], state['points'][0][1]+state['pos'][1]]
        p2 = [state['points'][1][0]+state['pos'][0], state['points'][1][1]+state['pos'][1]]
        self.movePoint(self.getHandles()[0], p1, finish=False)
        self.movePoint(self.getHandles()[1], p2)
            
    def paint(self, p, *args):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        h1 = self.endpoints[0].pos()
        h2 = self.endpoints[1].pos()
        p.drawLine(h1, h2)
        
    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):
        p = QPainterPath()
    
        h1 = self.endpoints[0].pos()
        h2 = self.endpoints[1].pos()
        dh = h2-h1
        if dh.length() == 0:
            return p
        pxv = self.pixelVectors(dh)[1]
        if pxv is None:
            return p
            
        pxv *= 4
        
        p.moveTo(h1+pxv)
        p.lineTo(h2+pxv)
        p.lineTo(h2-pxv)
        p.lineTo(h1-pxv)
        p.lineTo(h1+pxv)
      
        return p
    
    def getArrayRegion(self, data, img, axes=(0,1), order=1, returnMappedCoords=False, **kwds):
        """
        Use the position of this ROI relative to an imageItem to pull a slice 
        from an array.
        
        Since this pulls 1D data from a 2D coordinate system, the return value 
        will have ndim = data.ndim-1
        
        See :meth:`~pyqtgraph.ROI.getArrayRegion` for a description of the
        arguments.
        """
        imgPts = [self.mapToItem(img, h.pos()) for h in self.endpoints]

        d = Point(imgPts[1] - imgPts[0])
        o = Point(imgPts[0])
        rgn = fn.affineSlice(data, shape=(int(d.length()),), vectors=[Point(d.norm())], origin=o, axes=axes, order=order, returnCoords=returnMappedCoords, **kwds)

        return rgn

