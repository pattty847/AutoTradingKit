from typing import Tuple, List

import numpy as np
import pandas as pd

from atklip.graphics.pyqtgraph import *
from atklip.graphics.pyqtgraph import functions as fn

from PySide6.QtCore import Signal, QObject, QRectF, QPointF,QThreadPool,Qt
from PySide6.QtGui import QPainter, QPicture,QColor

from atklip.controls.talipp import INDICATOR, IndicatorType
from atklip.controls.talipp.ohlcv import OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI

from atklip.appmanager import FastWorker
from atklip.app_utils import *

class BasicSPTrend(PlotDataItem):
    """RSI"""
    on_click = Signal(QObject)

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)

    def __init__(self, lastcandle,jp_candle: JAPAN_CANDLE|HEIKINASHI=[],pen:str="yellow",atr_period:int=10,mult:int=3,ma_time_frame=None,id = None,symbol='',interval='',clickable=True) -> None:
        """Choose colors of candle"""
        super().__init__(clickable=clickable)

        self.jp_candle = jp_candle
        self.opts.update({'pen':pen})
        self.indicator_name = f"SMA {atr_period}"
        self.id = id
        self.atr_period = atr_period
        self.mult = mult
        self.spt_time_frame = ma_time_frame
        self.symbol = symbol
        self.interval = interval
        
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(1)

        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)

        self.spt = INDICATOR.SuperTrend(atr_period=self.atr_period,
                                input_values = self.jp_candle.candles,
                                input_indicator = None,
                                input_modifier = None,
                                input_sampling = None,
                                mult = self.mult) 

        output_times = []
        output_values = []

        [self.remove_none_value(output_times,output_values,i) for i  in range(len(self.spt.output_values)) if self.spt.output_values[i] != None]

        self.set_Data((output_times[:-1],output_values[:-1]))

        self.LastPointLine = CurrentSPTrend(lastcandle= lastcandle,jp_candle= jp_candle,atr_period=atr_period,mult=mult,pen=pen)
        self.LastPointLine.setParentItem(self)

        lastcandle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)

    def remove_none_value(self,output_times,output_values,i):
        output_times.append(self.spt.output_times[i])
        output_values.append(self.spt.output_values[i])

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

    def percent_caculator(self,start, stop):
        percent = float(((float(start) - float(stop)) / float(start))) * 100
        if percent > 0:
            return percent
        else:
            return abs(percent)
    
    def setdata_worker(self,lastcandle):
        self.worker = None
        self.worker = FastWorker(self.threadpool,self.update_data,lastcandle)
        self.worker.signals.setdata.connect(self.set_Data)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def set_Data(self,data):

        xData = data[0]
        yData = data[1]

        self.setData(xData, yData)
        self.update()


    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,_value

    
    def update_data(self,last_candle:List[OHLCV],setdata):
        # self.spt = SMA(atr_period=self.atr_period,input_values=self.jp_candle.candles,_type=self._type)
        _last_sma_time = self.spt.output_times[-1]
        _last_time, _last_value = getspecialvalues(self._type,last_candle)
        if _last_sma_time == _last_time:
            self.spt.update(last_candle[-1])
        else:
            self.spt.add(last_candle[-1])
            output_times = []
            output_values = []
            [self.remove_none_value(output_times,output_values,i) for i  in range(len(self.spt.output_values)) if self.spt.output_values[i] != None]
            setdata.emit((output_times[:-1],output_values[:-1]))
    
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
    
    def setMaLeng(self, atr_period):
        self.atr_period = atr_period
    
    def getMaLeng(self):
        return self.atr_period
    
    def setIndicatorType(self, _type):
        self._type = _type

    def getIndicatorType(self):
        return self._type


    def setMaTimeFrame(self, ma_time_frame):
        self.spt_time_frame = ma_time_frame
    
    def getMaTimeFrame(self):
        return self.spt_time_frame


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

class CurrentSPTrend(PlotDataItem):
    """Zigzag plot"""
    on_click = Signal(QObject)

    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)

    def __init__(self, lastcandle,jp_candle: JAPAN_CANDLE|HEIKINASHI=[],pen:str="yellow",atr_period:int=10,mult:int=3,ma_time_frame=None,id = None,symbol='',interval='',clickable=True) -> None:
        """Choose colors of candle"""
        super().__init__(clickable=clickable)

        self.opts.update({'pen':pen})
        self.indicator_name = f"SMA {atr_period}"
        self.id = id
        self.atr_period = atr_period
        self.mult = mult
        self.spt_time_frame = ma_time_frame
        self.symbol = symbol
        self.interval = interval

        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        self.signal_change_color.connect(self.change_color)
        self.signal_change_width.connect(self.change_width)
        self.signal_change_type.connect(self.change_type)

        self.spt = INDICATOR.SuperTrend(atr_period=self.atr_period,
                                input_values = jp_candle.candles,
                                input_indicator = None,
                                input_modifier = None,
                                input_sampling = None,
                                mult = self.mult) 
        
        lastcandle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)

    
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

    
    
    def setdata_worker(self,lastcandle):
        self.worker = None
        self.worker = FastWorker(self.threadpool,self.update_data,lastcandle)
        self.worker.signals.setdata.connect(self.set_Data)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def set_Data(self,data):
        xData = data[0]
        yData = data[1]
        self.setData(xData, yData)
        self.update()

    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,_value

    def update_data(self,last_candle:List[OHLCV],setdata):
        # self.spt = SMA(atr_period=self.atr_period,input_values=self.jp_candle.candles,_type=self._type)
        _last_sma_time = self.spt.output_times[-1]
        _last_time, _last_value = self.getspecialvalues(self._type,last_candle)
        if _last_sma_time == _last_time:
            self.spt.update(last_candle[-1])
        else:
            self.spt.add(last_candle[-1])
        setdata.emit((self.spt.output_times[-2:],self.spt.output_values[-2:]))

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
    
    def setMaLeng(self, atr_period):
        self.atr_period = atr_period
    
    def getMaLeng(self):
        return self.atr_period
    
    def setIndicatorType(self, _type):
        self._type = _type

    def getIndicatorType(self):
        return self._type


    def setMaTimeFrame(self, ma_time_frame):
        self.spt_time_frame = ma_time_frame
    
    def getMaTimeFrame(self):
        return self.spt_time_frame


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
