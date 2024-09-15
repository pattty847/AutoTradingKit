# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    non_zero_range,
    tal_ma,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def stoch(
    high: Series, low: Series, close: Series,
    k: Int = None, d: Int = None, smooth_k: Int = None,
    mamode: str = None, talib: bool = True,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Stochastic (STOCH)

    The Stochastic Oscillator (STOCH) was developed by George Lane in the
    1950's. He believed this indicator was a good way to measure momentum
    because changes in momentum precede changes in price.

    It is a range-bound oscillator with two lines moving between 0 and 100.
    The first line (%K) displays the current close in relation to the
    period's high/low range. The second line (%D) is a Simple Moving Average
    of the %K line. The most common choices are a 14 period %K and a 3 period
    SMA for %D.

    Sources:
        https://www.tradingview.com/wiki/Stochastic_(STOCH)
        https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=332&Name=KD_-_Slow

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        k (int): The Fast %K period. Default: 14
        d (int): The Slow %D period. Default: 3
        smooth_k (int): The Slow %K period. Default: 3
        mamode (str): See ``help(ta.ma)``. Default: 'sma'
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: %K, %D, Histogram columns.
    """
    # Validate
    k = v_pos_default(k, 14)
    d = v_pos_default(d, 3)
    smooth_k = v_pos_default(smooth_k, 3)
    _length = k + d + smooth_k
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    mamode = v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal and smooth_k > 2:
        from atklip.controls.talib import STOCH
        stoch_ = STOCH(
            high, low, close, k, d, tal_ma(mamode), d, tal_ma(mamode)
        )
        stoch_k, stoch_d = stoch_[0], stoch_[1]
    else:
        ll = low.rolling(k).min()
        hh = high.rolling(k).max()

        stoch = 100 * (close - ll) / non_zero_range(hh, ll)

        if stoch is None: return

        stoch_fvi = stoch.loc[stoch.first_valid_index():, ]
        if smooth_k == 1:
            stoch_k = stoch
        else:
            stoch_k = ma(mamode, stoch_fvi, length=smooth_k)

        stochk_fvi = stoch_k.loc[stoch_k.first_valid_index():, ]
        stoch_d = ma(mamode, stochk_fvi, length=d)

    stoch_h = stoch_k - stoch_d  # Histogram

    # Offset
    if offset != 0:
        stoch_k = stoch_k.shift(offset)
        stoch_d = stoch_d.shift(offset)
        stoch_h = stoch_h.shift(offset)

    # Fill
    if "fillna" in kwargs:
        stoch_k.fillna(kwargs["fillna"], inplace=True)
        stoch_d.fillna(kwargs["fillna"], inplace=True)
        stoch_h.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _name = "STOCH"
    _props = f"_{k}_{d}_{smooth_k}"
    stoch_k.name = f"{_name}k{_props}"
    stoch_d.name = f"{_name}d{_props}"
    stoch_h.name = f"{_name}h{_props}"
    stoch_k.category = stoch_d.category = stoch_h.category = "momentum"

    data = {
        stoch_k.name: stoch_k,
        stoch_d.name: stoch_d,
        stoch_h.name: stoch_h
    }
    df = DataFrame(data, index=close.index)
    df.name = f"{_name}{_props}"
    df.category = stoch_k.category

    return df

import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class STOCH(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    def __init__(self,parent,_candles,smooth_k_period,k_period,d_period,ma_type) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
                 
        self.smooth_k_period:int = smooth_k_period
        self.k_period:int = k_period
        self.d_period:int = d_period
    
        self.ma_type:PD_MAType = ma_type

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"STOCH {self.smooth_k_period} {self.k_period} {self.d_period} {self.ma_type.name.lower()}"

        self.df = pd.DataFrame([])
        
        self.xdata,self.stoch_,self.signalma = np.array([]),np.array([]),np.array([])

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
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE|PD_MAType):
        is_update = False
        print(_input,_source)
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "smooth_k_period":
            self.smooth_k_period = _source
            is_update = True
        elif _input == "k_period":
            self.k_period = _source
            is_update = True
        elif _input == "d_period":
            self.d_period = _source
            is_update = True
        elif _input == "type":
            self.source = _source
            is_update = True
        elif _input == "ma_type":
            self.ma_type = _source
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
        return self.xdata,self.stoch_,self.signalma
    
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
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        column_names = INDICATOR.columns.tolist()
        stoch_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("STOCHk"):
                stoch_name = name
            elif name.__contains__("STOCHd"):
                signalma_name = name

        stoch_ = INDICATOR[stoch_name]
        signalma = INDICATOR[signalma_name]
        return stoch_,signalma
    
    def caculate(self,df: pd.DataFrame):
        INDICATOR = stoch(high=df["high"],
                        low=df["low"],
                        close=df["close"],
                        smooth_k=self.smooth_k_period,
                        k = self.k_period,
                        d = self.d_period,
                        mamode=self.ma_type.name.lower())
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        stoch_, signalma = self.caculate(df)
        
        _index = df["index"]

        self.df = pd.DataFrame({
                            'index':_index,
                            "stoch":stoch_,
                            "signalma":signalma
                            })
                
        self.xdata,self.stoch_,self.signalma = self.df["index"].to_numpy(),\
                                                stoch_.to_numpy(),\
                                                signalma.to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.k_period*5)
                    
            stoch_, signalma = self.caculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "stoch":[stoch_.iloc[-1]],
                                    "signalma":[signalma.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.stoch_,self.signalma  = self.df["index"].to_numpy(),\
                                                    self.df["stoch"].to_numpy(),\
                                                    self.df["signalma"].to_numpy()
                                            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.k_period*5)
                    
            stoch_, signalma = self.caculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,stoch_.iloc[-1],signalma.iloc[-1]]
                    
            self.xdata,self.stoch_,self.signalma  = self.df["index"].to_numpy(),\
                                                    self.df["stoch"].to_numpy(),\
                                                    self.df["signalma"].to_numpy()
            self.sig_update_candle.emit()
