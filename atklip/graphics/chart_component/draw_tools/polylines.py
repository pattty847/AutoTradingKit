from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from pyqtgraph import PolyLineROI, TextItem, Point, ArrowItem, mkPen

draw_line_color = '#2962ff'
epoch_period = 1e30

from .roi import BaseHandle, SpecialROI, _FiboLineSegment

class RangePolyLine(SpecialROI):     # for date price range
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    
    def __init__(self, pos, size=..., angle=0, invertible=True, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, rotatable=True, resizable=True, removable=False, aspectLocked=False, drawtool=None):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked)
    
        self.drawtool = drawtool
        self.chart = self.drawtool.chart
        
        self.has = {
            "name": "rectangle",
            "type": "drawtool",
            "id": id
        }
        self.texts = []
        self.arrows = []
        self.finished = False
        self.dounbleclick = False
        self.last_point = None
        self.segments = []
        self.isSelected = False
        self.indicator_name="Ruler..."
        
        
        self.v_arrow = ArrowItem(angle=90, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.h_arrow = ArrowItem(angle=180, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.text = TextItem(color=draw_line_color,anchor=(0,0))

        self.v_arrow.setParentItem(self)
        self.h_arrow.setParentItem(self)
        self.text.setParentItem(self)
        
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 1], [0, 0])
        try:
            self.addSegment(self.handles[0]['item'], self.handles[1]['item'])
        except:
            import traceback
            traceback.print_exc()

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
    
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
    
    def change_size_handle(self, size):
        for handle in self.endpoints:
            handle.change_size_handle(size)
    
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
        QGraphicsItem.setSelected(self, s)
        #print "select", self, s
        if s:
            [h['item'].show() for h in self.handles]
            [h.show() for h in self.segments]

        else:
            [h['item'].hide() for h in self.handles]
            [h.hide() for h in self.segments]

    def hoverEvent(self, ev):
        hover = False
        if ev.exit:
            hover = False
        else:
            hover = True
                
        if not self.isSelected:
            if hover:
                self.setSelected(True)
                ev.acceptClicks(Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(Qt.MouseButton.RightButton)
                ev.acceptClicks(Qt.MouseButton.MiddleButton)
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)
    
    def mouseDragEvent(self, ev, axis=None, line=None):
        self.setSelected(True)
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.chart.vb.mouseDragEvent(ev, axis)

        if not self.locked and line:
            return super().mouseDragEvent(ev)
        elif self.locked and line:
            ev.ignore()
        ev.ignore()
    
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.finished = True
        ev.ignore()
    

    def setObjectName(self, name):
        self.indicator_name = name

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if not self.boundingRect().contains(ev.pos()):
                ev.accept()
                self.on_click.emit(self)
            self.finished = True
            self.drawtool.drawing_object =None
        ev.ignore()
    
    def objectName(self):
        return self.indicator_name
        
    def setPoint(self, pos_x, pos_y):
        print(pos_x, pos_y, self.drawtool)
        if not self.finished:
            if self.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()

            point = Point(pos_x, pos_y)
            pos = self.chart.vb.mapViewToScene(point)
            self.last_point = point
            lasthandle = self.handles[-1]['item']
                        
            lasthandle.movePoint(pos)
            # self.update_arrows()
            self.stateChanged()
    
    def update_text(self, text):
        print(text)
        # h0 = text.segment.handles[0]['item']
        # h1 = text.segment.handles[1]['item']
        # # self.segments
        # diff = h1.pos() - h0.pos()
        # if diff.y() < 0:
        #     text.setAnchor((0.5,0))
        # else:
        #     text.setAnchor((0.5,1))
        # text.setPos(h1.pos())
        # text.setText(_draw_line_segment_text(self, text.segment, h0.pos(), h1.pos()))

    def update_texts(self):
        self.update_text("text")

    def update_arrows(self):
        h0 = self.handles[0]['item'].pos()
        h1 = self.handles[1]['item'].pos()
        diff = h1 - h0
        _width = abs(diff.x()) 
        _height = abs(diff.y()) #- self.v_arrow.opts["headLen"]
        if diff.y() < 0:
            # print(63, "di xuong")
            self.v_arrow.setStyle(angle=-90)
        else:
            self.v_arrow.setStyle(angle=90)
        if diff.x() > 0:
            # sang phai
            self.h_arrow.setStyle(angle=180)
        else:
            self.h_arrow.setStyle(angle=0)
            # print(66, "di len")
        self.h_arrow.setPos(h1.x(), h1.y() - diff.y() /2)
        self.v_arrow.setPos(h1.x() - diff.x() /2, h1.y())

    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        if ev is not None:
            pos = segment.mapToParent(ev.pos())
        elif pos is None:
            raise Exception("Either an event or a position must be given.")
        # h2 = segment.handles[1]['item']
        print(598, pos, self)
        if not self.finished:
            self.finished = True
            self.drawtool.drawing_object =None
        self.on_click.emit(self)

    
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
        h.mouseClickEvent = self.mouseClickEvent_Handle
        h.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        return h
    
    
    def mouseDoubleClickEvent(self, event) -> None:
        self.drawtool.drawing_object =None
        self.finished = True
        self.dounbleclick = True
        self.update()
    
    def mouseClickEvent_Handle(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if self.last_point != None and (not self.dounbleclick):
                self.drawtool.drawing_object =None
                self.finished = True
                self.dounbleclick = True
                print(111,self.drawtool.drawing_object)
                self.update()
    
    def paint(self, p: QPainter, *args):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(mkPen(draw_line_color,width=1))
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[1]['item'].pos()
            diff = h1 - h0
            p.drawLine(QPointF(h1.x(), h1.y() - diff.y() /2), QPointF(h0.x(), h1.y() - diff.y() /2))
            p.drawLine(QPointF(h1.x() - diff.x() /2, h1.y()), QPointF(h1.x() - diff.x() /2, h0.y()))
            p.setPen(QColor(252, 163, 38, 40))
            p.setBrush(QColor(252, 163, 38, 40))
            p.fillRect(QRectF(h1,h0), QColor(252, 163, 38, 40))
            self.update_arrows()


class MouseDragHandler(object):
    """Implements default mouse drag behavior for ROI (not for ROI handles).
    """
    def __init__(self, roi):
        self.roi = roi
        self.dragMode = None
        self.startState = None
        self.snapModifier = Qt.KeyboardModifier.ControlModifier
        self.translateModifier = Qt.KeyboardModifier.NoModifier
        self.rotateModifier = Qt.KeyboardModifier.AltModifier
        self.scaleModifier = Qt.KeyboardModifier.ShiftModifier
        self.rotateSpeed = 0.5
        self.scaleSpeed = 1.01

    def mouseDragEvent(self, ev):
        roi = self.roi

        if ev.isStart():
            if ev.button() == Qt.MouseButton.LeftButton:
                roi.setSelected(True)
                mods = ev.modifiers() & ~self.snapModifier
                if roi.translatable and mods == self.translateModifier:
                    self.dragMode = 'translate'
                elif roi.rotatable and mods == self.rotateModifier:
                    self.dragMode = 'rotate'
                elif roi.resizable and mods == self.scaleModifier:
                    self.dragMode = 'scale'
                else:
                    self.dragMode = None
                
                if self.dragMode is not None:
                    roi._moveStarted()
                    self.startPos = roi.mapToParent(ev.buttonDownPos())
                    print(164, self.startPos)
                    self.startState = roi.saveState()
                    self.cursorOffset = roi.pos() - self.startPos
                    ev.accept()
                else:
                    ev.ignore()
            else:
                self.dragMode = None
                ev.ignore()


        if ev.isFinish() and self.dragMode is not None:
            roi._moveFinished()
            return

        # roi.isMoving becomes False if the move was cancelled by right-click
        if not roi.isMoving or self.dragMode is None:
            return

        snap = True if (ev.modifiers() & self.snapModifier) else None
        pos = roi.mapToParent(ev.pos())
        if self.dragMode == 'translate':
            newPos = pos + self.cursorOffset
            roi.translate(newPos - roi.pos(), snap=snap, finish=False)
        elif self.dragMode == 'rotate':
            diff = self.rotateSpeed * (ev.scenePos() - ev.buttonDownScenePos()).x()
            angle = self.startState['angle'] - diff
            roi.setAngle(angle, centerLocal=ev.buttonDownPos(), snap=snap, finish=False)
        elif self.dragMode == 'scale':
            diff = self.scaleSpeed ** -(ev.scenePos() - ev.buttonDownScenePos()).y()
            roi.setSize(Point(self.startState['size']) * diff, centerLocal=ev.buttonDownPos(), snap=snap, finish=False)


def _draw_line_segment_text(polyline, segment, pos0, pos1):
    diff = pos1 - pos0
    fsecs = abs(diff.x()) #*epoch_period)
    secs = int(fsecs)
    mins = secs//60
    hours = mins//60
    mins = mins%60
    secs = secs%60
    if hours==0 and mins==0 and secs < 60: # and   < 1:
        msecs = int((fsecs-int(fsecs))*1000)
        ts = '%0.2i:%0.2i.%0.3i' % (mins, secs, msecs)
    elif hours==0 and mins < 60 and epoch_period < 60:
        ts = '%0.2i:%0.2i:%0.2i' % (hours, mins, secs)
    elif hours < 24:
        ts = '%0.2i:%0.2i' % (hours, mins)
    else:
        days = hours // 24
        hours %= 24
        ts = '%id %0.2i:%0.2i' % (days, hours, mins)
        if ts.endswith(' 00:00'):
            ts = ts.partition(' ')[0]
    # ysc = polyline.vb.yscale
    if 1: # polyline.vb.y_positive:
        # y0,y1 = ysc.xform(pos0.y()), ysc.xform(pos1.y())
        y0,y1 = pos0.y(), pos1.y()
        if y0:
            gain = y1 / y0 - 1
            if gain > 10:
                value = 'x%i' % gain
            else:
                value = '%+.2f %%' % (100 * gain)
        elif not y1:
            value = '0'
        else:
            value = '+∞' if y1>0 else '-∞'
    else:
        dy = diff.y() # ysc.xform(diff.y())
        if dy and (abs(dy) >= 1e4 or abs(dy) <= 1e-2):
            value = '%+3.3g' % dy
        else:
            value = '%+2.2f' % dy
    extra = _draw_line_extra_text(polyline, segment, pos0, pos1)
    # print(180, value, extra, ts)
    return '%s %s (%s)' % (value, extra, ts)


def _draw_line_extra_text(polyline, segment, pos0, pos1):
    '''Shows the proportions of this line height compared to the previous segment.'''
    prev_text = None
    for text in polyline.texts:
        if prev_text is not None and text.segment == segment:
            h0 = prev_text.segment.handles[0]['item']
            h1 = prev_text.segment.handles[1]['item']
            prev_change = h1.pos().y() - h0.pos().y()
            this_change = pos1.y() - pos0.y()
            if abs(prev_change) <= 1e-14:
                break
            change_part = abs(this_change / prev_change)
            # print(196, change_part)
            return ' = 1:%.2f ' % change_part
        prev_text = text
    return ''


"""
    The yaxis parameter can be one of [False, 'linear', 'log'].'''
"""