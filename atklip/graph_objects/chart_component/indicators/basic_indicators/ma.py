from typing import Tuple, List,TYPE_CHECKING

import numpy as np
import pandas as pd

from atklip.graph_objects.pyqtgraph import PlotDataItem,GraphicsObject
from atklip.graph_objects.pyqtgraph import functions as fn


from PySide6.QtCore import Signal, QObject, QThreadPool,Qt,QRectF,QCoreApplication
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsItem

from atklip.indicators import PD_MAType
from atklip.indicators import pandas_ta as ta
from atklip.indicators import OHLCV

from atklip.indicators.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE
from atklip.graph_objects.chart_component.base_items import PlotLineItem
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graph_objects.chart_component.viewchart import Chart
    
class BasicMA(PlotLineItem):
    """DEMA EMA HMA SMA SMMA TEMA TRIX ZLEMA WMA"""
    on_click = Signal(QObject)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    sig_change_indicator_name = Signal(str)

    def __init__(self,chart,indicator_type: PD_MAType,pen:str="yellow",period:int=3,_type:str="close",id = None,clickable=True) -> None:
        """Choose colors of candle"""
        PlotLineItem.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        
        self.has = {
            "name": f"{indicator_type.value} {period} {_type}",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name":self.chart.jp_candle.source_name,
                    "type":_type,
                    "ma_type":indicator_type,
                    "period":period,
                    "show":True
                    },

            "styles":{
                    'pen': pen,
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,}
        }
        
        self.opts.update({'pen':pen})
        self._pen = pen
        self.id = id
        self.on_click.connect(self.on_click_event)
        self._INDICATOR : pd.Series = pd.Series([])
        self.is_reset = False
        
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(1)
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)
        
        self.chart.sig_remove_source.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
        
        self.signal_delete.connect(self.delete)
        
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        
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
        self._INDICATOR =None
        
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.ma(f"{self.has["inputs"]["ma_type"].name}".lower(), df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"])
        self._INDICATOR = self._INDICATOR.astype('float64')
        _data = self._INDICATOR.to_numpy()
        _index = df["index"].to_numpy()

        self.set_Data((_index,_data))
        
        self.sig_change_yaxis_range.emit()
        
        self.has["name"] = f"{self.has["inputs"]["ma_type"].name} {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])

        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
    
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
      
    def get_source(self,_type,ma_type:PD_MAType=PD_MAType.EMA, period:int=3):
        if _type.value == "japan":
            return self.chart.jp_candle, None,None

    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "ma_type":self.has["inputs"]["ma_type"],
                    "period":self.has["inputs"]["period"],}
        return inputs
    
    def get_styles(self):
        styles =  {"pen":self.has["styles"]["pen"],
                    "width":self.has["styles"]["width"],
                    "style":self.has["styles"]["style"],}
        return styles
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.disconnect_connection()
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.reset_indicator()
        elif _input == "type":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        elif _input == "ma_type":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        elif _input == "period":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True

        if is_update:
            self.has["name"] = f"{self.has["inputs"]["ma_type"].name} {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.threadpool_asyncworker()
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])

    def threadpool_asyncworker(self,candle=None):
        self.worker = None
        self.worker = FastWorker(self.threadpool,self.first_load_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self._pen
    def get_xaxis_param(self):
        return None,"#363a45"

    def first_load_data(self,setdata):
        self.disconnect_connection()
        self._is_change_source = True
        self._INDICATOR = None
        
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.ma(f"{self.has["inputs"]["ma_type"].name}".lower(), df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"])
        
        self._INDICATOR = self._INDICATOR.astype('float64')
        
        _data = self._INDICATOR.to_numpy()
        _index = df["index"].to_numpy()

        setdata.emit((_index,_data))
        self.sig_change_yaxis_range.emit()
        
        self.has["name"] = f"{self.has["inputs"]["ma_type"].name} {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])

        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
    def remove_none_value(self,output_times,output_values,i):
        if self._INDICATOR != None:
            if self._INDICATOR.output_values != None:
                if self._INDICATOR.output_values[i] != None:
                    output_times.append(self._INDICATOR.output_times[i])
                    output_values.append(self._INDICATOR.output_values[i])

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
    
    def setdata_worker(self,sig_update_candle):
        self.worker = None
        self.worker = FastWorker(self.threadpool,self.update_data,sig_update_candle)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def set_Data(self,data):
        xData = data[0]
        yData = data[1]
        self.setData(xData, yData)
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()

    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,_value
    def update_data(self,last_candle:List[OHLCV],setdata):
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.ma(f"{self.has["inputs"]["ma_type"].name}".lower(), df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"])
        self._INDICATOR = self._INDICATOR.astype('float64')
        _data = self._INDICATOR.to_numpy()
        _index = df["index"].to_numpy()
        setdata.emit((_index,_data))
        #QCoreApplication.processEvents()
    
        
    def on_click_event(self,_object):
        print("zooo day__________________",_object)
 
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
        self._line.updateItems(styleUpdate=True)

    def data_bounds(self, ax=0, offset=0) -> Tuple:
        x, y = self._line.getData()
        if ax == 0:
            sub_range = x[-offset:]
        else:
            sub_range = y[-offset:]
        return np.nanmin(sub_range), np.nanmax(sub_range)
