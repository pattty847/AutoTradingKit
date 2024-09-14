# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.utils import v_offset, v_pos_default, v_series



def donchian(
    high: Series, low: Series,
    lower_length: Int = None, upper_length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Donchian Channels (DC)

    Donchian Channels are used to measure volatility, similar to
    Bollinger Bands and Keltner Channels.

    Sources:
        https://www.tradingview.com/wiki/Donchian_Channels_(DC)

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        lower_length (int): The short period. Default: 20
        upper_length (int): The short period. Default: 20
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: lower, mid, upper columns.
    """
    # Validate
    lower_length = v_pos_default(lower_length, 20)
    upper_length = v_pos_default(upper_length, 20)
    lmin_periods = int(kwargs.pop("lmin_periods", lower_length))
    umin_periods = int(kwargs.pop("umin_periods", upper_length))

    _length = max(lower_length, lmin_periods, upper_length, umin_periods)
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    offset = v_offset(offset)

    # Calculate
    lower = low.rolling(lower_length, min_periods=lmin_periods).min()
    upper = high.rolling(upper_length, min_periods=umin_periods).max()
    mid = 0.5 * (lower + upper)

    # Fill
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)

    # Name and Category
    lower.name = f"DCL_{lower_length}_{upper_length}"
    mid.name = f"DCM_{lower_length}_{upper_length}"
    upper.name = f"DCU_{lower_length}_{upper_length}"
    mid.category = upper.category = lower.category = "volatility"

    data = {lower.name: lower, mid.name: mid, upper.name: upper}
    df = DataFrame(data, index=high.index)
    df.name = f"DC_{lower_length}_{upper_length}"
    df.category = mid.category

    return df

import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class DONCHIAN(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    def __init__(self,parent,_candles,lower_length,upper_length) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
                
        self.lower_length:int = lower_length
        self.upper_length:int = upper_length

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"DC {self.lower_length} {self.upper_length}"

        self.df = pd.DataFrame([])
        
        self.xdata,self.lb,self.cb,self.ub = np.array([]),np.array([]),np.array([]),np.array([])

        self.connect_signals()
        
    def disconnect_signals(self):
        try:
            self._candles.sig_reset_all.disconnect(self.started_worker)
            self._candles.sig_update_candle.disconnect(self.update_worker)
            self._candles.sig_add_candle.disconnect(self.add_worker)
            self._candles.signal_delete.disconnect(self.signal_delete)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self._candles.sig_reset_all.connect(self.started_worker,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update_worker,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.QueuedConnection)
        self._candles.signal_delete.connect(self.signal_delete)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        is_update = False
        print(_input)
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "period_lower":
            self.lower_length = _source
            is_update = True
        elif _input == "period_upper":
            self.upper_length = _source
            is_update = True
        if is_update:
            self.started_worker()
    
    @property
    def indicator_name(self):
        return self.name
    @indicator_name.setter
    def indicator_name(self,_name):
        self.name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self):
        return self.xdata,self.lb,self.cb,self.ub
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    def update_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.update,candle)
        self.worker_.start()
    
    def add_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add,candle)
        self.worker_.start()
    
    def started_worker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    
    def paire_data(self,INDICATOR:DataFrame):
        column_names = INDICATOR.columns.tolist()
        INDICATOR.astype('float32')
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("DCL_"):
                lower_name = name
            elif name.__contains__("DCM_"):
                mid_name = name
            elif name.__contains__("DCU_"):
                upper_name = name

        lb = INDICATOR[lower_name]
        cb = INDICATOR[mid_name]
        ub = INDICATOR[upper_name]
        return lb,cb,ub
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        INDICATOR = donchian(high=df["high"],low=df["low"],lower_length=self.lower_length,upper_length=self.upper_length)
        _index = df["index"]
        lb,cb,ub = self.paire_data(INDICATOR)

        self.df = pd.DataFrame({
                            'index':_index,
                            "lb":lb,
                            "cb":cb,
                            "ub":ub
                            })
                
        self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),\
                                                self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.upper_length*5)
                    
            INDICATOR = donchian(high=df["high"],low=df["low"],lower_length=self.lower_length,upper_length=self.upper_length)
            
            lb,cb,ub = self.paire_data(INDICATOR)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "lb":[lb.iloc[-1]],
                                    "cb":[cb.iloc[-1]],
                                    "ub":[ub.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                
            self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),\
                                                self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
            
           
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.upper_length*5)
                    
            INDICATOR = donchian(high=df["high"],low=df["low"],lower_length=self.lower_length,upper_length=self.upper_length)
            
            lb,cb,ub = self.paire_data(INDICATOR)
                    
            self.df.iloc[-1] = [new_candle.index,lb.iloc[-1],cb.iloc[-1],ub.iloc[-1]]
                    
            self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),\
                                                self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
            
            self.sig_update_candle.emit()
            
