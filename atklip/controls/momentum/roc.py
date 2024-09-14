# -*- coding: utf-8 -*-
from numba import njit
from pandas import Series
from atklip.controls.pandas_ta._typing import Array, DictLike, Int, IntFloat
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    nb_idiff,
    nb_shift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib
)
from .mom import mom



@njit(cache=True)
def nb_roc(x, n, k):
    return k * nb_idiff(x, n) / nb_shift(x, n)


def roc(
    close: Series, length: Int = None,
    scalar: IntFloat = None, talib: bool = True,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rate of Change (ROC)

    Rate of Change is an indicator is also referred to as Momentum
    (yeah, confusingly). It is a pure momentum oscillator that measures the
    percent change in price with the previous price 'n' (or length)
    periods ago.

    Sources:
        https://www.tradingview.com/wiki/Rate_of_Change_(ROC)

    Args:
        close (pd.Series): Series of 'close's
        length (int): Its period. Default: 10
        scalar (float): How much to magnify. Default: 100
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length + 1)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from atklip.controls.talib import ROC
        roc = ROC(close, length)
    else:
        # roc = scalar * mom(close=close, length=length, talib=mode_tal) \
            # / close.shift(length)
        np_close = close.values
        _roc = nb_roc(np_close, length, scalar)
        roc = Series(_roc, index=close.index)

    # Offset
    if offset != 0:
        roc = roc.shift(offset)

    # Fill
    if "fillna" in kwargs:
        roc.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    roc.name = f"ROC_{length}"
    roc.category = "momentum"

    return roc


import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class ROC(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    def __init__(self,parent,_candles,source,length) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.source:str = source      
        self.length:int = length

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"ROC {self.source} {self.length}"

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
        elif _input == "period":
            self.length = _source
            is_update = True
        elif _input == "type":
            self.source = _source
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
    
    def started_worker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        
        if isinstance(INDICATOR,pd.Series):
            y_data = INDICATOR
        else:
            column_names = INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("ROC"):
                    roc_name = name
            y_data = INDICATOR[roc_name]
        return y_data
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        INDICATOR = roc(close=df[self.source],length=self.length)
        
        _index = df["index"]
        data = self.paire_data(INDICATOR)

        self.df = pd.DataFrame({
                            'index':_index,
                            "data":data,
                            })
                
        self.xdata,self.data = self.df["index"].to_numpy(),data.to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
                    
            INDICATOR = roc(close=df[self.source],length=self.length)
            
            data = self.paire_data(INDICATOR)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "data":[data.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                
            self.xdata,self.data = self.df["index"].to_numpy(),self.df["data"].to_numpy()
            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
                    
            INDICATOR = roc(close=df[self.source],length=self.length)
            
            data = self.paire_data(INDICATOR)
                    
            self.df.iloc[-1] = [new_candle.index,data.iloc[-1]]
                    
            self.xdata,self.data = self.df["index"].to_numpy(),self.df["data"].to_numpy()
            
            self.sig_update_candle.emit()
            
