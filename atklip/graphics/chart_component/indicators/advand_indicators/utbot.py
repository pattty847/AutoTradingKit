import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.controls import PD_MAType,IndicatorType,UTBOT_ALERT
from atklip.controls.models import UTBotModel
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem

from atklip.appmanager import FastWorker
from atklip.app_utils import *

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class UTBot(PlotDataItem):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        super().__init__()
        # GraphicsObject.__init__(self)
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has = {
            "name": f"UTBOT 1 3 20",
            "y_axis_show":False,
            
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "key_value":1,
                    "atr_period":3,
                    "ema_period":20,
                    "indicator_type":IndicatorType.UTBOT,
                    "show":False},

            "styles":{
                    'pen_high_line': "green",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "red",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)
        
        # self.bb_bank = FillBetweenItem(self.lowline,self.highline,self.has["styles"]['brush_color'])
        # self.bb_bank.setParentItem(self)
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()
        self.INDICATOR  = UTBOT_ALERT(self.has["inputs"]["source"], self.model.__dict__)
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id
        
    @property
    def model(self) -> dict:
        return UTBotModel(self.id,"UTBot",self.chart.jp_candle.source_name,self.has["inputs"]["key_value"],
                              self.has["inputs"]["atr_period"],self.has["inputs"]["ema_period"])
    
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.add_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR.signal_delete.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
    
    def fisrt_gen_data(self):
        self.connect_signals()
        self.INDICATOR.started_worker()
       
    def delete(self):
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data()
        setdata.emit((xdata,_long,_short))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"UTBOT {self.has["inputs"]["key_value"]} {self.has["inputs"]["atr_period"]}- {self.has["inputs"]["ema_period"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "key_value":self.has["inputs"]["key_value"],
                    "atr_period":self.has["inputs"]["atr_period"],
                    "ema_period":self.has["inputs"]["ema_period"],
                    }
        return inputs
    
    def get_styles(self):
        styles =  {"pen_high_line":self.has["styles"]["pen_high_line"],
                    "width_high_line":self.has["styles"]["width_high_line"],
                    "style_high_line":self.has["styles"]["style_high_line"],
                    
                    "pen_low_line":self.has["styles"]["pen_low_line"],
                    "width_low_line":self.has["styles"]["width_low_line"],
                    "style_low_line":self.has["styles"]["style_low_line"],
                    }
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        
        if is_update:
            self.has["name"] = f"UTBOT {self.has["inputs"]["key_value"]} {self.has["inputs"]["atr_period"]}- {self.has["inputs"]["ema_period"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
    
    def get_xaxis_param(self):
        return None,"#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def set_Data(self,data):
        "df.loc[(df['max_speed'] > 1) & (df['shield'] < 8)]"
        if self.list_pos:
            for obj in self.list_pos.values():
                self.chart.remove_item(obj)
        self.list_pos.clear()
        # print(data)
        
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        data = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        df = data.loc[(data['long'] == True) | (data['short'] == True)]
        # df = data.loc[(data['long'] == True)]        
        for i in range(len(df)):
            if df.iloc[i]['long'] == True:
                _x = df.iloc[i]['x']
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.chart.add_item(obj)
                self.list_pos[_x] = obj
            elif df.iloc[i]['short'] == True:
                _x = df.iloc[i]['x']
                _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                obj =  BaseArrowItem(drawtool=self,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.chart.add_item(obj)
                self.list_pos[_x] = obj

    
    def add_historic_Data(self,data):
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        data = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        df = data.loc[(data['long'] == True) | (data['short'] == True)]
        # df = data.loc[(data['long'] == True)]

        for i in range(len(df)):
            if df.iloc[i]['long'] == True:
                _x = df.iloc[i]['x']
                if self.list_pos.get(_x):
                    continue
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.chart.add_item(obj)
                self.list_pos[_x] = obj
            elif df.iloc[i]['short'] == True:
                _x = df.iloc[i]['x']
                if self.list_pos.get(_x):
                    continue
                _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                obj =  BaseArrowItem(drawtool=self,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.chart.add_item(obj)
                self.list_pos[_x] = obj
        
    def update_Data(self,data):
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        data = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        df = data.loc[(data['long'] == True) | (data['short'] == True)]
        # df = data.loc[(data['long'] == True)]
        for i in range(len(df)):
            if df.iloc[i]['long'] == True:
                _x = df.iloc[i]['x']
                if self.list_pos.get(_x):
                    continue
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.chart.add_item(obj)
                self.list_pos[_x] = obj
            elif df.iloc[i]['short'] == True:
                _x = df.iloc[i]['x']
                if self.list_pos.get(_x):
                    continue
                _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                obj =  BaseArrowItem(drawtool=self,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.chart.add_item(obj)
                self.list_pos[_x] = obj
        
    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()  
    
    def add_historic_worker(self,_len):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data,_len)
        self.worker.signals.setdata.connect(self.add_historic_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start() 
    
    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
    
    def load_historic_data(self,_len,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(stop=_len)
        setdata.emit((xdata,_long,_short))
        
    def add_data(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(start=-1)
        setdata.emit((xdata,_long,_short))
    
    def update_data(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(start=-1)
        setdata.emit((xdata,_long,_short))

    # def boundingRect(self) -> QRectF:
    #     x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
    #     start_index = self.chart.jp_candle.candles[0].index
    #     stop_index = self.chart.jp_candle.candles[-1].index
    #     if x_left > start_index:
    #         _start = x_left+2
    #         x_range_left = x_left - start_index
    #     else:
    #         _start = start_index+2
    #         x_range_left = 0
    #     if x_right < stop_index:
    #         _width = x_right-_start
    #     else:
    #         _width = stop_index-_start

    #     return QRectF(0,0,0,0)
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self.has["styles"]['pen_high_line']
    
    
    def get_last_point(self):
        # _time = self.centerline.xData[-1]
        _time = self.xData[-1]
        # _value = self.centerline.yData[-1]
        _value = self.yData[-1]
        return _time,_value
    
    def get_min_max(self):
        return None,None
        try:
            _min, _max = np.nanmin(self.lowline.yData), np.nanmax(self.highline.yData)
            # if y_data.__len__() > 0:
            #     _min = y_data.min()
            #     _max = y_data.max()
            return _min,_max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min,_max

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
    