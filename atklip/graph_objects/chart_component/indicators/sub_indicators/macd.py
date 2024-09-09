from typing import Tuple, List,TYPE_CHECKING
import numpy as np
import time

import pandas as pd
from atklip.graph_objects.pyqtgraph import GraphicsObject, GraphicsItem, PlotDataItem
from atklip.graph_objects.pyqtgraph import functions as fn
from atklip.graph_objects.chart_component.base_items import PriceLine,PlotLineItem
from PySide6.QtCore import Signal, QObject, QThreadPool,Qt,QRectF,QCoreApplication
from PySide6.QtGui import QColor,QPicture,QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.indicators import PD_MAType,IndicatorType
from atklip.indicators import pandas_ta as ta
from atklip.indicators import OHLCV

from atklip.indicators.candle import JAPAN_CANDLE,HEIKINASHI
from .macd_histogram import MACDHistogram
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graph_objects.chart_component.viewchart import Chart
    from atklip.graph_objects.chart_component.sub_panel_indicator import ViewSubPanel
    
class BasicMACD(GraphicsObject):
    """RSI"""
    on_click = Signal(QObject)

    last_pos = Signal(tuple)
    
    sig_update_histogram = Signal(tuple)
    
    sig_reset_histogram = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker,chart,panel,id = None,clickable=True) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        #super().__init__(clickable=clickable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self.panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has = {
            "name": f"MACD 9 12 26",
            "y_axis_show":True,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "indicator_type":IndicatorType.MACD,
                    "fast_period":12,
                    "slow_period":26,
                    "signal_period":9,
                    "ma_type":PD_MAType.EMA,
                    "price_high":60,
                    "price_low":-60,
                    "show":True},

            "styles":{
                    'pen_macd_line': "red",
                    'width_macd_line': 1,
                    'style_macd_line': Qt.PenStyle.SolidLine,
                    'pen_signal_line': "orange",
                    'width_signal_line': 1,
                    'style_signal_line': Qt.PenStyle.SolidLine,
                    "pen_high_historgram": '#089981',
                    "pen_low_historgram" : '#f23645',
                    "brush_high_historgram":mkBrush('#089981',width=0.7),
                    "brush_low_historgram":mkBrush('#f23645',width=0.7)
                    }
                    }
     
        self.id = id
        

        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        
        self.macd_line = PlotDataItem(pen="red")  # for z value
        self.macd_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.macd_line.setParentItem(self)
        self.signal = PlotDataItem(pen="orange")
        self.signal.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.signal.setParentItem(self)
        
        self._INDICATOR : pd.DataFrame = pd.DataFrame([])

        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        
        self.price_high = PriceLine(color="green",width=2,movable=True)  # for z value
        self.price_high.setParentItem(self)
        self.price_high.setPos(self.has["inputs"]["price_high"])
        
        self.price_low = PriceLine(color="red",width=2,movable=True)  # for z value
        self.price_low.setParentItem(self)
        self.price_low.setPos(self.has["inputs"]["price_low"])
        
        self.histogram = MACDHistogram(self.chart,self.panel,self.sig_reset_histogram,self.sig_update_histogram,self.has)
        self.histogram.setParentItem(self)

        self.picture: QPicture = QPicture()
        
        self.destroyed.connect(self.price_line.deleteLater)
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)
        self.chart.sig_remove_source.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
        

        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        
    def delete(self):
        self.chart.sig_remove_item.emit(self)
    
    def disconnect_connection(self):
        try:
            self.has["inputs"]["source"].sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.has["inputs"]["source"].sig_update_candle.disconnect(self.setdata_worker)
            self.has["inputs"]["source"].sig_add_candle.disconnect(self.threadpool_asyncworker)
        except Exception as e:
                    pass
    
    def reset_indicator(self):
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.macd(close=df[f"{self.has["inputs"]["type"]}"],
                                  fast=self.has["inputs"]["fast_period"],
                                  slow=self.has["inputs"]["slow_period"],
                                  signal = self.has["inputs"]["signal_period"],
                                  mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

        column_names = self._INDICATOR.columns.tolist()
        
        macd_name = ''
        histogram_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("MACD"):
                macd_name = name
            elif name.__contains__("HISTOGRAM"):
                histogram_name = name
            elif name.__contains__("SIGNAL"):
                signalma_name = name

        macd = self._INDICATOR[macd_name].to_numpy()
        histogram = self._INDICATOR[histogram_name].to_numpy()
        signalma = self._INDICATOR[signalma_name].to_numpy()
        xdata = df["index"].to_numpy()
        
        self.has["name"] = f"MACD {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.histogram.setData((xdata,histogram))
        
        self.set_Data((xdata,macd,signalma,histogram))
        
        self.sig_change_yaxis_range.emit()
        
        #QCoreApplication.processEvents()
        
        
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        

    def replace_source(self,source_name):
        if self.has["inputs"]["source_name"] == source_name:
            self.disconnect_connection()
            self.has["inputs"]["source"] = self.chart.jp_candle
            self.has["inputs"]["source_name"] = self.chart.jp_candle.source_name
            self.reset_indicator()
            
    def reset_threadpool_asyncworker(self):
        self.disconnect_connection()
        source_name = self.has["inputs"]["source_name"].split(" ")[0]
        self.has["inputs"]["source"].source_name = f"{source_name} {self.chart.symbol} {self.chart.interval}"
        self.chart.update_sources(self.has["inputs"]["source"])
        self.reset_indicator()

    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
            
    def update_inputs(self,_input,_source):
        """"source":self.has["inputs"]["source"],
                "ma_type":self.has["inputs"]["ma_type"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.disconnect_connection()
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.chart.update_sources(self.has["inputs"]["source"])
                self.reset_indicator()
        elif _input == "price_high":
            if _source != self.has["inputs"]["price_high"]:
                self.has["inputs"]["price_high"] = _source
                self.price_high.setPos(_source)
        elif _input == "price_low":
            if _source != self.has["inputs"]["price_low"]:
                self.has["inputs"]["price_low"] = _source
                self.price_low.setPos(_source)
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True
        if update:
            self.has["name"] = f"MACD {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.threadpool_asyncworker()
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "fast_period":self.has["inputs"]["fast_period"],
                    "slow_period":self.has["inputs"]["slow_period"],
                    "signal_period":self.has["inputs"]["signal_period"],
                    "ma_type":self.has["inputs"]["ma_type"],
                    "price_high":self.has["inputs"]["price_high"],
                    "price_low":self.has["inputs"]["price_low"]}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_macd_line":self.has["styles"]["pen_macd_line"],
                    "width_macd_line":self.has["styles"]["width_macd_line"],
                    "style_macd_line":self.has["styles"]["style_macd_line"],
                    "pen_signal_line":self.has["styles"]["pen_signal_line"],
                    "width_signal_line":self.has["styles"]["width_signal_line"],
                    "style_signal_line":self.has["styles"]["style_signal_line"],
                    "pen_high_historgram":self.has["styles"]["pen_high_historgram"],
                    "pen_low_historgram":self.has["styles"]["pen_low_historgram"],
                    "brush_high_historgram":self.has["styles"]["brush_high_historgram"],
                    "brush_low_historgram":self.has["styles"]["brush_low_historgram"],}
        return styles

    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_macd_line" or _input == "width_macd_line" or _input == "style_macd_line":
            self.macd_line.setPen(color=self.has["styles"]["pen_macd_line"], width=self.has["styles"]["width_macd_line"],style=self.has["styles"]["style_macd_line"])
        elif _input == "pen_signal_line" or _input == "width_signal_line" or _input == "style_signal_line":
            self.signal.setPen(color=self.has["styles"]["pen_signal_line"], width=self.has["styles"]["width_signal_line"],style=self.has["styles"]["style_signal_line"])
        elif _input == "pen_high_historgram" or _input == "pen_low_historgram" or _input == "brush_high_historgram" or _input == "brush_low_historgram":
            
            df:pd.DataFrame = self.has["inputs"]["source"].get_df()
            self._INDICATOR = ta.macd(close=df[f"{self.has["inputs"]["type"]}"],
                                    fast=self.has["inputs"]["fast_period"],
                                    slow=self.has["inputs"]["slow_period"],
                                    signal = self.has["inputs"]["signal_period"],
                                    mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

            column_names = self._INDICATOR.columns.tolist()
            
            macd_name = ''
            histogram_name = ''
            signalma_name = ''
            for name in column_names:
                if name.__contains__("MACD"):
                    macd_name = name
                elif name.__contains__("HISTOGRAM"):
                    histogram_name = name
                elif name.__contains__("SIGNAL"):
                    signalma_name = name

            macd = self._INDICATOR[macd_name].to_numpy()
            histogram = self._INDICATOR[histogram_name].to_numpy()
            signalma = self._INDICATOR[signalma_name].to_numpy()
            xdata = df["index"].to_numpy()
            
            self.histogram.update_styles(_input,(xdata,histogram))
            
    def threadpool_asyncworker(self,candle=None):
        self.worker = None
        if candle == None:
            self.worker = FastWorker(self.first_load_data)
        else:
            self.worker = FastWorker(self.update_data,candle)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.setdata.connect(self.update_histogram,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def update_histogram(self,data):
        xdata,histogram = data[0], data[3]
        self.sig_reset_histogram.emit((xdata,histogram))

    def first_load_data(self,setdata):
        self.disconnect_connection()
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.macd(close=df[f"{self.has["inputs"]["type"]}"],
                                  fast=self.has["inputs"]["fast_period"],
                                  slow=self.has["inputs"]["slow_period"],
                                  signal = self.has["inputs"]["signal_period"],
                                  mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

        column_names = self._INDICATOR.columns.tolist()
        
        macd_name = ''
        histogram_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("MACD"):
                macd_name = name
            elif name.__contains__("HISTOGRAM"):
                histogram_name = name
            elif name.__contains__("SIGNAL"):
                signalma_name = name

        macd = self._INDICATOR[macd_name].to_numpy()
        histogram = self._INDICATOR[histogram_name].to_numpy()
        signalma = self._INDICATOR[signalma_name].to_numpy()
        xdata = df["index"].to_numpy()
        
        self.has["name"] = f"MACD {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        
        setdata.emit((xdata,macd,signalma,histogram))
        #QCoreApplication.processEvents()
        
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        if _value != None:
            if self._precision != None:
                _value = round(_value,self._precision)
            else:
                _value = round(_value,3)
        return _value,"#363a45"
    def get_xaxis_param(self):
        return None,"#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def setdata_worker(self,sig_update_candle):
        self.worker = None
        self.worker = FastWorker(self.update_data,sig_update_candle)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def boundingRect(self) -> QRectF:
        return self.histogram.boundingRect()
    
    def set_Data(self,data):
        
        xData = data[0]
        lb = data[1]
        cb = data[2]
        histogram = data[3]
        
        self.sig_update_histogram.emit((xData[-2:],histogram[-2:]))
        try:
            self.macd_line.setData(xData,lb)
            self.signal.setData(xData,cb)
        except Exception as e:
            pass
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def get_last_point(self):
        _time = self.signal.xData[-1]
        _value = self.signal.yData[-1]
        return _time,_value
    
    def get_min_max(self):
        _min = None
        _max = None
        try:
            if len(self.signal.yData) > 0:
                new_data = self.signal.yData[np.isfinite(self.signal.yData)]
                _min = new_data.min()
                _max = new_data.max()
                if _min == np.nan or _max == np.nan:
                    return None, None
                return _min,_max
        except Exception as e:
            print(e)
        return _min,_max

    def update_data(self,last_candle:List[OHLCV],setdata):
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.macd(close=df[f"{self.has["inputs"]["type"]}"],
                                  fast=self.has["inputs"]["fast_period"],
                                  slow=self.has["inputs"]["slow_period"],
                                  signal = self.has["inputs"]["signal_period"],
                                  mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

        column_names = self._INDICATOR.columns.tolist()
        
        macd_name = ''
        histogram_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("MACD"):
                macd_name = name
            elif name.__contains__("HISTOGRAM"):
                histogram_name = name
            elif name.__contains__("SIGNAL"):
                signalma_name = name
        macd = self._INDICATOR[macd_name].to_numpy()
        histogram = self._INDICATOR[histogram_name].to_numpy()
        signalma = self._INDICATOR[signalma_name].to_numpy()
        xdata = df["index"].to_numpy()
        setdata.emit((xdata,macd,signalma,histogram))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],signalma[-1]))
        self.panel.sig_update_y_axis.emit()

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
    
    def setPen(self, *args, **kargs):
        """
        Sets the pen used to draw lines between points.
        The argument can be a :class:`QtGui.QPen` or any combination of arguments accepted by 
        :func:`pyqtgraph.mkPen() <pyqtgraph.mkPen>`.
        """
        pen = fn.mkPen(*args, **kargs)
        self.opts['pen'] = pen
        self.currentPen = pen
        self.updateItems(styleUpdate=True)

    def data_bounds(self, ax=0, offset=0) -> Tuple:
        x, y = self.getData()
        if ax == 0:
            sub_range = x[-offset:]
        else:
            sub_range = y[-offset:]
        return np.nanmin(sub_range), np.nanmax(sub_range)