import datetime as dt
from math import atan2, cos, sin
from operator import itemgetter

import numpy as np
import pytz
from PySide6 import QtCore
from PySide6.QtCore import Signal, QObject, QPointF, Qt, QRectF, QCoreApplication, QPoint
from PySide6.QtGui import QPainter, QPainterPath, QColor, QTransform
from PySide6.QtWidgets import QWidget, QMenu
from pyqtgraph import functions as fn, LineSegmentROI, ROI, TextItem, TargetItem, mkPen, UIGraphicsItem, GraphicsObject
from pyqtgraph.Point import Point
from pyqtgraph.graphicsItems.ROI import Handle

DEFAULTS_FIBO = [1.0, 0.786, 0.618, 0.5, 0.382, 0.236, 0.0]
DEFAULTS_COLOR = [(120,123,134,200),(242,54,69,200),(255,152,0,200),(76,175,80,200),(8,153,129,200),(0,188,212,200),(120,123,134,200),(41, 98, 255,200),(242, 54, 69, 200),(156,39,176,200),(233, 30, 99,200),(206,147,216,200),(159,168,218,200),(255,204,128,200),
                        (229,115,115,200),(244,142,177,200),(66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200)]
LEFT_FAR_TIMESTAMP = 1562990041
RIGHT_FAR_TIMESTAMP = 1783728000
translate = QCoreApplication.translate


