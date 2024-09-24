from PySide6.QtGui import QColor
from pyqtgraph import *


class CustomReplayObject(GraphicsObject):
    sigPlotChanged = QtCore.Signal(object)
    def __init__(self) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.has = {
            "name": "rectangle",
            "type": "drawtool",
            "id": id
        }
        self.picture = QtGui.QPicture()
        self.colorline = 'white'
        self.setAcceptHoverEvents(True)
        
        
    def paint(self, p: QtGui.QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QtCore.QRect:
        return QtCore.QRectF(self.picture.boundingRect())
    def set_data(self,x0,x1,h0, h1):

        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        #p.setPen(self.outline_pen)
        
        #high_brush = mkBrush('#0ecb81',width=1)
        #outline_pen = mkPen(color='#0ecb81',width=1)
        
        #p.setPen(outline_pen)
        p.setBrush(QColor(55,55,55,150))
        
        #print(x0, h1, x1, h0)
        
        p.drawRect(QtCore.QRectF(x0, h0, x1, h1))
        p.end()

        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        # self.bounds = [None, None]
        # self.sigPlotChanged.emit(self)
    
    # def getData(self) -> Tuple[List[float], List[Tuple[float, ...]]]:
    #     return self.x_data, self.y_data

    def hoverEnterEvent(self, ev):
        #data = self.getData()
        #print(data)
        ev.accept()
        
    def hoverLeaveEvent(self, ev):
        self.brush = mkBrush('g')
        self.update()
        ev.accept()

        """ _summary_
    mousePressEvent(ev): Sự kiện này được gọi khi người dùng nhấn chuột trái, phải hoặc giữa trên GraphicsObject.

    mouseMoveEvent(ev): Sự kiện này được gọi khi chuột di chuyển trên GraphicsObject.

    mouseReleaseEvent(ev): Sự kiện này được gọi khi người dùng nhả chuột trái, phải hoặc giữa trên GraphicsObject.

    wheelEvent(ev): Sự kiện này được gọi khi người dùng cuộn chuột trên GraphicsObject.

    keyPressEvent(ev): Sự kiện này được gọi khi người dùng nhấn một phím trên bàn phím khi GraphicsObject đang được chọn.

    keyReleaseEvent(ev): Sự kiện này được gọi khi người dùng nhả phím trên bàn phím khi GraphicsObject đang được chọn.
        _extended_summary_
        """



