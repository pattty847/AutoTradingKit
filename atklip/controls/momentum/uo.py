# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def uo(
    high: Series, low: Series, close: Series,
    fast: Int = None, medium: Int = None, slow: Int = None,
    fast_w: IntFloat = None, medium_w: IntFloat = None, slow_w: IntFloat = None,
    talib: bool = False, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Ultimate Oscillator (UO)

    The Ultimate Oscillator is a momentum indicator over three different
    periods.  It attempts to correct false divergence trading signals.

    Sources:
        https://www.tradingview.com/wiki/Ultimate_Oscillator_(UO)

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        fast (int): The Fast %K period. Default: 7
        medium (int): The Slow %K period. Default: 14
        slow (int): The Slow %D period. Default: 28
        fast_w (float): The Fast %K period. Default: 4.0
        medium_w (float): The Slow %K period. Default: 2.0
        slow_w (float): The Slow %D period. Default: 1.0
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        drift (int): The difference period. Default: 1
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    fast = v_pos_default(fast, 7)
    medium = v_pos_default(medium, 14)
    slow = v_pos_default(slow, 28)
    _length = max(fast, medium, slow) + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    fast_w = v_pos_default(fast_w, 4.0)
    medium_w = v_pos_default(medium_w, 2.0)
    slow_w = v_pos_default(slow_w, 1.0)
    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from atklip.controls.talib import ULTOSC
        uo = ULTOSC(high, low, close, fast, medium, slow)
    else:
        close_drift = close.shift(drift)
        tdf = DataFrame({
            "high": high, "low": low, f"close_{drift}": close_drift
        })
        max_h_or_pc = tdf.loc[:, ["high", f"close_{drift}"]].max(axis=1)
        min_l_or_pc = tdf.loc[:, ["low", f"close_{drift}"]].min(axis=1)
        del tdf

        bp = close - min_l_or_pc
        tr = max_h_or_pc - min_l_or_pc

        fast_avg = bp.rolling(fast).sum() / tr.rolling(fast).sum()
        medium_avg = bp.rolling(medium).sum() / tr.rolling(medium).sum()
        slow_avg = bp.rolling(slow).sum() / tr.rolling(slow).sum()

        total_weight = fast_w + medium_w + slow_w
        weights = (fast_w * fast_avg) + (medium_w * medium_avg) \
            + (slow_w * slow_avg)
        uo = 100 * weights / total_weight

    # Offset
    if offset != 0:
        uo = uo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        uo.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    uo.name = f"UO_{fast}_{medium}_{slow}"
    uo.category = "momentum"

    return uo

import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class UO(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()  
    sig_add_historic = Signal()  
    def __init__(self,parent,_candles,fast_period,medium_period,slow_period,fast_w_value,medium_w_value,slow_w_value) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.fast_period :int=fast_period
        self.medium_period :int=medium_period
        self.slow_period :int=slow_period
        self.fast_w_value :float=fast_w_value
        self.medium_w_value :float=medium_w_value
        self.slow_w_value :float=slow_w_value
        
        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"UO {self.fast_period} {self.medium_period} {self.slow_period} {self.fast_w_value} {self.medium_w_value} {self.slow_w_value}"

        self.df = pd.DataFrame([])
        
        self.xdata,self.data = np.array([]),np.array([])

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
        self._candles.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.QueuedConnection)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE|PD_MAType):
        is_update = False
        print(_input,_source)
        
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "fast_w_value":
            self.fast_w_value = _source
            is_update = True
        elif _input == "slow_w_value":
            self.slow_w_value = _source
            is_update = True
        elif _input == "medium_w_value":
            self.medium_w_value = _source
            is_update = True
        elif _input == "fast_period":
            self.fast_period = _source
            is_update = True
        elif _input == "slow_period":
            self.slow_period = _source
            is_update = True
        elif _input == "medium_period":
            self.medium_period = _source
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
        return self.xdata,self.data 
    
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
    
    def add_historic_worker(self,n):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add_historic,n)
        self.worker_.start()
    
    def started_worker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        if isinstance(INDICATOR,pd.Series):
            data = INDICATOR.dropna()
        else:
            column_names = INDICATOR.columns.tolist()
            uo_name = ''
            for name in column_names:
                if name.__contains__("UO_"):
                    uo_name = name
            data = INDICATOR[uo_name].dropna()
        return data
    
    def caculate(self,df: pd.DataFrame):
        INDICATOR = uo(high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    fast=self.fast_period,
                    medium=self.medium_period,
                    slow=self.slow_period,
                    fast_w=self.fast_w_value,
                    medium_w=self.medium_w_value,
                    slow_w=self.slow_w_value).dropna()
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        data = self.caculate(df)
        
        _len = len(data)
        _index = df["index"].tail(_len)
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        self.xdata,self.data = self.df["index"].to_numpy(),self.df["data"].to_numpy()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        data = self.caculate(df)
        
        _len = len(data)
        _index = df["index"].tail(_len)
        
        _df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        self.df = pd.concat([_df,self.df],ignore_index=True)
        self.xdata,self.data = self.df["index"].to_numpy(),self.df["data"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
                    
            data = self.caculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "data":[data.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.data  = self.df["index"].to_numpy(),self.df["data"].to_numpy()
                                            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
            data = self.caculate(df)
            self.df.iloc[-1] = [new_candle.index,data.iloc[-1]]
            self.xdata,self.data  = self.df["index"].to_numpy(),self.df["data"].to_numpy()
            self.sig_update_candle.emit()
