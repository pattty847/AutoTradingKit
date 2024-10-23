import datetime as dt
from operator import itemgetter
import random
import pytz
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Signal, QPointF, Qt, QRectF, QCoreApplication
from PySide6.QtGui import QPainter, QColor,QTextItem
from PySide6.QtWidgets import QWidget
from atklip.graphics.pyqtgraph import TextItem, mkPen
from atklip.graphics.pyqtgraph.Point import Point


class BaseTextItem(TextItem):
    def __init__(self, text='', color=(200,200,200), html=None, anchor=(0,0),
                 border=None, fill=None, angle=0, rotateAxis=None, ensureInBounds=False):
        super().__init__(text=text, color=color, html=html, anchor=anchor,
                 border=border, fill=fill, angle=angle, rotateAxis=rotateAxis, ensureInBounds=ensureInBounds)
    
    def updateTextPos(self):
        pass

    def updatePos(self,y_line_pointf:float=0):
        # update text position to obey anchor
        r = self.textItem.boundingRect()
        tl = self.textItem.mapToParent(r.topLeft())
        br = self.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.anchor
        p = self.parentItem()
        if p is not None:
            prb = p.boundingRect()
            x,y,w,h = prb.x(),prb.y(),prb.width(),prb.height()
            _x = -offset.x() + x
            mapFromParent = self.mapFromParent(Point(0,y_line_pointf))
            _y = self.anchor.y() + mapFromParent.y()
            # print(_x,_y,mapFromParent,y_line_pointf, prb.height(),offset)
            pos = Point(_x,_y)
            self.textItem.setPos(pos)
