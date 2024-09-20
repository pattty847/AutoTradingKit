# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.statistics import stdev
from atklip.controls.pandas_ta.utils import (
    non_zero_range,
    tal_ma,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def bbands(
    close: Series, length: Int = None, std: IntFloat = None, ddof: Int = 0,
    mamode: str = None, talib: bool = True,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Bollinger Bands (BBANDS)

    A popular volatility indicator by John Bollinger.

    Sources:
        https://www.tradingview.com/wiki/Bollinger_Bands_(BB)

    Args:
        close (pd.Series): Series of 'close's
        length (int): The short length. Default: 5
        std (int): The long length. Default: 2
        ddof (int): Degrees of Freedom to use. Default: 0
        mamode (str): See ``help(ta.ma)``. Default: 'sma'
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        ddof (int): Delta Degrees of Freedom.
                    The divisor used in calculations is N - ddof, where N
                    represents the number of elements. The 'talib' argument
                    must be false for 'ddof' to work. Default: 1
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: lower, mid, upper, bandwidth, and percent columns.
    """
    # Validate
    length = v_pos_default(length, 5)
    close = v_series(close, length)

    if close is None:
        return

    std = v_pos_default(std, 2.0)
    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    mamode = v_mamode(mamode, "sma")
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from atklip.controls.talib import BBANDS
        upper, mid, lower = BBANDS(close, length, std, std, tal_ma(mamode))
    else:
        std_dev = stdev(close=close, length=length, ddof=ddof, talib=mode_tal)
        deviations = std * std_dev
        # deviations = std * standard_deviation.loc[standard_deviation.first_valid_index():,]

        mid = ma(mamode, close, length=length, talib=mode_tal, **kwargs)
        lower = mid - deviations
        upper = mid + deviations

    ulr = non_zero_range(upper, lower)
    bandwidth = 100 * ulr / mid
    percent = non_zero_range(close, lower) / ulr

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)
        bandwidth = bandwidth.shift(offset)
        percent = percent.shift(offset)

    # Fill
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
        bandwidth.fillna(kwargs["fillna"], inplace=True)
        percent.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}_{std}"
    lower.name = f"BBL{_props}"
    mid.name = f"BBM{_props}"
    upper.name = f"BBU{_props}"
    bandwidth.name = f"BBB{_props}"
    percent.name = f"BBP{_props}"
    upper.category = lower.category = "volatility"
    mid.category = bandwidth.category = upper.category

    data = {
        lower.name: lower,
        mid.name: mid,
        upper.name: upper,
        bandwidth.name: bandwidth,
        percent.name: percent
    }
    df = DataFrame(data, index=close.index)
    df.name = f"BBANDS{_props}"
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

class BBANDS(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal()    
    def __init__(self,parent,_candles,source,ma_type,length,std_dev_mult) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.ma_type:PD_MAType = ma_type
        self.source:str = source
        self.length:int = length
        self.std_dev_mult:float = std_dev_mult

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"{self.ma_type.name.lower()} {self.source} {self.length} {self.std_dev_mult}"

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
        self._candles.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.QueuedConnection)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE|PD_MAType):
        is_update = False
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "type":
            self.source = _source
            is_update = True
        elif _input == "ma_type":
            self.ma_type = _source
            is_update = True
        elif _input == "length":
            self.length = _source
            is_update = True
        elif _input == "std_dev_mult":
            self.std_dev_mult = _source
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


    def add_historic_worker(self,n):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add_historic,n)
        self.worker_.start()
    
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
        INDICATOR.astype('float32')
        column_names = INDICATOR.columns.tolist()
        
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

        lb = INDICATOR[lower_name].dropna()
        cb = INDICATOR[mid_name].dropna()
        ub = INDICATOR[upper_name].dropna()
        return lb,cb,ub
    def caculate(self,df: pd.DataFrame):
        INDICATOR = bbands(df[self.source],
                           length=self.length,
                           std=self.std_dev_mult,
                           mamode=self.ma_type.name.lower())
        return self.paire_data(INDICATOR)
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
                     
        lb,cb,ub = self.caculate(df)
        
        _len = min([len(lb),len(cb),len(ub)])
        _index = df["index"].tail(_len)
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "lb":lb.tail(_len),
                            "cb":cb.tail(_len),
                            "ub":ub.tail(_len)
                            })
                
        self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        lb,cb,ub = self.caculate(df)

        _len = min([len(lb),len(cb),len(ub)])
        _index = df["index"].tail(_len)
        
        _df = pd.DataFrame({
                            'index':_index,
                            "lb":lb.tail(_len),
                            "cb":cb.tail(_len),
                            "ub":ub.tail(_len)
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False 
        
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                    
            lb,cb,ub = self.caculate(df)
            
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
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                    
            lb,cb,ub = self.caculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,lb.iloc[-1],cb.iloc[-1],ub.iloc[-1]]
                    
            self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),\
                                                self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
            
            self.sig_update_candle.emit()
            
