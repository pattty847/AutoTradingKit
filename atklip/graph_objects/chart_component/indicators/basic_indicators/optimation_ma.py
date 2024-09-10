from typing import Dict, Tuple, List,TYPE_CHECKING

import numpy as np

from PySide6.QtCore import Signal, QRect, QRectF, QPointF,QThreadPool,Qt,QLineF,QCoreApplication,QObject
from PySide6.QtGui import QPainter, QPicture,QPainterPath
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget
import pandas as pd
from atklip.graph_objects.pyqtgraph import mkPen, GraphicsObject, mkBrush,PlotDataItem,functions as fn

from atklip.indicators import PD_MAType

from atklip.indicators import pandas_ta as ta

from atklip.indicators import OHLCV
from atklip.indicators.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE
from atklip.graph_objects.chart_component.base_items import PlotLineItem
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graph_objects.chart_component.viewchart import Chart
    
class BasicMA(GraphicsObject):
    """DEMA EMA HMA SMA SMMA TEMA TRIX ZLEMA WMA"""
    on_click = Signal(QObject)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    sig_change_indicator_name = Signal(str)

    def __init__(self,chart,indicator_type: PD_MAType,pen:str="yellow",period:int=3,_type:str="close",id = None,clickable=True) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
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
        
        self._pen = pen
        self.id = id
        self.on_click.connect(self.on_click_event)
        self._INDICATOR : pd.Series = pd.Series([])
        self.is_reset = False
        

        self.x_data, self.y_data = np.array([]),np.array([])
        self._bar_picutures: Dict[int, QPicture] = {}
        self.picture: QPicture = QPicture()
        self._rect_area: Tuple[float, float] = None
        self._to_update: bool = False
        self._is_change_source:bool=False
        self._start:int = None
        self._stop:int = None
        
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
        self.disconnect_connection()
        
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.ma(f"{self.has["inputs"]["ma_type"].name}".lower(), df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"])
        self._INDICATOR = self._INDICATOR.astype('float32')
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
            self.has["inputs"]["source"] = self.chart.jp_candle
            self.has["inputs"]["source_name"] = self.chart.jp_candle.source_name
            self.reset_indicator()
            
    
    def reset_threadpool_asyncworker(self):
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
            self.threadpool_asyncworker()
            
    def threadpool_asyncworker(self,candle=None):
        self.disconnect_connection()
        self.worker = None
        self.worker = FastWorker(self.first_load_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
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
        self._is_change_source = True
        self._INDICATOR = None
        
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.ma(f"{self.has["inputs"]["ma_type"].name}".lower(), df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"])
        
        self._INDICATOR = self._INDICATOR.astype('float32')
        
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
        self.worker = FastWorker(self.update_data,sig_update_candle)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    @property
    def xData(self):
        return self.x_data 
    @property
    def yData(self):
        return self.y_data
    
    def paint(self,painter: QPainter,opt: QStyleOptionGraphicsItem,w: QWidget) -> None:
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        if self._start is None or self._start is None:
            x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
            start_index = self.chart.jp_candle.candles[0].index
            stop_index = self.chart.jp_candle.candles[-1].index
            if x_left > start_index:
                self._start = x_left+2
            else:
                self._start = start_index+2
            if x_right < stop_index:
                self._stop = x_right
            else:
                self._stop = stop_index
        rect_area: tuple = (self._start, self._stop)
        if self._to_update:
            self._draw_item_picture(self._start, self._stop)
            self._to_update = False
        elif (rect_area != self._rect_area):
            self._rect_area = rect_area
            self._draw_item_picture(self._start, self._stop)
        elif self.picture == None:
            self._rect_area = rect_area
            self._draw_item_picture(self._start, self._stop)
        self.picture.play(painter)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        self.picture = QPicture()
        painter = QPainter(self.picture)
        [self.play_bar(painter,ix) for ix in range(min_ix, max_ix)]
        painter.end()
    
    def play_bar(self,painter,ix):
        bar_picture = self._bar_picutures.get(ix)
        if bar_picture is not None:
            bar_picture.play(painter)    
            
    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        start_index = self.chart.jp_candle.candles[0].index
        stop_index = self.chart.jp_candle.candles[-1].index
        if x_left > start_index:
            self._start = x_left+2
            x_range_left = x_left - start_index
        elif x_left > stop_index:
            self._start = start_index+2
            x_range_left = 0
        else:
            self._start = start_index+2
            x_range_left = 0
            
        if x_right < stop_index:
            _width = x_right-start_index
            self._stop = x_right+1
        else:
            _width = len(self.chart.jp_candle.candles)
            self._stop = stop_index+1

        if self.y_data.size != 0:
            try:
                h_low,h_high = np.min(self.y_data[x_range_left:_width]), np.max(self.y_data[x_range_left:_width]) 
            except ValueError:
                h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        else:
            h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        rect = QRectF(self._start,h_low,_width,h_high-h_low)
        return rect

    def draw_line(self,index):
        if index != 0:
            pre_t = self.x_data[index-1]
            pre_value = self.y_data[index-1]
            t = self.x_data[index]
            value = self.y_data[index]
            if self._bar_picutures.get(t) == None or index == len(self.y_data)-1:
                candle_picture:QPicture =QPicture()
                p:QPainter =QPainter(candle_picture)
                outline_pen = mkPen(color=self.has["styles"]["pen"],width=self.has["styles"]["width"],style= self.has["styles"]["style"])
                p.setPen(outline_pen)
                _line = QLineF(QPointF(pre_t, pre_value), QPointF(t, value))
                p.drawLine(_line)
                p.end()
                self._bar_picutures[t] = candle_picture

    def set_Data(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        self._to_update = False
        x_data, y_data = data[0],data[1]
        if self._is_change_source:
            self._bar_picutures.clear()
            self._is_change_source = False
        self.x_data, self.y_data = x_data, y_data
        [self.draw_line(index) for index in range(len(y_data)) if y_data[index] is not np.nan]
        # p.end()
        self._to_update = True
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,_value

    def update_data(self,last_candle:List[OHLCV],setdata):
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.ma(f"{self.has["inputs"]["ma_type"].name}".lower(), df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"])
        self._INDICATOR = self._INDICATOR.astype('float32')
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
    
    def data_bounds(self, ax=0, offset=0) -> Tuple:
        x, y = self._line.getData()
        if ax == 0:
            sub_range = x[-offset:]
        else:
            sub_range = y[-offset:]
        return np.nanmin(sub_range), np.nanmax(sub_range)
