"""
Real-time quotes charting components
"""
import pyqtgraph as pg
from PySide6 import QtCore, QtGui,QtWidgets
from PySide6.QtGui import QPainter

from atklip.app_utils.functions import mkBrush


# TODO: test this out as our help menu
class CenteredTextItem(QtWidgets.QGraphicsTextItem):
    def __init__(
        self,
        text='',
        parent=None,
        pos=(0, 0),
        pen=None,
        brush=None,
        valign=QtCore.Qt.AlignBottom,
        opacity=0.1,
    ):
        super().__init__(text, parent)

        self.pen = pen
        self.brush = mkBrush(brush)
        self.opacity = opacity
        self.valign = valign
        self.text_flags = QtCore.Qt.AlignCenter
        self.setPos(*pos)
        self.setFlag(self.GraphicsItemFlag.ItemIgnoresTransformations)

    def boundingRect(self):  # noqa
        r = super().boundingRect()
        if self.valign == QtCore.Qt.AlignTop:
            return QtCore.QRectF(-r.width() / 2, -37, r.width(), r.height())
        elif self.valign == QtCore.Qt.AlignBottom:
            return QtCore.QRectF(-r.width() / 2, 15, r.width(), r.height())

    def paint(self, p, option, widget):
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        p.setPen(self.pen)
        if self.brush.style() != QtCore.Qt.NoBrush:
            p.setOpacity(self.opacity)
            p.fillRect(option.rect, self.brush)
            p.setOpacity(1)
        p.drawText(option.rect, self.text_flags, self.toPlainText())