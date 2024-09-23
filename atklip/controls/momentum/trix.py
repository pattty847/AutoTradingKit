# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.overlap.ema import ema
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series
)



def trix(
    close: Series, length: Int = None, signal: Int = None,mamode: str = "ema",
    scalar: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Trix (TRIX)

    TRIX is a momentum oscillator to identify divergences.

    Sources:
        https://www.tradingview.com/wiki/TRIX

    Args:
        close (pd.Series): Series of 'close's
        length (int): It's period. Default: 18
        signal (int): It's period. Default: 9
        scalar (float): How much to magnify. Default: 100
        drift (int): The difference period. Default: 1
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 30)
    signal = v_pos_default(signal, 9)
    if length < signal:
        length, signal = signal, length
    _length = 3 * length - 1
    close = v_series(close, _length)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    
    # ema1 = ema(close=close, length=length, **kwargs)
    ema1 = ma(mamode, source=close, length=length, **kwargs)
    if all(isnan(ema1)):
        return  # Emergency Break

    # ema2 = ema(close=ema1, length=length, **kwargs)
    ema2 = ma(mamode, source=ema1, length=length, **kwargs)
    if all(isnan(ema2)):
        return  # Emergency Break

    # ema3 = ema(close=ema2, length=length, **kwargs)
    ema3 = ma(mamode, source=ema2, length=length, **kwargs)
    if all(isnan(ema3)):
        return  # Emergency Break

    trix = scalar * ema3.pct_change(drift)
    trix_signal = trix.rolling(signal).mean()

    # Offset
    if offset != 0:
        trix = trix.shift(offset)
        trix_signal = trix_signal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        trix.fillna(kwargs["fillna"], inplace=True)
        trix_signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    trix.name = f"TRIX_{length}_{signal}"
    trix_signal.name = f"TRIXs_{length}_{signal}"
    trix.category = trix_signal.category = "momentum"

    data = {trix.name: trix, trix_signal.name: trix_signal}
    df = DataFrame(data, index=close.index)
    df.name = f"TRIX_{length}_{signal}"
    df.category = "momentum"

    return df


import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class TRIX(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()  
    sig_add_historic = Signal()    
    def __init__(self,parent,_candles,source,length_period,signal_period,ma_type) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.length_period :int = length_period
        self.signal_period:int = signal_period
        self.source:str = source
        self.ma_type:PD_MAType = ma_type

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"TRIX {self.source} {self.length_period} {self.signal_period} {self.ma_type.name.lower()}"

        self.df = pd.DataFrame([])
        
        self.xdata,self.trix_ , self.signalma = np.array([]),np.array([]),np.array([])

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
        elif _input == "signal_period":
            self.signal_period = _source
            is_update = True
        elif _input == "length_period":
            self.length_period = _source
            is_update = True
        elif _input == "d_period":
            self.d_period = _source
            is_update = True
        elif _input == "k_period":
            self.k_period = _source
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
        return self.xdata,self.trix_ , self.signalma
    
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
        column_names = INDICATOR.columns.tolist()
        
        trix_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("TRIX_"):
                trix_name = name
            elif name.__contains__("TRIXs_"):
                signalma_name = name

        trix_ = INDICATOR[trix_name].dropna()
        signalma = INDICATOR[signalma_name].dropna()
        
        return trix_,signalma
    
    def caculate(self,df: pd.DataFrame):
        INDICATOR = trix(close=df[self.source],
                            length=self.length_period,
                            signal = self.signal_period,
                            mamode=self.ma_type.name.lower()
                            ).dropna()
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        trix_, signalma = self.caculate(df)
        
        _len = min([len(trix_),len(signalma)])
        _index = df["index"].tail(_len)

        self.df = pd.DataFrame({
                            'index':_index,
                            "trix":trix_.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
                
        self.xdata,self.trix_ , self.signalma = self.df["index"].to_numpy(),\
                                                self.df["trix"].to_numpy(),\
                                                self.df["signalma"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        trix_, signalma = self.caculate(df)
        
        _len = min([len(trix_),len(signalma)])
        _index = df["index"].tail(_len)

        _df = pd.DataFrame({
                            'index':_index,
                            "trix":trix_.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
        self.df = pd.concat([_df,self.df],ignore_index=True)
        self.xdata,self.trix_ , self.signalma = self.df["index"].to_numpy(),\
                                                self.df["trix"].to_numpy(),\
                                                self.df["signalma"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length_period*5)
                    
            trix_, signalma = self.caculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "trix":[trix_.iloc[-1]],
                                    "signalma":[signalma.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.trix_ , self.signalma  = self.df["index"].to_numpy(),\
                                                    self.df["trix"].to_numpy(),\
                                                    self.df["signalma"].to_numpy()
                                            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length_period*5)
                    
            trix_, signalma = self.caculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,trix_.iloc[-1],signalma.iloc[-1]]
                    
            self.xdata,self.trix_ , self.signalma  = self.df["index"].to_numpy(),\
                                                    self.df["trix"].to_numpy(),\
                                                    self.df["signalma"].to_numpy()
            self.sig_update_candle.emit()

