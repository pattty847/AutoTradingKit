from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QPainterPath, QColor
from atklip.graphics.pyqtgraph import LineSegmentROI
from atklip.graphics.pyqtgraph.Point import Point
import math

from .roi import MyHandle, SpecialROI

translate = QtCore.QCoreApplication.translate

class _PolyLineSegment(LineSegmentROI):
    # Used internally by PolyLineROI
    def __init__(self, *args, **kwds):
        self._parentHovering = False
        LineSegmentROI.__init__(self, *args, **kwds)
        
    def setParentHover(self, hover):
        # set independently of own hover state
        if self._parentHovering != hover:
            self._parentHovering = hover
            self._updateHoverColor()
        
    def _makePen(self):
        if self.mouseHovering or self._parentHovering:
            return self.hoverPen
        else:
            return self.pen
        
    def hoverEvent(self, ev):
        # accept drags even though we discard them to prevent competition with parent ROI
        # (unless parent ROI is not movable)
        if self.parentItem().translatable:
            ev.acceptDrags(Qt.MouseButton.LeftButton)
        return LineSegmentROI.hoverEvent(self, ev)
    
class MyPolyLineROI(SpecialROI):
    r"""
    Container class for multiple connected LineSegmentROIs.

    This class allows the user to draw paths of multiple line segments.

    ============== =============================================================
    **Arguments**
    positions      (list of length-2 sequences) The list of points in the path.
                   Note that, unlike the handle positions specified in other
                   ROIs, these positions must be expressed in the normal
                   coordinate system of the ROI, rather than (0 to 1) relative
                   to the size of the ROI.
    closed         (bool) if True, an extra LineSegmentROI is added connecting 
                   the beginning and end points.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    """
    def __init__(self, positions, closed=False, pos=None, **args):
        
        if pos is None:
            pos = [0,0]
            
        self.closed = closed
        self.segments = []
        SpecialROI.__init__(self, pos, size=[1,1], **args)
        
        self.setPoints(positions)


    def hoverEvent(self, ev: QtCore.QEvent):
        if ev.exit:
            self.setSelected(False)
        else:
            self.setSelected(True)
        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
                hover=True
                
            for btn in [QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton, QtCore.Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                
        if hover:
            self.setMouseHover(True)
            ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
            ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
            self.sigHoverEvent.emit(self)
        else:
            self.setMouseHover(False)

    def setPoints(self, points, closed=None):
        """
        Set the complete sequence of points displayed by this ROI.
        
        ============= =========================================================
        **Arguments**
        points        List of (x,y) tuples specifying handle locations to set.
        closed        If bool, then this will set whether the ROI is closed 
                      (the last point is connected to the first point). If
                      None, then the closed mode is left unchanged.
        ============= =========================================================
        
        """
        if closed is not None:
            self.closed = closed
        
        self.clearPoints()
        
        for p in points:
            self.addFreeHandle(p)
        
        start = -1 if self.closed else 0
        for i in range(start, len(self.handles)-1):
            self.addSegment(self.handles[i]['item'], self.handles[i+1]['item'])
        
    def clearPoints(self):
        """
        Remove all handles and segments.
        """
        while len(self.handles) > 0:
            self.removeHandle(self.handles[0]['item'])
    
    def getState(self):
        state = SpecialROI.getState(self)
        state['closed'] = self.closed
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = SpecialROI.saveState(self)
        state['closed'] = self.closed
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        SpecialROI.setState(self, state)
        self.setPoints(state['points'], closed=state['closed'])
        
    def addSegment(self, h1, h2, index=None):
        seg = _PolyLineSegment(handles=(h1, h2), pen=self.pen, hoverPen=self.hoverPen,
                               parent=self, movable=False)
        if index is None:
            self.segments.append(seg)
        else:
            self.segments.insert(index, seg)
        seg.sigClicked.connect(self.segmentClicked)
        seg.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        seg.setZValue(self.zValue()+1)
        for h in seg.handles:
            h['item'].setDeletable(True)
            h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | Qt.MouseButton.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles
        
    def setMouseHover(self, hover):
        ## Inform all the ROI's segments that the mouse is(not) hovering over it
        SpecialROI.setMouseHover(self, hover)
        for s in self.segments:
            s.setParentHover(hover)
          
    def addHandle(self, info, index=None):
        h = SpecialROI.addHandle(self, info, index=index)
        h.sigRemoveRequested.connect(self.removeHandle)
        self.stateChanged(finish=True)
        return h
        
    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        if ev is not None:
            pos = segment.mapToParent(ev.pos())
        elif pos is None:
            raise Exception("Either an event or a position must be given.")
        h2 = segment.handles[1]['item']
        
        i = self.segments.index(segment)
        h3 = self.addFreeHandle(pos, index=self.indexOfHandle(h2))
        self.addSegment(h3, h2, index=i+1)
        segment.replaceHandle(h2, h3)
        
    def removeHandle(self, handle, updateSegments=True):
        SpecialROI.removeHandle(self, handle)
        handle.sigRemoveRequested.disconnect(self.removeHandle)
        
        if not updateSegments:
            return
        segments = handle.rois[:]
        
        if len(segments) == 1:
            self.removeSegment(segments[0])
        elif len(segments) > 1:
            handles = [h['item'] for h in segments[1].handles]
            handles.remove(handle)
            segments[0].replaceHandle(handle, handles[0])
            self.removeSegment(segments[1])
        self.stateChanged(finish=True)
        
    def removeSegment(self, seg):
        for handle in seg.handles[:]:
            seg.removeHandle(handle['item'])
        self.segments.remove(seg)
        seg.sigClicked.disconnect(self.segmentClicked)
        self.scene().removeItem(seg)
        
    def checkRemoveHandle(self, h):
        ## called when a handle is about to display its context menu
        if self.closed:
            return len(self.handles) > 3
        else:
            return len(self.handles) > 2
        
    def paint(self, p, *args):
        pass
    
    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        p = QPainterPath()
        if len(self.handles) == 0:
            return p
        p.moveTo(self.handles[0]['item'].pos())
        for i in range(len(self.handles)):
            p.lineTo(self.handles[i]['item'].pos())
        p.lineTo(self.handles[0]['item'].pos())
        return p

    def getArrayRegion(self, *args, **kwds):
        return self._getArrayRegionForArbitraryShape(*args, **kwds)

    def setPen(self, *args, **kwds):
        SpecialROI.setPen(self, *args, **kwds)
        for seg in self.segments:
            seg.setPen(*args, **kwds)

class PathROI(MyPolyLineROI):
    on_click = Signal(QObject)
    on_Doubleclick = Signal(QObject)
    draw_rec = Signal()
    

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)

    def __init__(self, positions, closed=False,id=None, pos=None,drawtool=None, **args):
        super().__init__(positions, closed, pos, **args)

        self.has = {
            "name": "rectangle",
            "type": "drawtool",
            "id": id
        }
        
        self.uid = None
        self.id = id
        self.drawtool=drawtool
        self.isSelected = False
        self.last_point = None
        self.finished = False
        self.dounbleclick = False
        self.yoff = False
        self.xoff =False
        self.locked = False

        # self.on_click.connect(self.drawtool.show_popup_setting_tool)
        # self.on_click.connect(self.get_pos_point)
        
        self._arrow_height = 5
        self._arrow_width = 4

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)

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
        if ev.exit:
            hover = False
        else:
            hover = True
                
        if not self.isSelected:
            if hover:
                self.setSelected(True)
                ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    
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

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
    
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def setMouseHover(self, hover):
        ## Inform the ROI that the mouse is(not) hovering over it
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        self._updateHoverColor()
        
    def _updateHoverColor(self):
        pass
    def _makePen(self):
        # Generate the pen color for this ROI based on its current state.
        if self.mouseHovering:
            return self.hoverPen
        else:
            return self.pen

    def setPen(self, *args, **kwds):
        SpecialROI.setPen(self, *args, **kwds)
        for seg in self.segments:
            seg.setPen(*args, **kwds)

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
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.deleteLater()


    def mouseDoubleClickEvent(self, event) -> None:
        #print(325, "mouseDoubleClickEvent", event)
        #ev.ignore()
        self.drawtool.draw_object =None
        self.finished = True
        self.dounbleclick = True
        lasthandle = self.handles[-1]['item']
        self.removeHandle(lasthandle)
        # self.addArrowAtEnd()
        self.update()
    
    def mouseClickEvent_Handle(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if self.last_point != None and (not self.dounbleclick):
                self.addPoint(self.last_point)
    
    def addFreeHandle(self, pos=None, axes=None, item=None, name=None, index=None):
        """
        Add a new free handle to the ROI. Dragging free handles has no effect
        on the position or shape of the ROI. 
        
        =================== ====================================================
        **Arguments**
        pos                 (length-2 sequence) The position of the handle 
                            relative to the shape of the ROI. A value of (0,0)
                            indicates the origin, whereas (1, 1) indicates the
                            upper-right corner, regardless of the ROI's size.
        item                The Handle instance to add. If None, a new handle
                            will be created.
        name                The name of this handle (optional). Handles are 
                            identified by name when calling 
                            getLocalHandlePositions and getSceneHandlePositions.
        =================== ====================================================
        """
        if pos is not None:
            pos = Point(pos)
        return self.addHandle({'name': name, 'type': 'f', 'pos': pos, 'item': item}, index=index)

    def setPoint(self, data):
        if not self.finished and data[0]=="drawed_path":
            if self.drawtool.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()
            else:
                pos_x, pos_y = data[1], data[2]
            point = Point(pos_x, pos_y)
            self.last_point = point
            lasthandle = self.handles[-1]['item']
            self.removeHandle(lasthandle)
            self.addPoint(self.last_point)

    def addSegment(self, h1, h2, index=None):
        seg = _PolyLineSegment(handles=(h1, h2), pen=self.pen, hoverPen=self.hoverPen,
                               parent=self, movable=False)
        if index is None:
            self.segments.append(seg)
        else:
            self.segments.insert(index, seg)
        seg.sigClicked.connect(self.segmentClicked)
        seg.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        seg.setZValue(self.zValue()+1)
        for h in seg.handles:
            h['item'].setDeletable(True)
            h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | QtCore.Qt.MouseButton.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles
        
    def addPoint(self, point):
        self.addFreeHandle(point)
        self.addSegment(self.handles[-2]['item'], self.handles[-1]['item'])
        self.stateChanged(finish=True)
        self.update()

    def setPoints(self, points, closed=None):
        """
        Set the complete sequence of points displayed by this ROI.
        ============= =========================================================
        **Arguments**
        points        List of (x,y) tuples specifying handle locations to set.
        closed        If bool, then this will set whether the ROI is closed 
                      (the last point is connected to the first point). If
                      None, then the closed mode is left unchanged.
        ============= =========================================================
        """
        if closed is not None:
            self.closed = closed
        self.clearPoints()
        for p in points:
            self.addFreeHandle(p)
        start = -1 if self.closed else 0
        for i in range(start, len(self.handles)-1):
            self.addSegment(self.handles[i]['item'], self.handles[i+1]['item'])
        
    def clearPoints(self):
        """
        Remove all handles and segments.
        """
        while len(self.handles) > 0:
            self.removeHandle(self.handles[0]['item'])
    
    def getState(self):
        state = SpecialROI.getState(self)
        state['closed'] = self.closed
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = SpecialROI.saveState(self)
        state['closed'] = self.closed
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        SpecialROI.setState(self, state)
        self.setPoints(state['points'], closed=state['closed'])
        
    def setMouseHover(self, hover):
        ## Inform all the ROI's segments that the mouse is(not) hovering over it
        SpecialROI.setMouseHover(self, hover)
        for s in self.segments:
            s.setParentHover(hover)
          

    def addHandle(self, info, index=None):
        h = SpecialROI.addHandle(self, info, index=index)
        h.sigRemoveRequested.connect(self.removeHandle)
        self.stateChanged(finish=True)
        h.mouseClickEvent = self.mouseClickEvent_Handle
        h.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.update()
        return h
        
    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        self.on_click.emit(self)
        
    def indexOfHandle(self, handle):
        """
        Return the index of *handle* in the list of this ROI's handles.
        """
        if isinstance(handle, MyHandle):
            index = [i for i, info in enumerate(self.handles) if info['item'] is handle]    
            if len(index) == 0:
                raise Exception("Cannot return handle index; not attached to this ROI")
            return index[0]
        else:
            return handle
        
    def removeHandle(self, handle, updateSegments=True):
        SpecialROI.removeHandle(self, handle)
        handle.sigRemoveRequested.disconnect(self.removeHandle)
        
        if not updateSegments:
            return
        segments = handle.rois[:]
        
        if len(segments) == 1:
            self.removeSegment(segments[0])
        elif len(segments) > 1:
            handles = [h['item'] for h in segments[1].handles]
            handles.remove(handle)
            segments[0].replaceHandle(handle, handles[0])
            self.removeSegment(segments[1])
        self.stateChanged(finish=True)

    def removeSegment(self, seg):
        for handle in seg.handles[:]:
            seg.removeHandle(handle['item'])
        self.segments.remove(seg)
        seg.sigClicked.disconnect(self.segmentClicked)
        if self.scene():
            self.scene().removeItem(seg)

    def checkRemoveHandle(self, h):
        ## called when a handle is about to display its context menu
        if self.closed:
            return len(self.handles) > 3
        else:
            return len(self.handles) > 2
    
       
    def paint(self, painter: QtGui.QPainter, option, widget=None):
        pass
      
    
    # def boundingRect(self):
    #     pass
        # return self.shape().boundingRect()

    def shape(self):
        p = QtGui.QPainterPath()
        if len(self.handles) == 0:
            return p
        p.moveTo(self.handles[0]['item'].pos())
        for i in range(len(self.handles)):
            p.lineTo(self.handles[i]['item'].pos())
        p.lineTo(self.handles[0]['item'].pos())
        return p

    def getArrayRegion(self, *args, **kwds):
        return self._getArrayRegionForArbitraryShape(*args, **kwds)
    
    def addArrowAtEnd(self):
        if len(self.handles) >= 2:
            # Get the last two handles
            handle1 = self.handles[-2]['item']
            handle2 = self.handles[-1]['item']
            
            # Calculate the direction of the arrow
            direction = handle2.pos() - handle1.pos()
            direction /= Point(direction).length()
            
            # Calculate the arrowhead points
            arrowhead_length = 10  # You can adjust this value
            p1 = handle2.pos()
            p2 = p1 - direction.rotate(30) * arrowhead_length
            p3 = p1 - direction.rotate(-30) * arrowhead_length
            
            # Add arrowhead handles
            arrowhead_handle1 = self.addFreeHandle(p1)
            arrowhead_handle2 = self.addFreeHandle(p2)
            arrowhead_handle3 = self.addFreeHandle(p3)
            
            # Add a segment for the arrowhead
            self.addSegment(arrowhead_handle1, arrowhead_handle2)
            self.addSegment(arrowhead_handle2, arrowhead_handle3)







