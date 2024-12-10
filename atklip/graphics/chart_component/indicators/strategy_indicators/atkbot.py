import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.graphics.pyqtgraph import GraphicsObject

from atklip.controls import PD_MAType,IndicatorType,UTBOT_ALERT
from atklip.controls.models import ATKBOTModel, MACDModel, RSIModel,SQeezeModel,SuperTrendModel
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem
from atklip.graphics.chart_component.draw_tools.TargetItem import ArrowItem
from atklip.graphics.chart_component.draw_tools.entry import Entry

from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.candle import N_SMOOTH_CANDLE, SMOOTH_CANDLE
from atklip.controls.ma import ma
from atklip.controls.trend.zigzag import ZIGZAG
from atklip.controls.momentum.macd import MACD
from atklip.controls.momentum.rsi import RSI
from atklip.controls import  SQEEZE
from atklip.controls import SuperTrend
from atklip.controls import AllCandlePattern
from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.TextItem import TextItem
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class ATKBOT(GraphicsObject):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        # super().__init__()
        GraphicsObject.__init__(self)
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has = {
            "name": f"ATKPRO Ver_1.0",
            "y_axis_show":False,
            
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    
                    "key_value_long":0.1,
                    "key_value_short":0.1,
                    
                    "atr_long_period":1,
                    "ema_long_period":2,
                    
                    "atr_short_period":1,
                    "ema_short_period":2,
                    
                    "n_smooth_period":3,
                    "ma_smooth_period":3,
                    "mamode":PD_MAType.EMA,
                    
                    "supertrend_length":3,
                    "supertrend_atr_length":3,
                    "supertrend_multiplier":0.3,
                    "supertrend_atr_mamode":PD_MAType.RMA,

                    "n_period": 10,
                    "m_period": 10,
                    
                    "stoploss_price":0.25,
                    
                    "indicator_type":IndicatorType.ATKPRO,
                    
                    "bb_length":20,
                    "bb_std":2,
                    "kc_length":10,
                    "kc_scalar":1.5,
                    "mom_length":10,
                    "mom_smooth":10,
                    "use_tr":True,
                    "lazybear":True,
                    "detailed":False,
                    "sqeeze_mamode":PD_MAType.SMA,
                    
                    "show":False},

            "styles":{
                    'pen_high_line': "#089981",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "#f23645",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)
        
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()
        self.cr_position:dict = {"type":None,"index":None,"side_count":0}

        
        self.stoploss_smooth_heikin = N_SMOOTH_CANDLE(self.chart._precision,self.chart.heikinashi,
                                                  self.has["inputs"]["n_smooth_period"],
                                                  self.has["inputs"]["mamode"].value,
                                                  self.has["inputs"]["ma_smooth_period"])
        self.stoploss_smooth_heikin.fisrt_gen_data()
        
        
        # self.stoploss_smooth_heikin = SMOOTH_CANDLE(self.chart._precision,self.chart.heikinashi,
        #                                           self.has["inputs"]["mamode"].value,
        #                                           self.has["inputs"]["ma_smooth_period"])
        # self.stoploss_smooth_heikin.fisrt_gen_data()
        
        
        # self.super_smoothcandle = N_SMOOTH_CANDLE(self.chart._precision,self.chart.jp_candle,
        #                                           2,
        #                                           self.has["inputs"]["mamode"].value,
        #                                           3)
        # self.super_smoothcandle.fisrt_gen_data()
        # self.sqeeze = SQEEZE(self.stoploss_smooth_heikin, self.sqeeze_model.__dict__)
        # self.sqeeze.fisrt_gen_data()
        
        # self.super_trend = SuperTrend(self.stoploss_smooth_heikin, self.supertrend_model.__dict__)
        # self.super_trend.fisrt_gen_data()
        
        # self.INDICATOR  = UTBOT_ALERT(self.has["inputs"]["source"], self.model.__dict__)
        self.INDICATOR  = AllCandlePattern(self.has["inputs"]["source"])
                
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update and self.stoploss_smooth_heikin.is_current_update
        return is_updated
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id

    @property
    def sqeeze_model(self)-> dict:
        return SQeezeModel(self.id,"SQEEZE",self.chart.jp_candle.source_name,
                        self.has["inputs"]["bb_length"],
                        self.has["inputs"]["bb_std"],
                        self.has["inputs"]["kc_length"],
                        self.has["inputs"]["kc_scalar"],
                        self.has["inputs"]["mom_length"],
                        self.has["inputs"]["mom_smooth"],
                        self.has["inputs"]["sqeeze_mamode"].name.lower(),
                        self.has["inputs"]["use_tr"],
                        self.has["inputs"]["lazybear"],
                        self.has["inputs"]["detailed"]
                        )
    
    @property
    def supertrend_model(self)-> dict:
        return SuperTrendModel(self.id,"SQEEZE",self.chart.jp_candle.source_name,
                        self.has["inputs"]["supertrend_length"],
                        self.has["inputs"]["supertrend_atr_length"],
                        self.has["inputs"]["supertrend_multiplier"],
                        self.has["inputs"]["supertrend_atr_mamode"].name.lower()
                        )
    
    @property
    def macd_model(self) -> dict:
        return MACDModel(self.id,"MACD",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["type"],
                        self.has["inputs"]["slow_period"],
                        self.has["inputs"]["fast_period"],
                        self.has["inputs"]["signal_period"],
                        self.has["inputs"]["macd_type"].name.lower())
    
    @property
    def rsi_model(self) -> dict:
        return RSIModel(self.id,"RSI",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["type"],
                        self.has["inputs"]["rsi_period"],
                        self.has["inputs"]["rsi_ma_type"].name.lower())
    
    @property
    def model(self) -> dict:
        return ATKBOTModel(self.id,"ATKPRO",self.has["inputs"]["source"].source_name,self.has["inputs"]["key_value_long"],self.has["inputs"]["key_value_short"],
                              self.has["inputs"]["atr_long_period"],self.has["inputs"]["ema_long_period"],
                              self.has["inputs"]["atr_short_period"],self.has["inputs"]["ema_short_period"])
    
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
    
    def check_pivot_points(self,df:pd.DataFrame,_type:str="high",n = 10, m=20):
        _len = len(df)
        # print(df)   
        if _type == "high":
            for i in range(n):  
                if _len - i - m > 0:  
                    array = df.iloc[_len-i - m:_len-i][_type].to_numpy()
                    index = df.iloc[_len-i - m:_len-i]["index"].to_numpy()
                    max_previous_m = array.max()  
                    
                    if array[-1] >= max_previous_m: 
                        # print(True, array[-1], index[-1])
                        return (True, array[-1], index[-1])
            
        elif _type == "low":
            for i in range(n):  
                if _len - i - m > 0:  
                    array = df.iloc[_len-i - m:_len-i][_type].to_numpy()
                    index = df.iloc[_len-i - m:_len-i]["index"].to_numpy()
                    min_previous_m = array.min()   
                         
                    if array[-1] <= min_previous_m: 
                        # print(True, array[-1], index[-1]) 
                        return (True, array[-1], index[-1])
        return (False, None, None)

    def check_active_pos(self,_type:str,_open: float=0):
        if self.list_pos:
            for x in self.list_pos.keys():
                entry_infor:dict = self.list_pos[x]
                is_entry_closed =  entry_infor["is_stoploss"]
                is_take_profit_2R =  entry_infor["take_profit_2R"]
                is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
                
                entry_type = entry_infor["type"]
                entry:Entry = entry_infor["entry"]
                
                if entry_type == _type:
                    if not is_entry_closed and not is_take_profit_2R:
                        # self.list_pos[x]["is_stoploss"] = _open
                        # entry.locked_handle()
                        return True
        return False
    
    
    def check_active_other_side_pos(self,_type:str,_open: float):
        if self.list_pos:
            for x in self.list_pos.keys():
                entry_infor:dict = self.list_pos[x]
                is_entry_closed =  entry_infor["is_stoploss"]
                is_take_profit_2R =  entry_infor["take_profit_2R"]
                is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
                
                entry_type = entry_infor["type"]
                entry:Entry = entry_infor["entry"]
                
                if entry_type == _type:
                    if not is_entry_closed and not is_take_profit_2R:
                        self.list_pos[x]["is_stoploss"] = _open
                        entry.locked_handle()
        #                 return True
        # return False
    
                        
    def delete(self):
        print("vao day")
        self.INDICATOR.deleteLater()
        # self.macd.deleteLater()
        # self.sqeeze.deleteLater()
        # self.super_smoothcandle.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        df= self.INDICATOR.get_data()
        setdata.emit(df)
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"ATKPRO Ver_1.0"
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
                    "key_value_long":self.has["inputs"]["key_value_long"],
                    "key_value_short":self.has["inputs"]["key_value_short"],
                    "atr_long_period":self.has["inputs"]["atr_long_period"],
                    "ema_long_period":self.has["inputs"]["ema_long_period"],
                    "atr_short_period":self.has["inputs"]["atr_short_period"],
                    "ema_short_period":self.has["inputs"]["ema_short_period"],
                    
                    
                    "supertrend_length":self.has["inputs"]["supertrend_length"],
                    "supertrend_atr_length":self.has["inputs"]["supertrend_atr_length"],
                    "supertrend_multiplier":self.has["inputs"]["supertrend_multiplier"],
                    "supertrend_atr_mamode":self.has["inputs"]["supertrend_atr_mamode"],
                    
                    
                    
                    "n_smooth_period":self.has["inputs"]["n_smooth_period"],
                    "ma_smooth_period":self.has["inputs"]["ma_smooth_period"],
                    "mamode":self.has["inputs"]["mamode"],

                    "stoploss_price": self.has["inputs"]["stoploss_price"],

                    
                    "n_period":self.has["inputs"]["n_period"],
                    "m_period":self.has["inputs"]["m_period"],
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
                # if  _input != "price_high" and _input != "price_low":
                is_update = True
        
        if is_update:
            self.has["name"] = f"ATKPRO Ver_1.0"
            self.sig_change_indicator_name.emit(self.has["name"])
            
            if _input == "n_smooth_period" or _input == "ma_smooth_period" or _input == "mamode":
                self.stoploss_smooth_heikin.refresh_data(self.has["inputs"]["mamode"].value,self.has["inputs"]["ma_smooth_period"],self.has["inputs"]["n_smooth_period"])
                self.stoploss_smooth_heikin.fisrt_gen_data()
                # self.super_trend.fisrt_gen_data()
                # self.sqeeze.fisrt_gen_data()

            
            # if  _input == "supertrend_length" or _input == "supertrend_atr_length" or \
            #         _input == "supertrend_multiplier" or _input == "supertrend_atr_mamode":
            #     self.super_trend.change_input(dict_ta_params=self.supertrend_model.__dict__)
            
            self.fisrt_gen_data()
            
            # self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
    
    def get_xaxis_param(self):
        return None,"#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def calculate_stop_loss(self,_type:str, price:float):
        return calculate_stoploss(_type,price,0)
            
    
    def check_n_long_short_pos(self,is_new: bool=True,_type:str="long",n:int=5):
        sorted_pos = sorted(list(self.list_pos.keys()))
        if len(sorted_pos) < n:
            return False
        if is_new:
            pos =  sorted_pos[-n:]
        else:
            pos =  sorted_pos[:n]
        if pos:
            for i in pos:
                # print(self.list_pos[i]["type"],_type )
                if self.list_pos[i]["type"] != _type:
                    return False
        return True
    
    def check_last_pos(self):
        sorted_pos = sorted(list(self.list_pos.keys()))

        if len(sorted_pos) < 1:
            return None, False, False
        
        entry_infor = self.list_pos[sorted_pos[-1]]
        
        is_entry_closed =  entry_infor["is_stoploss"]
        is_take_profit_2R =  entry_infor["take_profit_2R"]
        is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
        
        entry_type = entry_infor["type"]
        
        stoploss = entry_infor["stop_loss"]
        
        entry:Entry = entry_infor["entry"]
        
        return entry_type, is_entry_closed, is_take_profit_2R
        
    
    
    def move_entry(self,index: float, high: float,low: float):
        return
        """
        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, 
        "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}"""
        sorted_pos = sorted(list(self.list_pos.keys()))

        if len(sorted_pos) < 1:
            return None, False, False
        
        entry_infor = self.list_pos[sorted_pos[-1]]
        
        is_entry_closed =  entry_infor["is_stoploss"]
        is_take_profit_2R =  entry_infor["take_profit_2R"]
        is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
        
        entry_type = entry_infor["type"]
        
        stoploss = entry_infor["stop_loss"]
        
        entry:Entry = entry_infor["entry"]
        
        if is_entry_closed or is_take_profit_2R:
            return True
        
        entry_pos_1_5R:QPointF = entry.has["inputs"]["data"][2.5].chart_pos
        entry_pos_2R:QPointF = entry.has["inputs"]["data"][3].chart_pos
        
        
        profit_2R = entry_pos_2R.y()
        profit_1_5R = entry_pos_1_5R.y()
        
        if entry_type == "long":
            if not is_take_profit_1_5R:
                if profit_1_5R <= high:
                    entry_infor["take_profit_1_5R"] = profit_1_5R
            if not is_take_profit_2R:
                if profit_2R <= high:
                    entry_infor["take_profit_2R"] = profit_2R
            if stoploss >= low:
                entry_infor["is_stoploss"] = True
        elif entry_type == "short":
            if not is_take_profit_1_5R:
                if profit_1_5R >= low:
                    entry_infor["take_profit_1_5R"] = profit_1_5R
            if not is_take_profit_2R:
                if profit_2R >= low:
                    entry_infor["take_profit_2R"] = profit_2R
            if stoploss <= high:
                entry_infor["is_stoploss"] = True
        
        is_entry_closed =  entry_infor["is_stoploss"]
        is_take_profit_2R =  entry_infor["take_profit_2R"]
        
        entry_y = entry_infor["entry_y"]
        # self.list_pos[sorted_pos[-1]]["entry_x"] = index
        self.list_pos[sorted_pos[-1]] = entry_infor
        # entry.moveEntry(index,entry_y)
        
        if is_entry_closed or is_take_profit_2R:
            entry.locked_handle()
    
    
    def check_pos_is_near_pivot(self,_x:int, check_type:str):
        
        stoploss_smooth_heikin = self.stoploss_smooth_heikin.df.loc[(self.stoploss_smooth_heikin.df['index'] >= _x-3) & (self.stoploss_smooth_heikin.df['index'] < _x)]
        
        if not stoploss_smooth_heikin.empty:
            
            pre_last_candle_open = stoploss_smooth_heikin.iloc[-1]["open"]
            pre_last_candle_close = stoploss_smooth_heikin.iloc[-1]["close"]
            
            pre_green = pre_last_candle_open - pre_last_candle_close < 0
            pre_red = pre_last_candle_open - pre_last_candle_close > 0
            
            for i in range(len(stoploss_smooth_heikin)):
                heikin_open = stoploss_smooth_heikin.iloc[i]["open"]
                heikin_close = stoploss_smooth_heikin.iloc[i]["close"]
                red = heikin_open - heikin_close > 0
                green = heikin_open - heikin_close < 0
                
                if check_type == "red" and red and pre_green:
                    return True
                elif check_type == "green" and green and pre_red:
                    return True
        return False
    
    def set_Data(self,df):
        if self.list_pos:
            for obj in self.list_pos.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["obj"])
                    # self.scene().removeItem(obj["entry"])
                    if hasattr(obj["obj"], "deleteLater"):
                        obj["obj"].deleteLater()
                    # if hasattr(obj["entry"], "deleteLater"):
                    #     obj["entry"].deleteLater()
                    # 
        self.list_pos.clear()   
        
        
        for i in range(1,len(df)):
            
            _x = df.iloc[i]['index']

            jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            jp_open = self.chart.jp_candle.map_index_ohlcv[_x].open
            jp_close = self.chart.jp_candle.map_index_ohlcv[_x].close
            
            
            pre_jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
            pre_jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
            pre_jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            pre_jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            pre_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            # cr_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            
            pre_sm_low = stoploss_long = None
            pre_sm_high = stoploss_short = None
            pre_sm_open = None
            pre_sm_close = None
            if not pre_smooth_heikin.empty:
                pre_sm_high = stoploss_short = pre_smooth_heikin.iloc[-1]["high"]
                pre_sm_low = stoploss_long = pre_smooth_heikin.iloc[-1]["low"]
                pre_sm_open = _open = pre_smooth_heikin.iloc[-1]["open"]
                pre_sm_close = _close = pre_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _open < _close  #and pre_jp_close > _close # and cr_jp_open > _close #and pre_jp_open < pre_jp_close
                smooth_heikin_short_signal = _open > _close #and pre_jp_close < _close # and cr_jp_open < _close #and pre_jp_open > pre_jp_close
                
            # self.move_entry(_x,cr_jp_high,cr_jp_low)
            if smooth_heikin_long_signal:# and sqz_long_signal:     
            # if super_trend_long_signal:     
                # _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "long":
                #     continue
                
                if self.cr_position["type"] != "long":
                    self.cr_position = {"type":"long","index":_x-1,"side_count":1}
                else:
                    self.cr_position["side_count"] = self.cr_position["side_count"] + 1
                
                if self.cr_position["side_count"] < 2:
                    continue
                
                if self.list_pos.get(self.cr_position["index"]):
                    continue
                
                is_small_change = False
                _max = max([pre_sm_close , pre_jp_close])
                _min = min([pre_sm_close , pre_jp_close])
                # if pre_sm_close < pre_jp_close:
                stoploss_percent = percent_caculator(_min, _max)
                if stoploss_percent < self.has["inputs"]["stoploss_price"]:
                    # continue
                    is_small_change = True
                    
                if pre_jp_close < pre_sm_low:
                        continue

                # if not self.check_pos_is_near_pivot(_x,"red"):
                #     continue
                
                # if not is_bearish(pre_jp_open,pre_jp_close):
                #     continue
                
                # if not is_bearish(pre_heikin_open,pre_heikin_close):
                #     continue

                index, text = None,None
                row = df.iloc[i-1]
                
                if row['evening_star'] == True:
                    # print(row['index'],row['evening_star'])
                    index = row['index']
                    text = 'evening_star'
                elif row['shooting_star'] == True:
                    # print(row['index'],row['shooting_star'])
                    index = row['index']
                    text = 'shooting_star'
                # elif row['bearish_harami'] == True:
                #     # print(row['index'],row['bearish_harami'])
                #     index = row['index']
                #     text = 'bearish_harami'
                elif row['bearish_engulfing'] == True:
                    # print(row['index'],row['bearish_engulfing'])
                    index = row['index']
                    text = 'bearish_engulfing'
                elif row['bearish_kicker'] == True:
                    # print(row['index'],row['bearish_kicker'])
                    index = row['index']
                    text = 'bearish_kicker'
                
                if (index and text) or is_small_change:
                    ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                    if ohlc:
                        # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                    #     obj = TextItem("",color="green")
                    #     obj.setParentItem(self)
                    #     txt = text.split("_")
                    #     txt1,txt2 = txt[0],txt[1]
                    #     html = f"""<div style="text-align: center">
                    # <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                    #     obj.setHtml(html)
                    #     obj.setAnchor((0.5,0))
                    #     r = obj.textItem.boundingRect()
                    #     tl = obj.textItem.mapToParent(r.topLeft())
                    #     br = obj.textItem.mapToParent(r.bottomRight())
                    #     offset = (br - tl) * obj.anchor
                    #     _y = ohlc.low-offset.y()/2
                    #     obj.setPos(Point(index,_y))
                        _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                                            
                        obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
                        obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                        obj.setParentItem(self)
                        obj.setPos(_x, _val)
                        obj.locked_handle()
                        # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                        stop_loss =  stoploss_short
                        # entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                        # entry.setPoint(_x-1,_val)
                        # entry.setParentItem(self)
                        # entry.moveEntry(_x,_val)
                        # self.chart.sig_add_item.emit(entry)
                        self.list_pos[self.cr_position["index"]] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            
            elif  smooth_heikin_short_signal:# and sqz_short_signal:    
            # elif  super_trend_short_signal:    
                # _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "short":
                #     continue
                
                if self.cr_position["type"] != "short":
                    self.cr_position = {"type":"short","index":_x-1,"side_count":1}
                else:
                    self.cr_position["side_count"] = self.cr_position["side_count"] + 1
                
                if self.cr_position["side_count"] < 2:
                    continue
                
                
                if self.list_pos.get(self.cr_position["index"]):
                    continue
                
                is_small_change = False
                _max = max([pre_sm_close , pre_jp_close])
                _min = min([pre_sm_close , pre_jp_close])
                # if pre_sm_close < pre_jp_close:
                stoploss_percent = percent_caculator(_max, _min)
                if stoploss_percent < self.has["inputs"]["stoploss_price"]:
                    # continue
                    is_small_change = True
                
                if pre_jp_close > pre_sm_high:
                        continue
                
                # if not self.check_pos_is_near_pivot(_x,"green"):
                #     continue
                
                # if not is_bulllish(pre_jp_open,pre_jp_close):
                #     continue
                
                # if not is_bulllish(pre_heikin_open,pre_heikin_close):
                #     continue
                
                index, text = None,None
                row = df.iloc[i-1]
                if row['morning_star'] == True:
                    # print(row['index'],row['morning_star'])
                    index = row['index']
                    text = 'morning_star'
                # elif row['bullish_harami'] == True:
                #     # print(row['index'],row['bullish_harami'])
                #     index = row['index']
                #     text = 'bullish_harami'
                elif row['bullish_engulfing'] == True:
                    index = row['index']
                    text = 'bullish_engulfing'
                elif row['bullish_kicker'] == True:
                    # print(row['index'],row['bullish_kicker'])
                    index = row['index']
                    text = 'bullish_kicker'
                    
                if (index and text) or is_small_change:
                    ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                    if ohlc:
                    #     obj = TextItem("",color="red")
                    #     obj.setParentItem(self)
                    #     obj.setAnchor((0.5,1))
                    #     txt = text.split("_")
                    #     txt1,txt2 = txt[0],txt[1]
                    #     html = f"""<div style="text-align: center">
                    # <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                    #     obj.setHtml(html)
                    #     obj.setPos(Point(index, ohlc.high))
                        _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                                            
                        obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
                        obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                        obj.setParentItem(self)
                        obj.setPos(_x, _val)
                        obj.locked_handle()
                        # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                        stop_loss =  stoploss_long
                        # entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                        # entry.setPoint(_x-1,_val)
                        # entry.setParentItem(self)
                        # entry.moveEntry(_x,_val)
                        # self.chart.sig_add_item.emit(entry)
                        self.list_pos[self.cr_position["index"]] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
          
        
    def add_historic_Data(self,df):
        for i in range(1,len(df)):
            
            _x = df.iloc[i]['index']

            jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            jp_open = self.chart.jp_candle.map_index_ohlcv[_x].open
            jp_close = self.chart.jp_candle.map_index_ohlcv[_x].close
            
            
            pre_jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
            pre_jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
            pre_jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            pre_jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            pre_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            # cr_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            
            pre_sm_low = stoploss_long = None
            pre_sm_high = stoploss_short = None
            pre_sm_open = None
            pre_sm_close = None
            if not pre_smooth_heikin.empty:
                pre_sm_high = stoploss_short = pre_smooth_heikin.iloc[-1]["high"]
                pre_sm_low = stoploss_long = pre_smooth_heikin.iloc[-1]["low"]
                pre_sm_open = _open = pre_smooth_heikin.iloc[-1]["open"]
                pre_sm_close = _close = pre_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _open < _close  #and pre_jp_close > _close # and cr_jp_open > _close #and pre_jp_open < pre_jp_close
                smooth_heikin_short_signal = _open > _close #and pre_jp_close < _close # and cr_jp_open < _close #and pre_jp_open > pre_jp_close
                
            
            # self.move_entry(_x,cr_jp_high,cr_jp_low)
            if smooth_heikin_long_signal:# and sqz_long_signal:     
            # if super_trend_long_signal:     
                # _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "long":
                #     continue
                
                if self.cr_position["type"] != "long":
                    self.cr_position = {"type":"long","index":_x-1,"side_count":1}
                else:
                    self.cr_position["side_count"] = self.cr_position["side_count"] + 1
                
                if self.cr_position["side_count"] < 2:
                    continue
                
                if self.list_pos.get(self.cr_position["index"]):
                    continue
                
                is_small_change = False
                _max = max([pre_sm_close , pre_jp_close])
                _min = min([pre_sm_close , pre_jp_close])
                # if pre_sm_close < pre_jp_close:
                stoploss_percent = percent_caculator(_min, _max)
                if stoploss_percent < self.has["inputs"]["stoploss_price"]:
                    # continue
                    is_small_change = True
                
                if pre_jp_close < pre_sm_low:
                        continue
                # if not self.check_pos_is_near_pivot(_x,"red"):
                #     continue
                
                # if not is_bearish(pre_jp_open,pre_jp_close):
                #     continue
                
                # if not is_bearish(pre_heikin_open,pre_heikin_close):
                #     continue

                index, text = None,None
                row = df.iloc[i-1]
                
                if row['evening_star'] == True:
                    # print(row['index'],row['evening_star'])
                    index = row['index']
                    text = 'evening_star'
                elif row['shooting_star'] == True:
                    # print(row['index'],row['shooting_star'])
                    index = row['index']
                    text = 'shooting_star'
                # elif row['bearish_harami'] == True:
                #     # print(row['index'],row['bearish_harami'])
                #     index = row['index']
                #     text = 'bearish_harami'
                elif row['bearish_engulfing'] == True:
                    # print(row['index'],row['bearish_engulfing'])
                    index = row['index']
                    text = 'bearish_engulfing'
                elif row['bearish_kicker'] == True:
                    # print(row['index'],row['bearish_kicker'])
                    index = row['index']
                    text = 'bearish_kicker'
                
                if (index and text) or is_small_change:
                    ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                    if ohlc:
                        # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                    #     obj = TextItem("",color="green")
                    #     obj.setParentItem(self)
                    #     txt = text.split("_")
                    #     txt1,txt2 = txt[0],txt[1]
                    #     html = f"""<div style="text-align: center">
                    # <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                    #     obj.setHtml(html)
                    #     obj.setAnchor((0.5,0))
                    #     r = obj.textItem.boundingRect()
                    #     tl = obj.textItem.mapToParent(r.topLeft())
                    #     br = obj.textItem.mapToParent(r.bottomRight())
                    #     offset = (br - tl) * obj.anchor
                    #     _y = ohlc.low-offset.y()/2
                    #     obj.setPos(Point(index,_y))
                        _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                                            
                        obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
                        obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                        obj.setParentItem(self)
                        obj.setPos(_x, _val)
                        obj.locked_handle()
                        # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                        stop_loss =  stoploss_short
                        # entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                        # entry.setPoint(_x-1,_val)
                        # entry.setParentItem(self)
                        # entry.moveEntry(_x,_val)
                        # self.chart.sig_add_item.emit(entry)
                        
                        self.list_pos[self.cr_position["index"]] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            
            elif  smooth_heikin_short_signal:# and sqz_short_signal:    
            # elif  super_trend_short_signal:    
                # _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "short":
                #     continue

                
                if self.cr_position["type"] != "short":
                    self.cr_position = {"type":"short","index":_x-1,"side_count":1}
                else:
                    self.cr_position["side_count"] = self.cr_position["side_count"] + 1
                
                if self.cr_position["side_count"] < 2:
                    continue
                
                
                if self.list_pos.get(self.cr_position["index"]):
                    continue
                
                is_small_change = False
                _max = max([pre_sm_close , pre_jp_close])
                _min = min([pre_sm_close , pre_jp_close])
                # if pre_sm_close < pre_jp_close:
                stoploss_percent = percent_caculator(_max, _min)
                if stoploss_percent < self.has["inputs"]["stoploss_price"]:
                    # continue
                    is_small_change = True
                
                if pre_jp_close > pre_sm_high:
                        continue
                
                # if not self.check_pos_is_near_pivot(_x,"green"):
                #     continue
                
                # if not is_bulllish(pre_jp_open,pre_jp_close):
                #     continue
                
                # if not is_bulllish(pre_heikin_open,pre_heikin_close):
                #     continue
                
                index, text = None,None
                row = df.iloc[i-1]
                if row['morning_star'] == True:
                    # print(row['index'],row['morning_star'])
                    index = row['index']
                    text = 'morning_star'
                # elif row['bullish_harami'] == True:
                #     # print(row['index'],row['bullish_harami'])
                #     index = row['index']
                #     text = 'bullish_harami'
                elif row['bullish_engulfing'] == True:
                    index = row['index']
                    text = 'bullish_engulfing'
                elif row['bullish_kicker'] == True:
                    # print(row['index'],row['bullish_kicker'])
                    index = row['index']
                    text = 'bullish_kicker'
                    
                if (index and text) or is_small_change:
                    ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                    if ohlc:
                    #     obj = TextItem("",color="red")
                    #     obj.setParentItem(self)
                    #     obj.setAnchor((0.5,1))
                    #     txt = text.split("_")
                    #     txt1,txt2 = txt[0],txt[1]
                    #     html = f"""<div style="text-align: center">
                    # <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                    #     obj.setHtml(html)
                    #     obj.setPos(Point(index, ohlc.high))
                        _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                                            
                        obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
                        obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                        obj.setParentItem(self)
                        obj.setPos(_x, _val)
                        obj.locked_handle()
                        # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                        stop_loss =  stoploss_long
                        # entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                        # entry.setPoint(_x-1,_val)
                        # entry.setParentItem(self)
                        # entry.moveEntry(_x,_val)
                        # self.chart.sig_add_item.emit(entry)
                        self.list_pos[self.cr_position["index"]] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
          
    
    def update_Data(self,df: pd.DataFrame):
        while not self.is_all_updated():
            print("not updated")
            time.sleep(0.01)
            continue
        
        # for i in range(1,len(df)):
        _x = df.iloc[-1]['index']
        
        # jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
        # jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
        # jp_open = self.chart.jp_candle.map_index_ohlcv[_x].open
        # jp_close = self.chart.jp_candle.map_index_ohlcv[_x].close
        
        # pre_jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
        # pre_jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
        # pre_jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
        pre_jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
        
        pre_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
        # cr_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
        smooth_heikin_short_signal = False
        smooth_heikin_long_signal = False
        
        pre_sm_low = stoploss_long = None
        pre_sm_high = stoploss_short = None
        pre_sm_open = None
        pre_sm_close = None
        
        row = df.iloc[-2]
            
        if not pre_smooth_heikin.empty:
            pre_sm_high = stoploss_short = pre_smooth_heikin.iloc[-1]["high"]
            pre_sm_low = stoploss_long = pre_smooth_heikin.iloc[-1]["low"]
            pre_sm_open = _open = pre_smooth_heikin.iloc[-1]["open"]
            pre_sm_close = _close = pre_smooth_heikin.iloc[-1]["close"]
            smooth_heikin_long_signal = _open < _close  #and pre_jp_close > _close # and cr_jp_open > _close #and pre_jp_open < pre_jp_close
            smooth_heikin_short_signal = _open > _close #and pre_jp_close < _close # and cr_jp_open < _close #and pre_jp_open > pre_jp_close
            
        
        # self.move_entry(_x,cr_jp_high,cr_jp_low)
        if smooth_heikin_long_signal:# and sqz_long_signal:     
        # if super_trend_long_signal:     
            # _type,is_sl,is_tp = self.check_last_pos()
            # if _type == "long":
            #     continue
            
                
            if self.cr_position["type"] != "long":
                self.cr_position = {"type":"long","index":_x-1,"side_count":1}
            else:
                self.cr_position["side_count"] = self.cr_position["side_count"] + 1
            
            if self.cr_position["side_count"] < 2:
                return
            
            if self.list_pos.get(self.cr_position["index"]):
                return
            
            is_small_change = False
            _max = max([pre_sm_close , pre_jp_close])
            _min = min([pre_sm_close , pre_jp_close])
            # if pre_sm_close < pre_jp_close:
            stoploss_percent = percent_caculator(_min, _max)
            if stoploss_percent < self.has["inputs"]["stoploss_price"]:
                # continue
                is_small_change = True
                    
            if pre_jp_close < pre_sm_low:
                return
            # if not self.check_pos_is_near_pivot(_x,"red"):
            #     continue
            
            # if not is_bearish(pre_jp_open,pre_jp_close):
            #     continue
            
            # if not is_bearish(pre_heikin_open,pre_heikin_close):
            #     continue

            index, text = None,None
            row = df.iloc[-2]
            
            # print("okieee row", _x, row)
            
            if row['evening_star'] == True:
                # print(row['index'],row['evening_star'])
                index = row['index']
                text = 'evening_star'
            elif row['shooting_star'] == True:
                # print(row['index'],row['shooting_star'])
                index = row['index']
                text = 'shooting_star'
            # elif row['bearish_harami'] == True:
            #     # print(row['index'],row['bearish_harami'])
            #     index = row['index']
            #     text = 'bearish_harami'
            elif row['bearish_engulfing'] == True:
                # print(row['index'],row['bearish_engulfing'])
                index = row['index']
                text = 'bearish_engulfing'
            elif row['bearish_kicker'] == True:
                # print(row['index'],row['bearish_kicker'])
                index = row['index']
                text = 'bearish_kicker'
            
            if (index and text) or is_small_change:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                #     obj = TextItem("",color="green")
                #     obj.setParentItem(self)
                #     txt = text.split("_")
                #     txt1,txt2 = txt[0],txt[1]
                #     html = f"""<div style="text-align: center">
                # <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                #     obj.setHtml(html)
                #     obj.setAnchor((0.5,0))
                #     r = obj.textItem.boundingRect()
                #     tl = obj.textItem.mapToParent(r.topLeft())
                #     br = obj.textItem.mapToParent(r.bottomRight())
                #     offset = (br - tl) * obj.anchor
                #     _y = ohlc.low-offset.y()/2
                #     obj.setPos(Point(index,_y))
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                                        
                    obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_short
                    # entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    # entry.setPoint(_x-1,_val)
                    # entry.setParentItem(self)
                    # entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[self.cr_position["index"]] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
        
        elif  smooth_heikin_short_signal:# and sqz_short_signal:    
        # elif  super_trend_short_signal:    
            # _type,is_sl,is_tp = self.check_last_pos()
            # if _type == "short":
            #     continue

            if self.cr_position["type"] != "short":
                self.cr_position = {"type":"short","index":_x-1,"side_count":1}
            else:
                self.cr_position["side_count"] = self.cr_position["side_count"] + 1
            
            if self.cr_position["side_count"] < 2:
                return
            
            if self.list_pos.get(self.cr_position["index"]):
                return

            is_small_change = False
            _max = max([pre_sm_close , pre_jp_close])
            _min = min([pre_sm_close , pre_jp_close])
            # if pre_sm_close < pre_jp_close:
            stoploss_percent = percent_caculator(_max, _min)
            if stoploss_percent < self.has["inputs"]["stoploss_price"]:
                # continue
                is_small_change = True
                    
                    
            if pre_jp_close > pre_sm_high:
                return
            # if not self.check_pos_is_near_pivot(_x,"green"):
            #     continue
            
            # if not is_bulllish(pre_jp_open,pre_jp_close):
            #     continue
            
            # if not is_bulllish(pre_heikin_open,pre_heikin_close):
            #     continue
            
            index, text = None,None
            row = df.iloc[-2]
            
            # print("okieee row", _x, row)
            
            if row['morning_star'] == True:
                # print(row['index'],row['morning_star'])
                index = row['index']
                text = 'morning_star'
            # elif row['bullish_harami'] == True:
            #     # print(row['index'],row['bullish_harami'])
            #     index = row['index']
            #     text = 'bullish_harami'
            elif row['bullish_engulfing'] == True:
                index = row['index']
                text = 'bullish_engulfing'
            elif row['bullish_kicker'] == True:
                # print(row['index'],row['bullish_kicker'])
                index = row['index']
                text = 'bullish_kicker'
                
            if (index and text) or is_small_change:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                #     obj = TextItem("",color="red")
                #     obj.setParentItem(self)
                #     obj.setAnchor((0.5,1))
                #     txt = text.split("_")
                #     txt1,txt2 = txt[0],txt[1]
                #     html = f"""<div style="text-align: center">
                # <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                #     obj.setHtml(html)
                #     obj.setPos(Point(index, ohlc.high))
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                                        
                    obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_long
                    # entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    # entry.setPoint(_x-1,_val)
                    # entry.setParentItem(self)
                    # entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[self.cr_position["index"]] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
    
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
        df= self.INDICATOR.get_data(stop=_len)
        setdata.emit(df)
        
    def add_data(self,setdata):
        df = self.INDICATOR.get_data(start=-10)
        setdata.emit(df)
    
    def update_data(self,setdata):
        df= self.INDICATOR.get_data(start=-10)
        setdata.emit(df)

    def boundingRect(self) -> QRectF:
        if self.list_pos:
            x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
            for _x in list(self.list_pos.keys()):
                obj = self.list_pos.get(_x)
                if obj:
                    if x_left < _x < x_right:
                        obj["obj"].show()
                    else:
                        obj["obj"].hide()

        return self.picture.boundingRect()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
        # p.drawRect(self.boundingRect())
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return None,None
    
    def get_last_point(self):
        return None,None
    
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
        #print("zooo day__________________")
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    