class MyHandle(Handle, UIGraphicsItem):
    """
    Handle represents a single user-interactable point attached to an ROI. They
    are usually created by a call to one of the ROI.add___Handle() methods.
    
    Handles are represented as a square, diamond, or circle, and are drawn with 
    fixed pixel size regardless of the scaling of the view they are displayed in.
    
    Handles may be dragged to change the position, size, orientation, or other
    properties of the ROI they are attached to.
    """
    types = {   ## defines number of sides, start angle for each handle type
        't': (4, np.pi/4),
        'f': (4, np.pi/4), # hinh vuong
        's': (4, 0),       # hinh thoi
        'r': (12, 0),      # hinh tron
        'sr': (12, 0),
        'rf': (12, 0),
    }

    sigClicked = Signal(object, object)   # self, event
    sigRemoveRequested = Signal(object)   # self
    
    def __init__(self, radius, typ="r", pen=(200, 200, 220),
                 hoverPen=(255, 255, 0), parent=None, deletable=False, draggable=True):
        self.rois = []
        self.radius = radius
        self.typ = typ
        self.pen = fn.mkPen(pen)
        self.brush = fn.mkBrush("#ff7028")
        self.currentBrush = self.brush
        self.hoverPen = fn.mkPen(hoverPen)
        self.hoverBrush = fn.mkBrush("#ff7028")
        self.currentPen = self.pen
        self.pen.setWidth(0)
        self.pen.setCosmetic(True)
        self.isMoving = False
        self.sides, self.startAng = self.types["r"]
        self.buildPath()
        self._shape = None
        self.menu = self.buildMenu()
        self.draggable = draggable
        self.horing = False
        
        UIGraphicsItem.__init__(self, parent=parent)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.deletable = deletable
        if deletable:
            self.setAcceptedMouseButtons(Qt.MouseButton.RightButton)        
        self.setZValue(11)

    def change_size_handle(self, size):
        self.radius = size
        self.buildPath()
        self.update()
        self._updateView()
        self.viewTransformChanged()
            
    def connectROI(self, roi):
        ### roi is the "parent" roi, i is the index of the handle in roi.handles
        self.rois.append(roi)
        
    def disconnectROI(self, roi):
        self.rois.remove(roi)
            
    def setDeletable(self, b):
        self.deletable = b
        if b:
            self.setAcceptedMouseButtons(self.acceptedMouseButtons() | Qt.MouseButton.RightButton)
        else:
            self.setAcceptedMouseButtons(self.acceptedMouseButtons() & ~Qt.MouseButton.RightButton)

    def removeClicked(self):
        self.sigRemoveRequested.emit(self)

    def hoverEvent(self, ev):
        hover = False
        if not ev.isExit():
            if ev.acceptDrags(Qt.MouseButton.LeftButton):
                hover=True
            for btn in [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
                    
        if hover:
            self.currentPen = self.hoverPen
            self.currentBrush = self.hoverBrush
            self.show()
        else:
            self.currentPen = self.pen
            self.currentBrush = self.brush
            # self.hide()

        self.update()

    def mouseClickEvent(self, ev):
        ## right-click cancels drag
        if ev.button() == Qt.MouseButton.RightButton and self.isMoving:
            self.isMoving = False  ## prevents any further motion
            self.movePoint(self.startPos, finish=True)
            ev.accept()
        elif self.acceptedMouseButtons() & ev.button():
            ev.accept()
            if ev.button() == Qt.MouseButton.RightButton and self.deletable:
                self.raiseContextMenu(ev)
            self.sigClicked.emit(self, ev)
        else:
            ev.ignore()
                
    def buildMenu(self):
        menu = QMenu()
        menu.setTitle(translate("ROI", "Handle"))
        self.removeAction = menu.addAction(translate("ROI", "Remove handle"), self.removeClicked) 
        return menu
        
    def getMenu(self):
        return self.menu

    def raiseContextMenu(self, ev):
        menu = self.scene().addParentContextMenus(self, self.getMenu(), ev)
        
        ## Make sure it is still ok to remove this handle
        removeAllowed = all(r.checkRemoveHandle(self) for r in self.rois)
        self.removeAction.setEnabled(removeAllowed)
        pos = ev.screenPos()
        menu.popup(QPoint(int(pos.x()), int(pos.y())))    

    def mouseDragEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        # if not self.draggable:
        #     return
        ev.accept()
        
        ## Inform ROIs that a drag is happening 
        ##  note: the ROI is informed that the handle has moved using ROI.movePoint
        ##  this is for other (more nefarious) purposes.
        #for r in self.roi:
            #r[0].pointDragEvent(r[1], ev)
            
        if ev.isFinish():
            if self.isMoving:
                for r in self.rois:
                    r.stateChangeFinished()
            self.isMoving = False
            self.currentPen = self.pen
            self.currentBrush = self.brush
            self.update()
        elif ev.isStart():
            for r in self.rois:
                r.handleMoveStarted()
            self.isMoving = True
            self.startPos = self.scenePos()
            self.cursorOffset = self.scenePos() - ev.buttonDownScenePos()
            self.currentPen = self.hoverPen
            self.currentBrush = self.hoverBrush
            
        if self.isMoving:  ## note: isMoving may become False in mid-drag due to right-click.
            pos = ev.scenePos() + self.cursorOffset
            self.currentPen = self.hoverPen
            self.currentBrush = self.hoverBrush

            # self.plotItem.vb.mapViewToScene  get_position_crosshair()
            # print("moving handle", pos, self.parentItem().chart.vb.mapViewToScene(QPointF(position[0],position[1])))
            if self.parentItem().chart.magnet_on:
                position = self.parentItem().chart.get_position_crosshair()
                pos = self.parentItem().chart.vb.mapViewToScene(QPointF(position[0],position[1]))
            self.movePoint(pos, ev.modifiers(), finish=False)

    def movePoint(self, pos, modifiers=None, finish=True):
        if modifiers is None:
            modifiers = Qt.KeyboardModifier.NoModifier
        for r in self.rois:
            if not r.checkPointMove(self, pos, modifiers):
                return
        #print "point moved; inform %d ROIs" % len(self.roi)
        # A handle can be used by multiple ROIs; tell each to update its handle position
        for r in self.rois:
            r.movePoint(self, pos, modifiers, finish=finish, coords='scene')
        
    def buildPath(self):
        size = self.radius
        self.path = QPainterPath()
        ang = self.startAng
        dt = 2 * np.pi / self.sides
        for i in range(0, self.sides+1):
            x = size * cos(ang)
            y = size * sin(ang)
            ang += dt
            if i == 0:
                self.path.moveTo(x, y)
            else:
                self.path.lineTo(x, y)            
            
    def paint(self, p, opt, widget):
        p.setRenderHints(p.RenderHint.Antialiasing, True)
        p.setPen(self.currentPen)
        p.setBrush(self.currentBrush)
        
        p.drawPath(self.shape())
            
    def shape(self):
        if self._shape is None:
            s = self.generateShape()
            if s is None:
                return self.path
            self._shape = s
            self.prepareGeometryChange()  ## beware--this can cause the view to adjust, which would immediately invalidate the shape.
        return self._shape
    
    def boundingRect(self):
        s1 = self.shape()  # noqa: avoid problems with shape invalidation
        return self.shape().boundingRect()
            
    def generateShape(self):
        dt = self.deviceTransform()
        
        if dt is None:
            self._shape = self.path
            return None
        
        v = dt.map(QPointF(1, 0)) - dt.map(QPointF(0, 0))
        va = atan2(v.y(), v.x())
        
        dti = fn.invertQTransform(dt)
        devPos = dt.map(QPointF(0,0))
        tr = QTransform()
        tr.translate(devPos.x(), devPos.y())
        tr.rotateRadians(va)
        
        return dti.map(tr.map(self.path))
        
    def viewTransformChanged(self):
        GraphicsObject.viewTransformChanged(self)
        self._shape = None  ## invalidate shape, recompute later if requested.
        self.update()

class MyROI(ROI):
    def __init__(self, *args, **kwargs):
        ROI.__init__(self, *args, **kwargs)
        self.handleSize = 4
        self.point_draggable = True

    def addHandle(self, info, index=None):
        ## If a Handle was not supplied, create it now
        if 'item' not in info or info['item'] is None:
            h = MyHandle(self.handleSize, pen=self.handlePen, hoverPen=self.handleHoverPen, parent=self) #typ=info['type']
            info['item'] = h
        else:
            h = info['item']
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

class SmallROI(ROI):
    def __init__(self, *args, **kwargs):
        ROI.__init__(self, *args, **kwargs)
        self.handleSize = 0
        self.point_draggable = True

class MyLineNoHandleROI(SmallROI):
    def __init__(self, positions=(None, None), pos=None, handles=(None,None), point_draggable=True,**args):
        if pos is None:
            pos = [0,0]
            
        SmallROI.__init__(self, pos, [1,1], **args)
        if len(positions) > 2:
            raise Exception("LineSegmentROI must be defined by exactly 2 positions. For more points, use PolyLineROI.")
        
        for i, p in enumerate(positions):
            self.addFreeHandle(p, item=handles[i])
            
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

class SpecialROI(ROI):
    finish_changed = Signal(list)

    def __init__(self, *args, **kwargs):
        ROI.__init__(self, *args, **kwargs)
        self.handleSize = 4
        self.yoff = False
        self.xoff = False
        self.locked = False

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
        return h

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
        
    def movePoint(self, handle, pos, modifiers=None, finish=True, coords='parent'):
        ## called by Handles when they are moved. 
        ## pos is the new position of the handle in scene coords, as requested by the handle.
        if modifiers is None:
            modifiers = Qt.KeyboardModifier.NoModifier
        newState = self.stateCopy()
        index = self.indexOfHandle(handle)
        h = self.handles[index]
        p0 = self.mapToParent(h['pos'] * self.state['size'])
        p1 = Point(pos)

        # print("moving ROI", p1)
        
        if coords == 'parent':
            pass
        elif coords == 'scene':
            p1 = self.mapSceneToParent(p1)
        else:
            raise Exception("New point location must be given in either 'parent' or 'scene' coordinates.")

        ## Handles with a 'center' need to know their local position relative to the center point (lp0, lp1)
        if 'center' in h:
            c = h['center']
            cs = c * self.state['size']
            lp0 = self.mapFromParent(p0) - cs
            lp1 = self.mapFromParent(p1) - cs
        
        if h['type'] == 't':
            snap = True if (modifiers & Qt.KeyboardModifier.ControlModifier) else None
            self.translate(p1-p0, snap=snap, update=False)
        
        elif h['type'] == 'f':
            # print(888, self.xoff, self.yoff)
            if self.yoff and self.xoff:
                self.freeHandleMoved = False
            else:
                newPos = self.mapFromParent(p1)
                h['item'].setPos(newPos)
                h['pos'] = newPos
                self.freeHandleMoved = True
            
        elif h['type'] == 's':
            ## If a handle and its center have the same x or y value, we can't scale across that axis.
            if h['center'][0] == h['pos'][0] or self.xoff:
                lp1[0] = 0
            if h['center'][1] == h['pos'][1] or self.yoff:
                lp1[1] = 0
            
            ## snap 
            if self.scaleSnap or (modifiers & Qt.KeyboardModifier.ControlModifier):
                lp1[0] = round(lp1[0] / self.scaleSnapSize) * self.scaleSnapSize
                lp1[1] = round(lp1[1] / self.scaleSnapSize) * self.scaleSnapSize
                
            ## preserve aspect ratio (this can override snapping)
            if h['lockAspect'] or (modifiers & Qt.KeyboardModifier.AltModifier):
                #arv = Point(self.preMoveState['size']) - 
                lp1 = lp1.proj(lp0)
            
            ## determine scale factors and new size of ROI
            hs = h['pos'] - c
            if hs[0] == 0:
                hs[0] = 1
            if hs[1] == 0:
                hs[1] = 1
            newSize = lp1 / hs
            
            ## Perform some corrections and limit checks
            if newSize[0] == 0:
                newSize[0] = newState['size'][0]
            if newSize[1] == 0:
                newSize[1] = newState['size'][1]
            if not self.invertible:
                if newSize[0] < 0:
                    newSize[0] = newState['size'][0]
                if newSize[1] < 0:
                    newSize[1] = newState['size'][1]
            if self.aspectLocked:
                newSize[0] = newSize[1]
            
            ## Move ROI so the center point occupies the same scene location after the scale
            s0 = c * self.state['size']
            s1 = c * newSize
            cc = self.mapToParent(s0 - s1) - self.mapToParent(Point(0, 0))
            
            ## update state, do more boundary checks
            newState['size'] = newSize
            newState['pos'] = newState['pos'] + cc
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            
            self.setPos(newState['pos'], update=False)
            self.setSize(newState['size'], update=False)
        
        elif h['type'] in ['r', 'rf']:
            if h['type'] == 'rf':
                self.freeHandleMoved = True
            
            if not self.rotatable:
                return
            ## If the handle is directly over its center point, we can't compute an angle.
            try:
                if lp1.length() == 0 or lp0.length() == 0:
                    return
            except OverflowError:
                return
            
            ## determine new rotation angle, constrained if necessary
            ang = newState['angle'] - lp0.angle(lp1)
            if ang is None:  ## this should never happen..
                return
            if self.rotateSnap or (modifiers & Qt.KeyboardModifier.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle
            
            ## create rotation transform
            tr = QTransform()
            tr.rotate(ang)
            
            ## move ROI so that center point remains stationary after rotate
            cc = self.mapToParent(cs) - (tr.map(cs) + self.state['pos'])
            newState['angle'] = ang
            newState['pos'] = newState['pos'] + cc
            
            ## check boundaries, update
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            self.setPos(newState['pos'], update=False)
            self.setAngle(ang, update=False)
            
            ## If this is a free-rotate handle, its distance from the center may change.
            
            if h['type'] == 'rf':
                h['item'].setPos(self.mapFromScene(p1))  ## changes ROI coordinates of handle
                h['pos'] = self.mapFromParent(p1)
                
        elif h['type'] == 'sr':
            try:
                if lp1.length() == 0 or lp0.length() == 0:
                    return
            except OverflowError:
                return
            
            ang = newState['angle'] - lp0.angle(lp1)
            if ang is None:
                return
            if self.rotateSnap or (modifiers & Qt.KeyboardModifier.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle

            if self.aspectLocked or h['center'][0] != h['pos'][0]:
                newState['size'][0] = self.state['size'][0] * lp1.length() / lp0.length()
                if self.scaleSnap:  # use CTRL only for angular snap here.
                    newState['size'][0] = round(newState['size'][0] / self.snapSize) * self.snapSize

            if self.aspectLocked or h['center'][1] != h['pos'][1]:
                newState['size'][1] = self.state['size'][1] * lp1.length() / lp0.length()
                if self.scaleSnap:  # use CTRL only for angular snap here.
                    newState['size'][1] = round(newState['size'][1] / self.snapSize) * self.snapSize

            if newState['size'][0] == 0:
                newState['size'][0] = 1
            if newState['size'][1] == 0:
                newState['size'][1] = 1

            c1 = c * newState['size']
            tr = QTransform()
            tr.rotate(ang)
            
            cc = self.mapToParent(cs) - (tr.map(c1) + self.state['pos'])
            newState['angle'] = ang
            newState['pos'] = newState['pos'] + cc
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            
            self.setState(newState, update=False)
        
        self.stateChanged(finish=finish)

    def stateChangeFinished(self):
        self.sigRegionChangeFinished.emit(self)
        self.finish_changed.emit([self.state])
        
class _FiboLineSegment(LineSegmentROI):     # dung de ke line cheo
    # Used internally by PolyLineROI
    on_click = Signal(QObject)
    def __init__(self, *args, **kwds):
        self._parentHovering = False
        LineSegmentROI.__init__(self, *args, **kwds)
        self._parent = kwds["parent"]
        self.scaleModifier = Qt.KeyboardModifier.NoModifier


    def mouseDragEvent(self, ev):
        

        return self._parent.mouseDragEvent(ev, line=self)
    
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

        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(Qt.MouseButton.LeftButton):
                hover=True
                
            for btn in [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(Qt.MouseButton.RightButton)
                
        if hover:
            # self.setMouseHover(True)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            ev.acceptClicks(Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(Qt.MouseButton.RightButton)
            ev.acceptClicks(Qt.MouseButton.MiddleButton)
            self.sigHoverEvent.emit(self)
        else:
            # self.setMouseHover(False)
            self.setCursor(Qt.CursorShape.CrossCursor)

class FiboROI(SpecialROI):
    on_click = Signal(object)
    draw_rec = Signal()


    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    signal_update_text = Signal(list)

    def __init__(self, pos, size=..., angle=0, invertible=True, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, rotatable=True, resizable=True, removable=False, aspectLocked=False, main=None, fibo_level=None, color_rect=None, color_line=None, color_borders=None,):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked)
        #self.generate_lines()
        self.id = None

        self.parent, self.chart=parent, main    # parent is viewbox


        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 1], [0, 0])
        self.segments = []
        self.popup_setting_tool = None
        self.isSelected = False
       
        # self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.precision = self.chart.get_trading_rules_precision(self.chart.symbol)
        # print(489, self.precision, self.chart.symbol)
        # self.add_cross_line_fibo()

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)
        self.signal_update_text.connect(self.update_text_percentage)

        self.last_left_pos = None
        self.last_right_pos = None
        self.reverse = False
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
            target = TextItem("")
            target.setAnchor((1,0.6))
            self.list_lines.append(target)
            self.parent.addItem(target)
        
        try:
            self.addSegment(self.handles[0]['item'], self.handles[1]['item'])
        except:
            import traceback
            traceback.print_exc()
        self.lastMousePos = pos
        self.finished = False
        self.first_click = False
        self.drawed = False
        self.chart.mousepossiton_signal.connect(self.setPoint)
        self.on_click.connect(self.chart.main.show_popup_setting_tool)
   
    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            self.setSelected(True)
            self.change_size_handle(3)
        else:
            self.isSelected = False
            self.setSelected(False)
            self.change_size_handle(4)

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
        h.mousePressEvent = self.mousePressEvent
        return h
    
    def update_text_percentage(self, data):
        i, price, x, direct = data[0], data[1], data[2], data[3]
        text = self.list_lines[i]
        if direct == 1:
            text.percent = self.fibonacci_levels[i]
            text.setColor(self.colors_lines[self.counts - i - 1])
            text.setText(f"{self.fibonacci_levels[i]} ({str(price)})" )
            text.setPos(x, price)
        else:
            text.percent = self.fibonacci_levels[self.counts - i - 1]
            text.setColor(self.colors_lines[i])
            text.setText(f"{self.fibonacci_levels[self.counts - i - 1]} ({str(price)})" )
            text.setPos(x, price)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            print(780, "Left button ne")
            self.chart.draw_object =None
            self.finished = True
        ev.ignore()

    def setPoint(self,data):
        # print(318, "lastmouse_position", data, self.finished)
        if not self.finished and data[0]=="drawed_fibo_retracement":
            self.state['size'] = [data[1]-self.state['pos'][0], data[2]-self.state['pos'][1]]
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
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.price_axis.kwargs["horizontal_ray"].remove(self.id)
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

    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        if ev is not None:
            pos = segment.mapToParent(ev.pos())
        elif pos is None:
            raise Exception("Either an event or a position must be given.")
        # h2 = segment.handles[1]['item']
        # print(598, pos, self)
        if self.chart.draw_object or not self.finished:
            self.chart.draw_object =None
            self.finished = True
        self.on_click.emit(self)

    def add_text(self, counts):
        diff = counts - self.counts
        if diff > 0:
            for i in range(counts):
                target = TextItem("")
                target.setAnchor((1,0.6))
                self.list_lines.append(target)
                self.parent.addItem(target)
            self.counts = len(self.list_lines)

    def update_fibo(self, mapchart_trading, setting_tool_menu):
        # print(161, setting_tool_menu.scrollAreaWidgetContents.findChildren(QWidget, "widget_fibo_lines"))
        list_line_config = setting_tool_menu.scrollAreaWidgetContents.findChildren(QWidget, "widget_fibo_lines")
        list_fibo_level_temp = []
        for wid in list_line_config:
            if wid.cb_on_off.isChecked():
                try:
                    list_fibo_level_temp.append({
                    "per_price": float(wid.txt_per_price.text()),
                    "color": wid.pick_color.color()
                    })
                except ValueError:
                    continue
            if wid.cb_on_off_2.isChecked():
                try:
                    list_fibo_level_temp.append({
                        "per_price": float(wid.txt_per_price_2.text()),
                        "color": wid.pick_color_2.color()
                    })
                except ValueError:
                    continue
        list_fibo_line_sorted = sorted(list_fibo_level_temp, key=itemgetter('per_price'), reverse=True)
        # print(179, list_fibo_line_sorted)   
        list_level = []
        color_rect = []
        color_line = []
        color_border = []
        for line in list_fibo_line_sorted:
            list_level.append(line["per_price"])
            red = line["color"].red()
            green = line["color"].green()
            blue = line["color"].blue()
            try:
                color_line.insert(0, (red, green, blue, 200))
                color_rect.insert(0, QColor(red, green, blue, 40))
                color_border.insert(0, (red, green, blue, 0))
            except:
                color_line.append((red, green, blue, 200))
                color_rect.append(QColor(red, green, blue, 40))
                color_border.append((red, green, blue, 0))
        # p = QPainter(self)
        # p.beginNativePainting()
        if len(list_level) >= len(self.fibonacci_levels):
            for i in range(len(list_level) - len(self.fibonacci_levels)):
                target = TextItem("")
                target.setAnchor((1,0.6))
                self.list_lines.append(target)
                self.parent.addItem(target)
        else:
            for i in range(-len(list_level) +len(self.fibonacci_levels)):
                target = self.list_lines.pop()
                self.parent.removeItem(target)

        self.fibonacci_levels = list_level
        self.counts = len(list_level)
        self.colors_rect = color_rect
        self.colors_lines = color_line
        self.colors_borders = color_border

        if "fibo_sp_line" in self.objectName():
            self.chart.main.fibo_special_levels = list_level
            self.chart.main.fibo_special_rects = color_rect
            self.chart.main.fibo_special_colors = color_line
        else:
            self.chart.custom_fibonacci_levels = list_level
            self.chart.custom_colors_rect = color_rect
            self.chart.custom_colors_lines = color_line
            self.chart.custom_colors_borders = color_border

        if hasattr(setting_tool_menu, "cb_trend_line"):
            if setting_tool_menu.cb_trend_line.isChecked():
                self.trend_line = True
            else:
                self.trend_line = False
        if hasattr(setting_tool_menu, "cb_extend_left"):
            if setting_tool_menu.cb_extend_left.isChecked():
                self.extend_to_left(True)
            else:
                self.extend_to_left(False)
            if setting_tool_menu.cb_extend_right.isChecked():
                self.extend_to_right(True)
            else:
                self.extend_to_right(False)
        # move coordinates
        first_date = setting_tool_menu.dt_edit_first.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        first_ele = dt.datetime.strptime(first_date, "%Y-%m-%d %H:%M:%S")
        first_utc = pytz.timezone('UTC').localize(first_ele).timestamp()
        second_date = setting_tool_menu.dt_edit_second.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        second_ele = dt.datetime.strptime(second_date, "%Y-%m-%d %H:%M:%S")
        second_utc = pytz.timezone('UTC').localize(second_ele).timestamp()
        # print(680, first_utc, second_utc, self.handles)
        h1_pre_pos = self.handles[1]["item"].pos()
        se_price = setting_tool_menu.sp_box_second_price.value()
        fi_price = setting_tool_menu.sp_box_first_price.value()
        self.movePoint(1, QPointF(second_utc, se_price))
        self.movePoint(0, QPointF(first_utc, fi_price)) 
        if self.reverse != setting_tool_menu.cb_reverse.isChecked():
            self.reverse = setting_tool_menu.cb_reverse.isChecked()
            if h1_pre_pos == self.handles[1]["item"].pos():
                print("ko chay reverse position")
                self.movePoint(1, QPointF(second_utc+1, se_price*1.001))
                self.movePoint(0, QPointF(first_utc, fi_price)) 
                self.movePoint(1, QPointF(second_utc, se_price))
        
        # print(688, "checking point", h1_pre_pos, self.handles[1]["item"].pos(), h0_pre_pos, self.handles[0]["item"].pos(), first_utc, second_utc)

        self.draw_rec.emit()

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
        # print(621, self.handles, checked)
        pos = self.state["pos"]
        size = self.state["size"]
        if checked:
            self.extend_left = True
            first_time = pos.x()
            second_time = pos.x() + size.x()
            first_price = pos.y()
            second_price = pos.y() + size.y()
            if first_time > second_time:
                self.last_left_pos = second_time
                print(715, "left extend 1")
                self.movePoint(1, QPointF(second_time-60*60, second_price))
            else:
                print(718, "left extend 0", first_price)
                self.last_left_pos = first_time
                self.movePoint(0, QPointF(first_time-60*60, first_price))
            
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
        # print(627, self.handles, checked)
        pos = self.state["pos"]
        size = self.state["size"]
        if checked:
            self.extend_right = True
            first_time = pos.x()
            second_time = pos.x() + size.x()
            first_price = pos.y()
            second_price = pos.y() + size.y()
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
            self.parent.removeItem(item)
        self.parent.removeItem(self)

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
        h0 = self.handles[0]['item']
        h1 = self.handles[1]['item']
        diff = h1.pos() - h0.pos()
        
        if self.size().y() < 0:
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

        else:
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
    
    # def keyPressEvent(self, event: QKeyEvent) -> None:
    #     print(325, "keyPressEvent", event)
    #     return super().keyPressEvent(event)

