import numpy as np
from atklip.graph_objects.pyqtgraph import PlotDataItem,GraphicsObject
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QPen,QBrush,QPicture, QPainter
from PySide6.QtWidgets import QGraphicsItem


class PlotLineItem(GraphicsObject):
    """Line plot"""
    def __init__(self, *args, **kargs):
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setZValue(999)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemAcceptsInputMethod, False)
        # self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        # self.setProperty('xViewRangeWasChanged', True)
        # self.setProperty('yViewRangeWasChanged', True)
        self.picture = QPicture()
        self._line = PlotDataItem(*args, **kargs)
        self._line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self._line.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self._line.setParentItem(self)
        self.opts = self._line.opts
    # @property
    # def xData(self):
    #     return self._line.xData
    # @property
    # def yData(self):
    #     return self._line.yData
    def setPen(self, *args, **kargs):
        self._line.setPen(self, *args, **kargs)
    def setData(self, *args, **kargs):
        self._line.setData(*args, **kargs)
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
    def boundingRect(self) -> QRectF:
        return self._line.boundingRect()
    def paint(self,p:QPainter,*args):
        self.picture.play(p)