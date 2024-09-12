import time
from typing import Tuple, List,TYPE_CHECKING

import numpy as np
import pandas as pd

from atklip.graphics.pyqtgraph import PlotDataItem,GraphicsObject
from atklip.graphics.pyqtgraph import functions as fn


from PySide6.QtCore import Signal, QObject, QThreadPool,Qt,QRectF,QCoreApplication
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType
from atklip.controls import pandas_ta as ta
from atklip.controls import OHLCV

from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE
from atklip.controls.ma import MA
from atklip.graphics.chart_component.base_items import PlotLineItem
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    
class BasicMA(PlotLineItem):
    """DEMA EMA HMA SMA SMMA TEMA TRIX ZLEMA WMA"""
    on_click = Signal(QObject)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    sig_change_indicator_name = Signal(str)

    def __init__(self,chart,indicator_type: PD_MAType,pen:str="yellow",period:int=3,_type:str="close",id = None,clickable=True) -> None:
        """Choose colors of candle"""
        PlotLineItem.__init__(self)
        self.chart:Chart = chart
        
        self.has = {
            "name": f"{indicator_type.value} {_type} {period}",
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
        self.is_reset = False
        self.xData, self.yData = np.array([]),np.array([])
        
        self.INDICATOR  = MA(self,self.has["inputs"]["source"], self.has["inputs"]["type"],
                              self.has["inputs"]["ma_type"],self.has["inputs"]["period"])
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)
        self.chart.sig_remove_source.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
        
        self.signal_delete.connect(self.delete)
        
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.setdata_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
    
    def threadpool_asyncworker(self):
        self.connect_signals()
        self.INDICATOR.fisrt_gen_data()
       
    def delete(self):
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        df:pd.DataFrame = self.INDICATOR.get_df()
        _data = df["data"].to_numpy()
        _index = df["index"].to_numpy()
        setdata.emit((_index,_data))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"{self.has["inputs"]["ma_type"].name} {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])

    def replace_source(self,source_name):
        if self.has["inputs"]["source_name"] == source_name:
            self.has["inputs"]["source"] = self.chart.jp_candle
            self.has["inputs"]["source_name"] = self.chart.jp_candle.source_name
            self.INDICATOR.change_source(self.has["inputs"]["source"])
            
    def reset_threadpool_asyncworker(self):
        source_name = self.has["inputs"]["source_name"].split(" ")[0]
        self.has["inputs"]["source"].source_name = f"{source_name} {self.chart.symbol} {self.chart.interval}"
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
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_inputs(_input,self.has["inputs"]["source"])
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
            self.INDICATOR.change_inputs(_input,_source)
            
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])


    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self._pen
    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
    
    def set_Data(self,data):
        self.xData = data[0]
        self.yData = data[1]
        self.setData(self.xData, self.yData)

    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,_value
    
    def update_data(self,setdata):
        df:pd.DataFrame = self.INDICATOR.get_df()
        _data = df["data"].to_numpy()
        _index = df["index"].to_numpy()
        setdata.emit((_index,_data))        

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mouseClickEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    
    def setPen(self, *args, **kargs):
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