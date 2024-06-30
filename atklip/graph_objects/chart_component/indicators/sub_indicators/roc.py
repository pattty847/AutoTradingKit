from typing import Tuple, List, TYPE_CHECKING
import numpy as np
import pandas as pd
from atklip.graph_objects.pyqtgraph import PlotDataItem
from atklip.graph_objects.pyqtgraph import functions as fn
from atklip.graph_objects.chart_component.base_items import PriceLine,PlotLineItem

from PySide6.QtCore import Signal, QObject, QThreadPool,Qt,QRectF,QCoreApplication
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsItem

from atklip.indicators import PD_MAType,IndicatorType
from atklip.indicators import pandas_ta as ta
from atklip.indicators import OHLCV

from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graph_objects.chart_component.viewchart import Chart
    from atklip.graph_objects.chart_component.sub_panel_indicator import ViewSubPanel
class BasicROC(PlotDataItem):
    """ROC"""
    on_click = Signal(QObject)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker, chart,panel,id = None,clickable=True) -> None:
        """Choose colors of candle"""
        super().__init__(clickable=clickable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has = {
            "name" :f"ROC 3",
            "y_axis_show":True,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "indicator_type":IndicatorType.ROC,
                    "period":3,
                    "price_high":0.5,
                    "price_low":-0.5,
                    "show":True},

            "styles":{
                    'pen': "yellow",
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,}
                }
        
        self.opts.update({'pen':"yellow"})

        self.id = id

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)

        self._INDICATOR : pd.DataFrame|pd.Series = pd.Series([])
        self.is_reset = False
        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        self.destroyed.connect(self.price_line.deleteLater)
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.price_high = PriceLine(color="green",width=2,movable=True)  # for z value
        self.price_high.setParentItem(self)
        self.price_high.setPos(self.has["inputs"]["price_high"])
        
        self.price_low = PriceLine(color="red",width=2,movable=True)  # for z value
        self.price_low.setParentItem(self)
        self.price_low.setPos(self.has["inputs"]["price_low"])
        
        self.threadpool = QThreadPool(self)
        #self.threadpool.setMaxThreadCount(8)
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)
        self.chart.sig_remove_source.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
        
        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.QueuedConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.QueuedConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.QueuedConnection)


    def delete(self):
        self.chart.sig_remove_item.emit(self)
    
    def disconnect_connection(self):
        try:
            self.has["inputs"]["source"].sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.has["inputs"]["source"].sig_update_candle.disconnect(self.setdata_worker)
            self.has["inputs"]["source"].sig_add_candle.disconnect(self.setdata_worker)
        except RuntimeError:
                    pass
    
    def reset_indicator(self):
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.roc(close=df[f"{self.has["inputs"]["type"]}"],
                                  length=self.has["inputs"]["period"])
        
        if isinstance(self._INDICATOR,pd.Series):
            y_data = self._INDICATOR.to_numpy()
        else:
            column_names = self._INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("ROC"):
                    roc_name = name
            y_data = self._INDICATOR[roc_name].to_numpy()  
        xdata = df["index"].to_numpy()
        
        self.set_Data((xdata,y_data))
        
        self.sig_change_yaxis_range.emit()

        self.has["name"] = f"ROC {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.QueuedConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.QueuedConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.QueuedConnection)

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
            
            self.has["name"] = f"ROC {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.threadpool_asyncworker()
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "period":self.has["inputs"]["period"],
                    "price_high":self.has["inputs"]["price_high"],
                    "price_low":self.has["inputs"]["price_low"]}
        return inputs
    
    def get_styles(self):
        styles =  {"pen":self.has["styles"]["pen"],
                    "width":self.has["styles"]["width"],
                    "style":self.has["styles"]["style"],}
        return styles
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])

    def threadpool_asyncworker(self,candle=None):
        self.worker = FastWorker(self,self.first_load_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.SingleShotConnection)
        self.threadpool.start(self.worker)
    def first_load_data(self,setdata):
        self.disconnect_connection()
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.roc(close=df[f"{self.has["inputs"]["type"]}"],
                                  length=self.has["inputs"]["period"])
        if isinstance(self._INDICATOR,pd.Series):
            y_data = self._INDICATOR.to_numpy()
        else:
            column_names = self._INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("ROC"):
                    roc_name = name
            y_data = self._INDICATOR[roc_name].to_numpy()
        xdata = df["index"].to_numpy()
        
        setdata.emit((xdata,y_data))

        self.has["name"] = f"ROC {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.QueuedConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.QueuedConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.QueuedConnection)


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

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
        return _value, "#363a45"
    def get_xaxis_param(self):
        return None,"#363a45"
    def change_type(self, type_):
        if type_ == "SolidLine":
            self.currentPen.setStyle(Qt.PenStyle.SolidLine)
        elif type_ == "DashLine":
            self.currentPen.setStyle(Qt.PenStyle.DashLine)
        elif type_ == "DotLine":
            self.currentPen.setStyle(Qt.PenStyle.DotLine)
        self.setPen(self.currentPen)

    def change_width(self, width):
        self.currentPen.setWidth(width)
        self.setPen(self.currentPen)

    def change_color(self, color):
        r, g, b = color[0], color[1], color[2]
        color = QColor(r, g, b)
        self.currentPen.setColor(color)
        self.setPen(self.currentPen)

    def setdata_worker(self,sig_update_candle):
        self.worker = FastWorker(self,self.update_data,sig_update_candle)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.SingleShotConnection)
        self.threadpool.start(self.worker)
    
    def set_Data(self,data):
        xData = data[0]
        yData = data[1]
        try:
            self.setData(xData, yData)
        except Exception as e:
            pass
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,round(_value,3)

    def get_min_max(self):
        _min = None
        _max = None
        try:
            if len(self.yData) > 0:
                new_data = self.yData[np.isfinite(self.yData)]
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
        self._INDICATOR = ta.roc(close=df[f"{self.has["inputs"]["type"]}"],
                                  length=self.has["inputs"]["period"])
        if isinstance(self._INDICATOR,pd.Series):
            y_data = self._INDICATOR.to_numpy()
        else:
            column_names = self._INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("ROC"):
                    roc_name = name
            y_data = self._INDICATOR[roc_name].to_numpy()  
        xdata = df["index"].to_numpy()
        setdata.emit((xdata,y_data))
        self.last_pos.emit((IndicatorType.ROC,y_data[-1]))
        self._panel.sig_update_y_axis.emit()
        
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mouseClickEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
   
    def getIndicatorType(self):
        return self.has["inputs"]["type"]

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
