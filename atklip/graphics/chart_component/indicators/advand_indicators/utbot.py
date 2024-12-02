import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.graphics.pyqtgraph import GraphicsObject

from atklip.controls import PD_MAType,IndicatorType,ATKBOT_ALERT
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
                    
                    "stoploss_price":0.01,
                    
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
        
        self.INDICATOR  = ATKBOT_ALERT(self.has["inputs"]["source"], self.model.__dict__)
                
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update 
        return True
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
        xdata,_long,_short= self.INDICATOR.get_data()
        setdata.emit((xdata,_long,_short))
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
                # self.stoploss_smooth_heikin.fisrt_gen_data()
                # self.super_trend.fisrt_gen_data()
                self.sqeeze.fisrt_gen_data()

            
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
    
    def set_Data(self,data):
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
        xdata,_long,_short = data[0],data[1],data[2]

        for i in range(1,len(self.stoploss_smooth_heikin.df)):
            _x = self.stoploss_smooth_heikin.df.iloc[i]['index']

            pre_jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
            pre_jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
            pre_jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            pre_jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            
            pre_heikin_high = self.chart.heikinashi.map_index_ohlcv[_x-1].high
            pre_heikin_low = self.chart.heikinashi.map_index_ohlcv[_x-1].low
            pre_heikin_open = self.chart.heikinashi.map_index_ohlcv[_x-1].open
            pre_heikin_close = self.chart.heikinashi.map_index_ohlcv[_x-1].close
            
            
            cr_jp_open = self.chart.jp_candle.map_index_ohlcv[_x].open
            cr_jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            cr_jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            
            row_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            # cr_row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            
            sm_low = stoploss_long = None
            sm_high = stoploss_short = None
            sm_open = None
            sm_close = None
            if not row_smooth_heikin.empty:
                sm_high = stoploss_short = _high = row_smooth_heikin.iloc[-1]["high"]
                sm_low = stoploss_long = _low = row_smooth_heikin.iloc[-1]["low"]
                sm_open = _open = row_smooth_heikin.iloc[-1]["open"]
                sm_close = _close = row_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _open < _close  #and pre_jp_close > _close # and cr_jp_open > _close #and pre_jp_open < pre_jp_close
                smooth_heikin_short_signal = _open > _close #and pre_jp_close < _close # and cr_jp_open < _close #and pre_jp_open > pre_jp_close
                

            
            # super_trend_df = self.super_trend.df.loc[(self.super_trend.df['index'] <= _x-1) & (self.super_trend.df['index'] >= _x-4)]
            # super_trend_long_signal = False
            # super_trend_short_signal = False
            # if len(super_trend_df) >= 3:
            #     sqz_histogram = super_trend_df.iloc[-1]['SUPERTd']
            #     super_trend_long_signal = sqz_histogram > 0 
            #     super_trend_short_signal = sqz_histogram < 0
            
            
            # sqeezee_df = self.sqeeze.df.loc[(self.sqeeze.df['index'] <= _x-1) & (self.sqeeze.df['index'] >= _x-4)]
            # sqz_histogram = None
            # sqz_long_signal = False
            # sqz_short_signal = False
            # if len(sqeezee_df) >= 3:
            #     sqz_histogram = sqeezee_df.iloc[-1]['SQZ_data']
            #     sqz_histogram_pre_1 = sqeezee_df.iloc[-2]['SQZ_data']
            #     sqz_histogram_pre_2 = sqeezee_df.iloc[-3]['SQZ_data']

            #     if sqz_histogram > 0 and sqz_histogram_pre_1 > 0:# and sqz_histogram_pre_2 > 0:
            #         if sqz_histogram < sqz_histogram_pre_1:
            #             sqz_long_signal = True
            #         elif sqz_histogram > sqz_histogram_pre_1:
            #             sqz_short_signal = True
            #     elif sqz_histogram < 0 and sqz_histogram_pre_1 < 0:# and sqz_histogram_pre_2 < 0:
            #         if sqz_histogram < sqz_histogram_pre_1:
            #             sqz_short_signal = True
            #         elif sqz_histogram > sqz_histogram_pre_1:
            #             sqz_long_signal = True
            
            # self.move_entry(_x,cr_jp_high,cr_jp_low)
            if smooth_heikin_long_signal:# and sqz_long_signal:     
            # if super_trend_long_signal:     
                _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "long":
                #     continue
                if sm_high < pre_jp_low:
                    stoploss_percent = percent_caculator(sm_high, pre_jp_low)
                    if stoploss_percent > self.has["inputs"]["stoploss_price"]:
                        continue
                # if pre_jp_low < sm_low:
                #         continue

                # if not self.check_pos_is_near_pivot(_x,"red"):
                #     continue
                
                if not is_bearish(pre_jp_open,pre_jp_close):
                    continue
                
                if not is_bearish(pre_heikin_open,pre_heikin_close):
                    continue
                
                
                _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                    
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
                self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            elif  smooth_heikin_short_signal:# and sqz_short_signal:    
            # elif  super_trend_short_signal:    
                # _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "short":
                #     continue
                if sm_low > pre_jp_high:
                    stoploss_percent = percent_caculator(sm_low, pre_jp_high)
                    if stoploss_percent > self.has["inputs"]["stoploss_price"]:
                        continue
                # if pre_jp_high > sm_high:
                #         continue
                
                # if not self.check_pos_is_near_pivot(_x,"green"):
                #     continue
                
                if not is_bulllish(pre_jp_open,pre_jp_close):
                    continue
                
                if not is_bulllish(pre_heikin_open,pre_heikin_close):
                    continue
                
                _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                    
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
                self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
        
    
            
                
    def old_set_Data(self,data):
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
        
        xdata,_long,_short = data[0],data[1],data[2]
             
        df = pd.DataFrame({
            "x":xdata,
            "long":_long,
            "short":_short,
        })
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']

            if i-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1 <=0:
                    continue
            
            
            jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            jp_open = self.chart.jp_candle.map_index_ohlcv[_x].open
            jp_close = self.chart.jp_candle.map_index_ohlcv[_x].close
            
            
            row_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            # cr_row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            if not row_smooth_heikin.empty:
                _high = row_smooth_heikin.iloc[-1]["high"]
                _low = row_smooth_heikin.iloc[-1]["low"]
                _open = row_smooth_heikin.iloc[-1]["open"]
                _close = row_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _open < _close #and jp_open < jp_close
                smooth_heikin_short_signal = _open > _close #and jp_open > jp_close

            stoploss_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            sm_low = stoploss_long = None
            sm_high = stoploss_short = None
            if not stoploss_smooth_heikin.empty:
                sm_low = stoploss_long = stoploss_smooth_heikin.iloc[-1]["low"]
                sm_high = stoploss_short = stoploss_smooth_heikin.iloc[-1]["high"]
                
                
                
                
            
            # self.move_entry(_x,cr_jp_high,cr_jp_low)
            
            # super_trend_df = self.super_trend.df.loc[(self.super_trend.df['index'] <= _x-1)]
            # super_trend_long_signal = True
            # super_trend_short_signal = True
            # if not super_trend_df.empty:
            #     sqz_histogram = super_trend_df.iloc[-1]['SUPERTd']
                # super_trend_long_signal = sqz_histogram > 0 
                # super_trend_short_signal = sqz_histogram < 0
            

            if df.iloc[i-1]['long'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                # if _type == "long":
                #     if is_sl == True:
                #         pass
                #     else:
                #         continue
                
                stoploss_percent = percent_caculator(stoploss_long, jp_open)
                
                if stoploss_percent > self.has["inputs"]["stoploss_price"]:
                    continue
                
                # if jp_open < sm_high:
                #     continue
                
                # if not self.check_pos_is_near_pivot(_x,"red"):
                #     continue
                
                
                if smooth_heikin_long_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
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
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            elif df.iloc[i-1]['short'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                stoploss_percent = percent_caculator(stoploss_short, jp_open)
                
                if stoploss_percent > self.has["inputs"]["stoploss_price"]:
                    continue
                
                # if jp_open > sm_low:
                #     continue
                
                # if not self.check_pos_is_near_pivot(_x,"green"):
                #     continue
                
                # if _type == "short":
                #     if is_sl:
                #         pass
                #     else:
                #         continue
                
                if  smooth_heikin_short_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
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
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":None, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            
        
        
    def add_historic_Data(self,data):
        return
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        df = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        # df = data.loc[(data['long'] == True) | (data['short'] == True)]
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']
            
            

            if i-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1 <=0:
                    continue
            
            # row = self.smoothcandle.df.loc[self.smoothcandle.df['index'] == _x-1]
            # sm_candle_short_signal = False
            # sm_candle_long_signal = False
            # if not row.empty:
            #     _high = row.iloc[-1]["high"]
            #     _low = row.iloc[-1]["low"]
            #     _open = row.iloc[-1]["open"]
            #     _close = row.iloc[-1]["close"]
            #     sm_candle_long_signal = _open < _close
            #     sm_candle_short_signal = _open > _close
            
            # jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            # jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            # macd_df = self.macd.df.loc[(self.macd.df['index'] == _x-1)]
            # macd = None
            # signalma = None
            # histogram = None
            # macd_long_signal = False
            # macd_short_signal = False
            # if len(macd_df) > 0:
            #     macd = macd_df.iloc[-1]['macd']
            #     signalma = macd_df.iloc[-1]['signalma']
            #     histogram = macd_df.iloc[-1]['histogram']
                
            #     macd_long_signal = ((histogram < 0) and (self.has["inputs"]["min_price_low"] < signalma < self.has["inputs"]["price_low"])  and (macd < 0)) 
            #     macd_short_signal = ((histogram > 0) and (self.has["inputs"]["price_high"] < signalma < self.has["inputs"]["max_price_high"])  and (macd > 0))
            
            if df.iloc[i-1]['long'] == True:
                # if self.check_n_long_short_pos(True,"long",1):
                #     continue
                
                pv_df =  self.chart.jp_candle.df.loc[(self.chart.jp_candle.df['index'] < _x) & (self.chart.jp_candle.df['index'] >= _x-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1)]   
                pivot_point = self.check_pivot_points(pv_df,"low",self.has["inputs"]["n_period"],self.has["inputs"]["m_period"])
                
                if self.list_pos.get(pivot_point[2]):
                    continue
                
                if pivot_point[0]:
  
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                    
                    if macd_long_signal and sm_candle_long_signal:
                        obj = BaseArrowItem(drawtool=self,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                        obj.setParentItem(self)
                        obj.setPos(_x, _val)
                        obj.locked_handle()
                        self.chart.sig_add_item.emit(obj)
                        entry = Entry([pivot_point[2], pivot_point[1]], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self.chart.drawtool)
                        
                        entry.setPoint(_x,_val)
                        entry.locked_handle()
                        entry.setParentItem(self)
                        self.chart.sig_add_item.emit(entry)
                        
                        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry}
            elif df.iloc[i-1]['short'] == True:
                # if self.check_n_long_short_pos(True,"short",1):
                #     continue
                pv_df =  self.chart.jp_candle.df.loc[(self.chart.jp_candle.df['index'] < _x) & (self.chart.jp_candle.df['index'] >= _x-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1)]   
                pivot_point = self.check_pivot_points(pv_df,"high",self.has["inputs"]["n_period"],self.has["inputs"]["m_period"])
                if self.list_pos.get(pivot_point[2]):
                    continue
                if pivot_point[0]:
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                    "Check dieu kien so voi smcandle 50"
                    if macd_short_signal and sm_candle_short_signal:
                        obj =  BaseArrowItem(drawtool=self,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                        obj.setParentItem(self)
                        obj.locked_handle()
                        obj.setPos(_x, _val)
                        self.chart.sig_add_item.emit(obj)
                        entry = Entry([pivot_point[2], pivot_point[1]], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self.chart.drawtool)
                        
                        entry.setPoint(_x,_val)
                        entry.locked_handle()
                        entry.setParentItem(self)
                        self.chart.sig_add_item.emit(entry)
                        
                        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry}
        
    
    def update_Data(self,data):
        return
        # while not self.is_all_updated():
        #     time.sleep(0.01)
        #     print("not updated yet")
        #     continue
        
        xdata,_long,_short = data[0],data[1],data[2]
             
        df = pd.DataFrame({
            "x":xdata,
            "long":_long,
            "short":_short,
        })
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']

            if i-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1 <=0:
                    continue
            
            row = self.super_smoothcandle.df.loc[self.super_smoothcandle.df['index'] == _x-1]
            sm_candle_short_signal = False
            sm_candle_long_signal = False
            if not row.empty:
                _high = row.iloc[-1]["high"]
                _low = row.iloc[-1]["low"]
                _open = row.iloc[-1]["open"]
                _close = row.iloc[-1]["close"]
                sm_candle_long_signal = _open < _close
                sm_candle_short_signal = _open > _close
            
            
            jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
            jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
            jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            
            row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x-1]
            # cr_row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            if not row_smooth_heikin.empty:
                _high = row_smooth_heikin.iloc[-1]["high"]
                _low = row_smooth_heikin.iloc[-1]["low"]
                _open = row_smooth_heikin.iloc[-1]["open"]
                _close = row_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _high < jp_low and jp_open < jp_close
                smooth_heikin_short_signal = _low > jp_high and jp_open > jp_close
                

            stoploss_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            stoploss_long = None
            stoploss_short = None
            if not stoploss_smooth_heikin.empty:
                stoploss_long = stoploss_smooth_heikin.iloc[-1]["low"]
                stoploss_short = stoploss_smooth_heikin.iloc[-1]["high"]
            
            cr_jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            cr_jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            self.move_entry(_x,cr_jp_high,cr_jp_low)
            
            super_trend_df = self.super_trend.df.loc[(self.super_trend.df['index'] <= _x-1) & (self.super_trend.df['index'] >= _x-4)]
            super_trend_long_signal = False
            super_trend_short_signal = False
            if len(super_trend_df) >= 3:
                sqz_histogram = super_trend_df.iloc[-1]['SUPERTd']
                super_trend_long_signal = sqz_histogram > 0 
                super_trend_short_signal = sqz_histogram < 0
            

            if df.iloc[i-1]['long'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                if _type == "long":
                    if is_sl == True:
                        pass
                    else:
                        continue

                if super_trend_long_signal and sm_candle_long_signal and smooth_heikin_long_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
                    obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_short
                    entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    entry.setPoint(_x-1,_val)
                    entry.setParentItem(self)
                    entry.moveEntry(_x,_val)
                    self.chart.sig_add_item.emit(entry)
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            elif df.iloc[i-1]['short'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                if _type == "short":
                    if is_sl:
                        pass
                    else:
                        continue
                
                # elif _type == "long":
                #     _open = self.chart.jp_candle.map_index_ohlcv[_x].open
                #     self.check_active_other_side_pos("long",_open)
                
                if  super_trend_short_signal and sm_candle_short_signal and smooth_heikin_short_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
                    obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_long
                    entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    entry.setPoint(_x-1,_val)
                    entry.setParentItem(self)
                    entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            
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
        xdata,_long,_short= self.INDICATOR.get_data(start=-int(self.has["inputs"]["n_period"]+self.has["inputs"]["m_period"]+10))
        setdata.emit((xdata,_long,_short))
    
    def update_data(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(start=-int(self.has["inputs"]["n_period"]+self.has["inputs"]["m_period"]+10))
        setdata.emit((xdata,_long,_short))

    def boundingRect(self) -> QRectF:
        # if self.list_pos:
        #     x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        #     for _x in self.list_pos.keys():
        #         obj = self.list_pos.get(_x)
        #         if obj:
        #             if x_left < _x < x_right:
        #                 obj["obj"].show()
        #             else:
        #                 obj["obj"].hide()

        return self.picture.boundingRect()
    
    def paint(self, p:QPainter, *args):
        # self.picture.play(p)
        p.drawRect(self.boundingRect())
    
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
    