#########################################################

class FiboSpecialROI(SpecialROI, QWidget):
    on_click = Signal(QObject)
    draw_rec = Signal()
    def __init__(self, pos, size=..., angle=0, invertible=True, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, rotatable=True, resizable=True, removable=False, aspectLocked=False, main=None, fibo_level=None, color_rect=None, color_line=None, color_borders=None,):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked)
        #self.generate_lines()
        self.parent = parent        # vb
        self.chart = main            # mapchart
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 1], [0, 0])
        self.popup_setting_tool = None
        # self.on_click.connect(self.chart.main.show_popup_setting_tool)
        self.precision = self.chart.get_trading_rules_precision(self.chart.symbol)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.movable = movable
        self.locked = False
        self.trend_line = True
        self.extend_left = False
        self.extend_right = False
        # self.installEventFilter(self)
        self.temp_config = {}
        self.list_lines = []
        self.fibonacci_levels = [1.0, 0.786, 0.618, 0.5, 0.382, 0.236, 0.0] 
        self.colors_rect = [QColor(242,54,69,40),QColor(242,54,69,40),QColor(255,152,0,40),QColor(76,175,80,40),QColor(8,153,129,40),QColor(0,188,212,40),QColor(120,123,134,40),QColor(41, 98, 255,40),QColor(242, 54, 69,40),QColor(156,39,176,40),QColor(233, 30, 99,40),QColor(61,90,254,40),QColor(230,81,0,40),QColor(255,23,68,40),QColor(255,64,129,40),QColor(170,0,255,40)]
                        # xam , do, cam, xanh chuoi, xanh la dam, xanh duong, xanh lam dam, do nhat , tim rgb(156 39 176)
        self.colors_lines = [(120,123,134,200),(242,54,69,200),(255,152,0,200),(76,175,80,200),(8,153,129,200),(0,188,212,200),(120,123,134,200),(41, 98, 255,200),(242, 54, 69, 200),(156,39,176,200),(233, 30, 99,200),(206,147,216,200),(159,168,218,200),(255,204,128,200),
                        (229,115,115,200),(244,142,177,200),(66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200)]
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
            target = TextItem("")
            target.setAnchor((1,0.6))
            self.list_lines.append(target)
            self.parent.addItem(target)
        
        # self.destroyed.connect(self.clear_all_texts)

    def change_size_handle(self, size):
        for handle in self.endpoints:
            handle.change_size_handle(size)

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]

    def add_line_fibo(self, line):
        pass

    def add_text(self, counts):
        diff = counts - self.counts
        if diff > 0:
            for i in range(counts):
                target = TextItem("")
                target.setAnchor((1,0.6))
                self.list_lines.append(target)
                self.parent.addItem(target)
            self.counts = len(self.list_lines)

    def update_fibo(self, mapchart_trading, setting_tool_menu):
        # print(161, setting_tool_menu.scrollAreaWidgetContents.findChildren(QWidget, "widget_fibo_lines"))
        list_line_config = setting_tool_menu.scrollAreaWidgetContents.findChildren(QWidget, "widget_fibo_lines")
        list_fibo_level_temp = []
        for wid in list_line_config:
            if wid.cb_on_off.isChecked():
                try:
                    list_fibo_level_temp.append({
                    "per_price": float(wid.txt_per_price.text()),
                    "color": wid.pick_color.color()
                    })
                except ValueError:
                    continue
            if wid.cb_on_off_2.isChecked():
                try:
                    list_fibo_level_temp.append({
                        "per_price": float(wid.txt_per_price_2.text()),
                        "color": wid.pick_color_2.color()
                    })
                except ValueError:
                    continue
        list_fibo_line_sorted = sorted(list_fibo_level_temp, key=itemgetter('per_price'), reverse=True)
        # print(179, list_fibo_line_sorted)   
        list_level = []
        color_rect = []
        color_line = []
        color_border = []
        for line in list_fibo_line_sorted:
            list_level.append(line["per_price"])
            red = line["color"].red()
            green = line["color"].green()
            blue = line["color"].blue()
            try:
                color_line.insert(0, (red, green, blue, 200))
                color_rect.insert(0, QColor(red, green, blue, 40))
                color_border.insert(0, (red, green, blue, 0))
            except:
                color_line.append((red, green, blue, 200))
                color_rect.append(QColor(red, green, blue, 40))
                color_border.append((red, green, blue, 0))
        # p = QPainter(self)
        # p.beginNativePainting()
        if len(list_level) >= len(self.fibonacci_levels):
            for i in range(len(list_level) - len(self.fibonacci_levels)):
                target = TextItem("")
                target.setAnchor((1,0.6))
                self.list_lines.append(target)
                self.parent.addItem(target)
        else:
            for i in range(-len(list_level) +len(self.fibonacci_levels)):
                target = self.list_lines.pop()
                self.parent.removeItem(target)

        self.fibonacci_levels = list_level
        self.counts = len(list_level)
        self.colors_rect = color_rect
        self.colors_lines = color_line
        self.colors_borders = color_border

        if "fibo_sp_line" in self.objectName():
            # print(1113, list_level)
            self.chart.main.fibo_special_levels = list_level
            self.chart.main.fibo_special_colors = color_line
            self.chart.main.fibo_special_rects = color_rect
        else:
            self.chart.custom_fibonacci_levels = list_level
            self.chart.custom_colors_rect = color_rect
            self.chart.custom_colors_lines = color_line
            self.chart.custom_colors_borders = color_border

        if hasattr(setting_tool_menu, "cb_trend_line"):
            if setting_tool_menu.cb_trend_line.isChecked():
                self.trend_line = True
            else:
                self.trend_line = False
        if hasattr(setting_tool_menu, "cb_extend_left"):
            if setting_tool_menu.cb_extend_left.isChecked():
                self.extend_left = True
                self.extend_to_left(True)
            else:
                self.extend_left = False
                self.extend_to_left(False)
            if setting_tool_menu.cb_extend_right.isChecked():
                self.extend_right = True
                self.extend_to_right(True)
            else:
                self.extend_right = False
                self.extend_to_right(False)

        self.draw_rec.emit()

    def extend_to_left(self, checked):
        print(1139, self.chart.fibo_sp_line_levels, self.chart.fibo_sp_line_lines)
    def extend_to_right(self, checked):
        print(627, self.handles, checked)

    def mouseDragEvent(self, ev):
        if not self.locked:
            return super().mouseDragEvent(ev)
        ev.ignore()
        # return super().mouseDragEvent(ev)
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # widget = self.childAt(ev.position().toPoint())
            print(191, ev.pos().toPoint())
            self.on_click.emit(self)
        ev.ignore()
    
    def remove(self):
        for item in self.list_lines:
            # print(156, "remove", item)
            self.parent.removeItem(item)
        self.parent.removeItem(self)

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
    
    def paint(self, p: QPainter, opt, widget):
        # print(576, self.state)
        # max_percent = max(self.fibonacci_levels)
        # min_percent = min(self.fibonacci_levels)
        r = self.boundingRect()
        parentbound = self.parentBounds()
        
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())
        
        if self.size().y() < 0:
            top = self.mapToView(Point(0,0)).y()
            bot = top + self.size().y()
            f = self.precision
            unit = 1/(self.fibonacci_levels[0]-self.fibonacci_levels[-1])
            for i in range(self.counts):
                try:
                    price = round(cal_line_price_fibo(top, bot, self.fibonacci_levels[self.counts - i - 1], -1),f)
                except IndexError:
                    print(567, self.counts - i - 1, len(self.fibonacci_levels))
                text = self.list_lines[i]
                text.percent = self.fibonacci_levels[self.counts - i - 1]
                text.setColor(self.colors_lines[i])
                text.setText(f"{self.fibonacci_levels[self.counts - i - 1]} ({str(price)})" )
                text.setPos(parentbound.x(), price)
                p.setPen(mkPen(self.colors_lines[i],width=1))
                y_line_pointf = (self.fibonacci_levels[self.counts-i-1]-self.fibonacci_levels[-1])*unit
                p.drawLine(QPointF(0,y_line_pointf), QPointF(1,y_line_pointf))
                if i >0:
                    pre_y_line_pointf = (self.fibonacci_levels[self.counts-i]-self.fibonacci_levels[-1])*unit
                    p.setPen(mkPen(self.colors_borders[i]))
                    p.setBrush(self.colors_rect[i]) #QBrush(mkBrush(color))
                    rect =  QRectF(0,y_line_pointf, 1, pre_y_line_pointf - y_line_pointf)
                    p.fillRect(rect, self.colors_rect[i])
            # draw line cheo
            if self.trend_line:
                p.setPen(mkPen(self.colors_lines[-1],width=1, style=Qt.PenStyle.DashLine))
                p.drawLine(QPointF(0, (1-self.fibonacci_levels[-1])*unit), QPointF(1,-self.fibonacci_levels[-1]*unit))
            # print("draw xuong")

        else:
            bot = self.mapToView(Point(0,0)).y()
            top = bot + self.size().y()
            f = self.precision
            unit = 1/(self.fibonacci_levels[0]-self.fibonacci_levels[-1])
            for i in range(self.counts):
                price = round(cal_line_price_fibo(top, bot, self.fibonacci_levels[i]),f)
                text = self.list_lines[i]
                text.percent = self.fibonacci_levels[i]
                text.setColor(self.colors_lines[self.counts - i - 1])
                text.setText(f"{self.fibonacci_levels[i]} ({str(price)})" )
                text.setPos(parentbound.x(), price)
                p.setPen(mkPen(self.colors_lines[i],width=1))
                y_line_pointf = (-self.fibonacci_levels[self.counts-i-1]+self.fibonacci_levels[0])*unit
                p.drawLine(QPointF(0,y_line_pointf), QPointF(1,y_line_pointf))
                if i >0:
                    pre_y_line_pointf = (-self.fibonacci_levels[self.counts-i]+self.fibonacci_levels[0])*unit
                    p.setPen(mkPen(self.colors_borders[i]))
                    p.setBrush(self.colors_rect[i]) #QBrush(mkBrush(color))
                    rect =  QRectF(0,pre_y_line_pointf, 1, -pre_y_line_pointf+y_line_pointf)
                    p.fillRect(rect, self.colors_rect[i])

            # draw line cheo
            if self.trend_line:
                p.setPen(mkPen(self.colors_lines[-1],width=1, style=Qt.PenStyle.DashLine))
                p.drawLine(QPointF(0,(-1+self.fibonacci_levels[0])*unit), QPointF(1,self.fibonacci_levels[0]*unit))
            # print("draw len")
        # p.endNativePainting()
    
    # def keyPressEvent(self, event: QKeyEvent) -> None:
    #     print(325, "keyPressEvent", event)
    #     return super().keyPressEvent(event)

