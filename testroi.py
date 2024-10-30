import numpy as np

import pyqtgraph as pg
from atklip.graphics.pyqtgraph.graphicsItems.ROI import RulerROI
from atklip.graphics.pyqtgraph.Qt import QtCore, QtWidgets

app = pg.mkQApp("Arrow Example")

w = QtWidgets.QMainWindow()
cw = pg.GraphicsLayoutWidget()
w.show()
w.resize(400,600)
w.setCentralWidget(cw)
w.setWindowTitle('pyqtgraph example: Arrow')

p = cw.addPlot(row=0, col=0)
p2 = cw.addPlot(row=1, col=0)

## variety of arrow shapes
a1 = pg.ArrowItem(angle=-160, tipAngle=60, headLen=40, tailLen=40, tailWidth=20, pen={'color': 'w', 'width': 3},pxMode=False)
a2 = pg.ArrowItem(angle=0, tipAngle=60, baseAngle=30, headLen=20, tailLen=100, tailWidth=2, pen=None, brush='green')
a3 = pg.ArrowItem(angle=-60, baseAngle=20, headLen=40, headWidth=20, tailLen=None, brush=None)
a4 = RulerROI((30,0))
a2.setPos(0,0)
a3.setPos(20,0)
#a4.setPos(30,0)
p.addItem(a1)
p.addItem(a2)
p.addItem(a3)
p.addItem(a4)
p.setRange(QtCore.QRectF(-20, -10, 60, 20))


## Animated arrow following curve
c = p2.plot(x=np.sin(np.linspace(0, 2*np.pi, 1000)), y=np.cos(np.linspace(0, 6*np.pi, 1000)))
a = pg.CurveArrow(c)
a.setStyle(headLen=40)
p2.addItem(a)
anim = a.makeAnimation(loop=-1)
anim.start()

if __name__ == '__main__':
    pg.exec()
