# import sys
import math
import sys
from math import atan2, degrees
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QMainWindow
from numpy import degrees
# from numpy.array_api import atan2
from pyqtgraph import GraphicsLayoutWidget, InfiniteLine, Point, mkBrush, mkPen, PlotWidget, RectROI, ROI
import pyqtgraph as pg
import numpy as np
from pyqtgraph import *

from typing import Dict, Tuple, List,TYPE_CHECKING
import numpy as np

from PySide6.QtCore import Signal, QRect, QRectF, QPointF,QThreadPool,Qt,QLineF,QCoreApplication
from PySide6.QtGui import QPainter, QPicture,QPainterPath
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget


class Rectangle(RectROI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paint(self, p, opt, widget):
        # Note: don't use self.boundingRect here, because subclasses may need to redefine it.
        r = QtCore.QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()

        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())

        brush = QBrush()
        brush.setColor(self.color)  # QColor(154, 14, 235, 30)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        p.setBrush(brush)

        p.drawRect(0, 0, 1, 1)

    def movePoint(self, handle, pos, modifiers=None, finish=True, coords='parent'):
        ## called by Handles when they are moved.
        ## pos is the new position of the handle in scene coords, as requested by the handle.
        if modifiers is None:
            modifiers = QtCore.Qt.KeyboardModifier.NoModifier
        newState = self.stateCopy()
        index = self.indexOfHandle(handle)
        h = self.handles[index]
        p0 = self.mapToParent(h['pos'] * self.state['size'])
        p1 = Point(pos)

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
            print(lp1)

        if h['type'] == 't':
            snap = True if (modifiers & QtCore.Qt.KeyboardModifier.ControlModifier) else None
            self.translate(p1 - p0, snap=snap, update=False)

        elif h['type'] == 'f':
            newPos = self.mapFromParent(p1)
            h['item'].setPos(newPos)
            h['pos'] = newPos
            self.freeHandleMoved = True

        elif h['type'] == 's':
            
            ## If a handle and its center have the same x or y value, we can't scale across that axis.
            if h['center'][0] == h['pos'][0]:
                lp1[0] = 0
            if h['center'][1] == h['pos'][1]:
                lp1[1] = 0

            ## snap
            if self.scaleSnap or (modifiers & QtCore.Qt.KeyboardModifier.ControlModifier):
                lp1[0] = round(lp1[0] / self.scaleSnapSize) * self.scaleSnapSize
                lp1[1] = round(lp1[1] / self.scaleSnapSize) * self.scaleSnapSize

            ## preserve aspect ratio (this can override snapping)
            if h['lockAspect'] or (modifiers & QtCore.Qt.KeyboardModifier.AltModifier):
                # arv = Point(self.preMoveState['size']) -
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
            # if not self.invertible:
            #     if newSize[0] < 0:
            #         newSize[0] = newState['size'][0]
            #     if newSize[1] < 0:
            #         newSize[1] = newState['size'][1]
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
            if self.rotateSnap or (modifiers & QtCore.Qt.KeyboardModifier.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle

            ## create rotation transform
            tr = QtGui.QTransform()
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
            if self.rotateSnap or (modifiers & QtCore.Qt.KeyboardModifier.ControlModifier):
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
            tr = QtGui.QTransform()
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