class CustomLineSegmentROI(SpecialROI):
    def __init__(self, positions=(None, None), pos=None, handles=(None,None), point_draggable=True,**args):
        if pos is None:
            pos = [0,0]
            
        SpecialROI.__init__(self, pos, [1,1], **args)
        if len(positions) > 2:
            raise Exception("LineSegmentROI must be defined by exactly 2 positions. For more points, use PolyLineROI.")
        
        for i, p in enumerate(positions):
            self.addFreeHandle(p, item=handles[i])

    def hoverEvent(self, ev):
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
            # self.setMouseHover(True)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
            ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
            self.sigHoverEvent.emit(self)
        else:
            # self.setMouseHover(False)
            self.setCursor(Qt.CursorShape.CrossCursor)
            
    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
        
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def getState(self):
        state = SpecialROI.getState(self)
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = SpecialROI.saveState(self)
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        SpecialROI.setState(self, state)
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

class TextBoxROI(TargetItem):
    on_click = Signal(QObject)
    draw_rec = Signal()

    signal_change_font_size = Signal(int)

    def __init__(self, pos=None, size=10,id=None, symbol= "o", pen=None, hoverPen=None, brush=None, hoverBrush=None, movable=True, label=None, labelOpts=None, parent=None, main=None):
        super().__init__(pos, size, symbol, pen, hoverPen, brush, hoverBrush, movable, label, labelOpts)
        self.uid = None
        self.id = id
        self.locked = False
        self.parent, self.chart=parent, main
        self.is_selected = False
        self.on_click.connect(self.chart.main.show_popup_setting_tool)
        # self.on_click.connect(self.get_pos_point)

        self.signal_change_font_size.connect(self.change_font_size)
        self.color =  "#F4511E"
        self.font_size = 14
        self.name = ''
        self.setLabel("Text",
                        {
                            "anchor": QtCore.QPointF(0.5, 0.5),
                            "offset": QtCore.QPointF(0, 30),
                            "color": self.color,
                        }
                        )

        self.update_html(self.color, self.font_size)
        self.setBrush(QColor("#1ec2f4"))

    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            # self.setSelected(True)
            # self.change_size_handle(3)
        else:
            self.isSelected = False
            # self.setSelected(False)
            # self.change_size_handle(4)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name

    def update_text_item(self, main_chart, setting_menu):
        updated_text = setting_menu.plain_textedit.toPlainText()
        self.update_html(text=updated_text)
        self.draw_rec.emit()
    
    def update_html(self, color="#F4511E",font_size=14, text="Text"):
        self.color =  color
        self.font_size = font_size
        self.html = f"""<div style="text-align: center">
    <span style="color: {color}; font-size: {font_size}pt;">{text}</span>"""
        self.label().setHtml(self.html)

    def getText(self):
        return self.label().toPlainText()
    
    def get_pos_point(self):
        return self.pos()

    def locked_handle(self):
        self.movable = False

    def unlocked_handle(self):
        self.movable = True

    def change_color(self, color):
        r, g, b = color[0], color[1], color[2]
        self.color = QColor(r, g, b).name()
        text = self.getText()
        self.update_html(color=self.color, text=text)

    def change_font_size(self, size):
        text = self.getText()
        self.update_html(color=self.color, text=text, font_size=size)

    def mouseDragEvent(self, ev, axis=None, line=None):
        if not self.locked:
            return super().mouseDragEvent(ev)
        elif self.locked:
            ev.ignore()
        ev.ignore()

    def mouseDoubleClickEvent(self, event) -> None:
        # print(325, "mouseDoubleClickEvent", event)
        return super().mouseDoubleClickEvent(event)
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # widget = self.childAt(ev.position().toPoint())
            # print(191, ev.pos().toPoint())
            self.on_click.emit(self)
        # print(647, self.pos(), self.state)
        ev.ignore()
        #return super().mouseClickEvent(event)


def cal_line_price_fibo(top, bot, percent, direct=1):

    diff = (top - bot) * percent
    if direct == 1:
        return top - diff
    return bot + diff

