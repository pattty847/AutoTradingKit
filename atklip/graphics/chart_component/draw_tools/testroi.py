# import numpy as np

# import pyqtgraph as pg
# from atklip.graph_objects.pyqtgraph.graphicsItems.ROI import RulerROI
# from atklip.graph_objects.pyqtgraph.Qt import QtCore, QtWidgets

# app = pg.mkQApp("Arrow Example")

# w = QtWidgets.QMainWindow()
# cw = pg.GraphicsLayoutWidget()
# w.show()
# w.resize(400,600)
# w.setCentralWidget(cw)
# w.setWindowTitle('pyqtgraph example: Arrow')

# p = cw.addPlot(row=0, col=0)
# p2 = cw.addPlot(row=1, col=0)

# ## variety of arrow shapes
# a1 = pg.ArrowItem(angle=-160, tipAngle=60, headLen=40, tailLen=40, tailWidth=20, pen={'color': 'w', 'width': 3})
# a2 = pg.ArrowItem(angle=0, tipAngle=30, baseAngle=20, headLen=10, tailLen=80, tailWidth=1, pen=None, brush='y')
# a3 = pg.ArrowItem(angle=-60, baseAngle=20, headLen=40, headWidth=20, tailLen=None, brush=None)
# a4 = RulerROI((30,0))
# a2.setPos(10,0)
# a3.setPos(20,0)
# #a4.setPos(30,0)
# p.addItem(a1)
# p.addItem(a2)
# p.addItem(a3)
# p.addItem(a4)
# p.setRange(QtCore.QRectF(-20, -10, 60, 20))


# ## Animated arrow following curve
# c = p2.plot(x=np.sin(np.linspace(0, 2*np.pi, 1000)), y=np.cos(np.linspace(0, 6*np.pi, 1000)))
# a = pg.CurveArrow(c)
# a.setStyle(headLen=40)
# p2.addItem(a)
# anim = a.makeAnimation(loop=-1)
# anim.start()

# if __name__ == '__main__':
#     pg.exec()
import sys

from PySide6 import QtCore, QtNetwork, QtWidgets


class CheckConnectivity(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        url = QtCore.QUrl("https://www.google.com/")
        req = QtNetwork.QNetworkRequest(url)
        self.net_manager = QtNetwork.QNetworkAccessManager()
        self.msg = QtWidgets.QMessageBox()

        self.res = self.net_manager.get(req)
        self.res.finished.connect(self.processRes)
        self.res.errorOccurred.connect(self.processErr)
        # sleep(5)

    @QtCore.Slot()
    def processRes(self):
        if self.res.bytesAvailable():
            self.msg.information(None, "Info", "You are connected to the Internet.")
        self.res.deleteLater()

    @QtCore.Slot(QtNetwork.QNetworkReply.NetworkError)
    def processErr(self, code):
        self.msg.critical(None, "Info", "You are not connected to the Internet.")
        print(code)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # win = QtWidgets.QWidget()
    # win.show()
    ic = CheckConnectivity()
    sys.exit(app.exec())
