from typing import Tuple

import numpy as np
from PySide6.QtCore import Signal, Qt, QObject
from PySide6.QtGui import QColor
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.graphics.pyqtgraph import functions as fn

from atklip.app_utils import *

class BasicZigzag(PlotDataItem):
    """Zigzag plot"""
    on_click = Signal(QObject)

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)

    def __init__(self,pen, chart=None, indicator_name='',percent=2,pivot_leg=2,id = None,symbol='',interval='',clickable=True) -> None:
        """Choose colors of candle"""
        super().__init__(clickable=clickable)
        self.chart = chart
        self.opts.update({'pen':pen})
        self.indicator_name = indicator_name
        self.id = id
        self.percent = percent
        self.pivot_leg = pivot_leg
        self.symbol = symbol
        self.interval = interval
        self.on_click.connect(self.on_click_event)

        self.chart.emit_data.connect(self.update_data)

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)

        #self.dataconnect = DataConnector(win=self.chart, plot=self)

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()
    
    def delete(self):
        self.deleteLater()

    
    def change_type(self, type_):
        if type_ == "SolidLine":
            self.currentPen.setStyle(Qt.PenStyle.SolidLine)
        elif type_ == "DashLine":
            self.currentPen.setStyle(Qt.PenStyle.DashLine)
        elif type_ == "DotLine":
            self.currentPen.setStyle(Qt.PenStyle.DotLine)
        self.setPen(self.currentPen)
        self.update()

    def change_width(self, width):
        self.currentPen.setWidth(width)
        self.setPen(self.currentPen)
        self.update()

    def change_color(self, color):
        r, g, b = color[0], color[1], color[2]
        color = QColor(r, g, b)
        self.currentPen.setColor(color)
        self.setPen(self.currentPen)
        self.update()

    async def update_data(self, data):
        candle_timedata = data[0]
        candle_data = data[1]
        list_zizgzag = [[candle_timedata[0],candle_data[0][2],'low'],[candle_timedata[0],candle_data[0][3],'high']]
        for i in range(len(candle_timedata)):
            if percent_caculator(list_zizgzag[0][1],list_zizgzag[1][1]) < self.percent:
                    if list_zizgzag[0][2] == 'low':
                        if list_zizgzag[0][1] > candle_data[i][2]:
                            list_zizgzag.pop(0)
                            list_zizgzag.append([candle_timedata[i],candle_data[i][2],'low'])
                        elif list_zizgzag[1][1] < candle_data[i][3]:
                            list_zizgzag.pop()
                            list_zizgzag.append([candle_timedata[i],candle_data[i][3],'high'])
                    elif list_zizgzag[0][2] == 'high':
                        if list_zizgzag[0][1] < candle_data[i][3]:
                            list_zizgzag.pop(0)
                            list_zizgzag.append([candle_timedata[i],candle_data[i][3],'high'])
                        elif list_zizgzag[1][1] > candle_data[i][2]:
                            list_zizgzag.pop()
                            list_zizgzag.append([candle_timedata[i],candle_data[i][2],'low'])
            else:
                if list_zizgzag[-1][2] == 'low':
                    if percent_caculator(list_zizgzag[-1][1],candle_data[i][3]) > self.percent:
                        list_zizgzag.append([candle_timedata[i],candle_data[i][3],'high'])
                    elif list_zizgzag[-1][1] > candle_data[i][2]:
                        list_zizgzag.pop()
                        list_zizgzag.append([candle_timedata[i],candle_data[i][2],'low'])
                elif list_zizgzag[-1][2] == 'high':
                    if percent_caculator(list_zizgzag[-1][1],candle_data[i][2]) > self.percent:
                        list_zizgzag.append([candle_timedata[i],candle_data[i][2],'low'])
                    elif list_zizgzag[-1][1] < candle_data[i][3]:
                        list_zizgzag.pop()
                        list_zizgzag.append([candle_timedata[i],candle_data[i][3],'high'])
        
        if len(list_zizgzag) == 2:
            if percent_caculator(list_zizgzag[0][1],list_zizgzag[1][1]) >= self.percent:
                x_data = [x[0] for x in list_zizgzag]
                y_data = [x[1] for x in list_zizgzag]   
            else:
                x_data,y_data = [],[]
        else:
            x_data = [x[0] for x in list_zizgzag]
            y_data = [x[1] for x in list_zizgzag]       
        if x_data != [] and y_data != []: 
            self.setData(x_data,y_data)
        #self.indicator.setData(data)
    def on_click_event(self):
        print("zooo day__________________")
        pass

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)

        super().mouseClickEvent(ev)


    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    
    def setPercent(self, percent):
        self.percent = percent
    
    def getPercent(self):
        return self.percent
    
    def setPivotLeg(self, pivot_leg):
        self.pivot_leg = pivot_leg

    def getPivotLeg(self):
        return self.pivot_leg

    def setPen(self, *args, **kargs):
        """
        Sets the pen used to draw lines between points.
        The argument can be a :class:`QtGui.QPen` or any combination of arguments accepted by 
        :func:`pyqtgraph.mkPen() <pyqtgraph.mkPen>`.
        """
        pen = fn.mkPen(*args, **kargs)
        self.opts['pen'] = pen
        self.currentPen = pen
        #self.curve.setPen(pen)
        #for c in self.curves:
            #c.setPen(pen)
        self.update()
        self.updateItems(styleUpdate=True)

    def data_bounds(self, ax=0, offset=0) -> Tuple:
        x, y = self.getData()
        if ax == 0:
            sub_range = x[-offset:]
        else:
            sub_range = y[-offset:]
        return np.nanmin(sub_range), np.nanmax(sub_range)
