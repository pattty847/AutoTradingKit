# import sys
# from numpy.array_api import atan2
from pyqtgraph import ROI
from PySide6.QtGui import QPainter
from PySide6.QtCore import QRectF,QPointF

from atklip.app_utils.functions import mkBrush, mkPen


class BaseRect(ROI):
    def __init__(self, pos, size, centered=False, sideScalers=False,is_short=False,is_long=False, **args):
        ROI.__init__(self, pos, size, **args)
        
        self.has = {
            "styles":{
                    'pen': None,
                    'brush': mkBrush((43, 106, 255, 40)),
                    'width': 1}
        }
        self.brush = self.has["styles"]['brush']
        self.is_short:bool = is_short
        self.is_long:bool = is_long
        
        
    
    def setBrush(self,brush):
        self.has["styles"]['brush'] = brush
    
    def boundingRect(self):
        return QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
    
    def paint(self, p:QPainter, opt, widget):
        # Note: don't use self.boundingRect here, because subclasses may need to redefine it.
        r = QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
        p.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            self._antialias
        )
        p.setPen(mkPen(self.has["styles"]['pen']))
        p.setBrush(self.has["styles"]["brush"])
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())
        p.drawRect(0, 0, 1, 1)
        if self.is_short:
            p.setPen(mkPen("red",width=1))
            p.drawLine(QPointF(0,0), QPointF(1,0))
            p.setPen(mkPen("w",width=1))
            p.drawLine(QPointF(0,1), QPointF(1,1))
        if self.is_long:
            p.setPen(mkPen("green",width=1))
            p.drawLine(QPointF(0,0), QPointF(1,0))
            p.setPen(mkPen("w",width=1))
            p.drawLine(QPointF(0,1), QPointF(1,1))
        