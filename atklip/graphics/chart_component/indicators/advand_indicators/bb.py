import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject, QThreadPool,Qt,QRectF,QCoreApplication
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.pyqtgraph import FillBetweenItem,GraphicsObject,PlotDataItem

from atklip.controls import PD_MAType,IndicatorType

from atklip.controls import pandas_ta as ta

from atklip.controls import OHLCV

from atklip.appmanager import FastWorker
from atklip.app_utils import *

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart


class BasicBB(GraphicsObject):
    on_click = Signal(QObject)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self.has = {
            "name": f"BB 20 2",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "ma_type":PD_MAType.SMA,
                    "period":20,
                    "std_dev_mult":2,
                    "indicator_type":IndicatorType.BB,
                    "show":False},

            "styles":{
                    'pen_high_line': "green",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_center_line': "orange",
                    'width_center_line': 1,
                    'style_center_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "red",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    
                    "brush_color": mkBrush('blue',width=0.7),
                    }
                    }
        
        self.lowline = PlotDataItem(pen=self.has["styles"]['pen_low_line'])  # for z value
        self.lowline.setParentItem(self)
        self.centerline = PlotDataItem(pen=self.has["styles"]['pen_center_line'])
        self.centerline.setParentItem(self)
        self.highline = PlotDataItem(pen=self.has["styles"]['pen_high_line'])
        self.highline.setParentItem(self)
        
        self.bb_bank = FillBetweenItem(self.lowline,self.highline,self.has["styles"]['brush_color'])
        self.bb_bank.setParentItem(self)
        
        self.picture: QPicture = QPicture()
        

        self._INDICATOR : pd.DataFrame = pd.DataFrame([])

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
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()


    def regen_indicator(self,setdata):
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.bbands(df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"],std=self.has["inputs"]["std_dev_mult"],\
                                        mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

        column_names = self._INDICATOR.columns.tolist()
        
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("BBL_"):
                lower_name = name
            elif name.__contains__("BBM_"):
                mid_name = name
            elif name.__contains__("BBU_"):
                upper_name = name

        lb = self._INDICATOR[lower_name].to_numpy()
        cb = self._INDICATOR[mid_name].to_numpy()
        ub = self._INDICATOR[upper_name].to_numpy()
        xdata = df["index"].to_numpy()
        
        # self.set_Data((xdata,lb,cb,ub))
        setdata.emit((xdata,lb,cb,ub))
        
        "update o day"
        
        self.has["name"] = f"BB {self.has["inputs"]["period"]} {self.has["inputs"]["std_dev_mult"]} {self.has["inputs"]["type"]} {self.has["inputs"]["ma_type"].name}"
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
                self.reset_indicator()
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True
        
        if update:
            self.has["name"] = f"BB {self.has["inputs"]["period"]} {self.has["inputs"]["std_dev_mult"]} {self.has["inputs"]["type"]} {self.has["inputs"]["ma_type"].name}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.threadpool_asyncworker()
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "period":self.has["inputs"]["period"],
                    "std_dev_mult":self.has["inputs"]["std_dev_mult"],
                    "ma_type":self.has["inputs"]["ma_type"],}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_high_line":self.has["styles"]["pen_high_line"],
                    "width_high_line":self.has["styles"]["width_high_line"],
                    "style_high_line":self.has["styles"]["style_high_line"],
                    
                    "pen_center_line":self.has["styles"]["pen_center_line"],
                    "width_center_line":self.has["styles"]["width_center_line"],
                    "style_center_line":self.has["styles"]["style_center_line"],
                    
                    "pen_low_line":self.has["styles"]["pen_low_line"],
                    "width_low_line":self.has["styles"]["width_low_line"],
                    "style_low_line":self.has["styles"]["style_low_line"],
                    
                    "brush_color":self.has["styles"]["brush_color"],
                    }
        return styles
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_high_line" or _input == "width_high_line" or _input == "style_high_line":
            self.highline.setPen(color=self.has["styles"]["pen_high_line"], width=self.has["styles"]["width_high_line"],style=self.has["styles"]["style_high_line"])
        elif _input == "pen_center_line" or _input == "width_center_line" or _input == "style_center_line":
            self.centerline.setPen(color=self.has["styles"]["pen_center_line"], width=self.has["styles"]["width_center_line"],style=self.has["styles"]["style_center_line"])
        elif _input == "pen_low_line" or _input == "width_low_line" or _input == "style_low_line":
            self.lowline.setPen(color=self.has["styles"]["pen_low_line"], width=self.has["styles"]["width_low_line"],style=self.has["styles"]["style_low_line"])
        elif _input == "brush_color":
            self.bb_bank.setBrush(self.has["styles"]["brush_color"])
        
    def threadpool_asyncworker(self,candle=None):
        self.worker = None
        self.worker = FastWorker(self.first_load_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    def first_load_data(self,setdata):
        self.disconnect_connection()
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.bbands(df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"],std=self.has["inputs"]["std_dev_mult"],\
                                        mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

        column_names = self._INDICATOR.columns.tolist()
        
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("BBL_"):
                lower_name = name
            elif name.__contains__("BBM_"):
                mid_name = name
            elif name.__contains__("BBU_"):
                upper_name = name

        lb = self._INDICATOR[lower_name].to_numpy()
        cb = self._INDICATOR[mid_name].to_numpy()
        ub = self._INDICATOR[upper_name].to_numpy()
        
        xdata = df["index"].to_numpy()
        
        setdata.emit((xdata,lb,cb,ub))
        
        self.has["name"] = f"BB {self.has["inputs"]["period"]} {self.has["inputs"]["std_dev_mult"]} {self.has["inputs"]["type"]} {self.has["inputs"]["ma_type"].name}"
        self.sig_change_indicator_name.emit(self.has["name"])
        self.has["inputs"]["source"].sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.has["inputs"]["source"].sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
    

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        start_index = self.chart.jp_candle.candles[0].index
        stop_index = self.chart.jp_candle.candles[-1].index
        if x_left > start_index:
            _start = x_left+2
            x_range_left = x_left - start_index
        else:
            _start = start_index+2
            x_range_left = 0
        if x_right < stop_index:
            _width = x_right-start_index
        else:
            _width = len(self.chart.jp_candle.candles)
        if self.lowline.yData is not None:
            if self.lowline.yData.size != 0:
                try:
                    h_low,h_high = self.lowline.yData[x_range_left:_width].min(), self.highline.yData[x_range_left:_width].max()
                except ValueError:
                    h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]  
            else:
                h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        else:
            h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        rect = QRectF(_start,h_low,_width,h_high-h_low)
        return rect
        return self.bb_bank.boundingRect()
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def setdata_worker(self,sig_update_candle):
        self.worker = None
        self.worker = FastWorker(self.update_data,sig_update_candle)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def set_Data(self,data):
        
        xData = data[0]
        lb = data[1]
        cb = data[2]
        ub = data[3]
        
        self.lowline.setData(xData,lb)
        self.centerline.setData(xData,cb)
        self.highline.setData(xData,ub)
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self.has["styles"]['pen_center_line']
    
    def get_xaxis_param(self):
        return None,"#363a45"
    
    def get_last_point(self):
        _time = self.centerline.xData[-1]
        _value = self.centerline.yData[-1]
        return _time,_value
    
    def get_min_max(self):
        y_data = self.signal.yData
        _min = None
        _max = None
        try:
            if y_data.__len__() > 0:
                _min = y_data.min()
                _max = y_data.max()
        except Exception as e:
            time.sleep(0.2)
            self.get_min_max()
        return _min,_max

    def update_data(self,last_candle:List[OHLCV],setdata):
        
        df:pd.DataFrame = self.has["inputs"]["source"].get_df()
        self._INDICATOR = ta.bbands(df[f"{self.has["inputs"]["type"]}"],length=self.has["inputs"]["period"],std=self.has["inputs"]["std_dev_mult"],\
                                        mamode=f"{self.has["inputs"]["ma_type"].name}".lower())

        column_names = self._INDICATOR.columns.tolist()
        
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("BBL_"):
                lower_name = name
            elif name.__contains__("BBM_"):
                mid_name = name
            elif name.__contains__("BBU_"):
                upper_name = name
        lb = self._INDICATOR[lower_name].to_numpy()
        cb = self._INDICATOR[mid_name].to_numpy()
        ub = self._INDICATOR[upper_name].to_numpy()
        xdata = df["index"].to_numpy()
        setdata.emit((xdata,lb,cb,ub))
        #QCoreApplication.processEvents()
        
    def on_click_event(self):
        print("zooo day__________________")
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    
