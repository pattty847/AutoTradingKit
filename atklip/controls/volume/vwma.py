# -*- coding: utf-8 -*-
from pandas import Series
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.overlap import sma
from atklip.controls.pandas_ta.utils import v_offset, v_pos_default, v_series



def vwma(
    close: Series, volume: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Volume Weighted Moving Average (VWMA)

    Volume Weighted Moving Average.

    Sources:
        https://www.motivewave.com/studies/volume_weighted_moving_average.htm

    Args:
        close (pd.Series): Series of 'close's
        volume (pd.Series): Series of 'volume's
        length (int): It's period. Default: 10
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)
    volume = v_series(volume, length)

    if close is None or volume is None:
        return

    offset = v_offset(offset)

    # Calculate
    pv = close * volume
    vwma = sma(close=pv, length=length) / sma(close=volume, length=length)

    # Offset
    if offset != 0:
        vwma = vwma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vwma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    vwma.name = f"VWMA_{length}"
    vwma.category = "overlap"

    return vwma


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool

from PySide6.QtCore import Signal,QObject

class VWMA(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()  
    sig_add_historic = Signal(int)   
    def __init__(self,_candles,dict_ta_params) -> None:   
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.source:str = dict_ta_params.get("source","close")   
        self.length:int = dict_ta_params.get("length",10)
        self.offset :int=dict_ta_params.get("offset",0)
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"VWMA {self.source} {self.length}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.data = np.array([]),np.array([])

        self.connect_signals()
    
    
    @property
    def source_name(self)-> str:
        return self._source_name
    @source_name.setter
    def source_name(self,source_name):
        self._source_name = source_name
    
    def change_input(self,candles=None,dict_ta_params: dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE= candles
            self.connect_signals()
        
        if dict_ta_params != {}:
            self.source:str = dict_ta_params.get("source","close")   
            self.length:int = dict_ta_params.get("length",10)
            self.offset :int=dict_ta_params.get("offset",0)

            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.length}"

            self.indicator_name = ta_param
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.fisrt_gen_data()
    
    def disconnect_signals(self):
        try:
            self._candles.sig_reset_all.disconnect(self.started_worker)
            self._candles.sig_update_candle.disconnect(self.update_worker)
            self._candles.sig_add_candle.disconnect(self.add_worker)
            self._candles.signal_delete.disconnect(self.signal_delete)
            self._candles.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self._candles.sig_reset_all.connect(self.started_worker)
        self._candles.sig_update_candle.connect(self.update_worker)
        self._candles.sig_add_candle.connect(self.add_worker)
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
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
    
    def get_data(self,start:int=0,stop:int=0):
        if len(self.xdata) == 0:
            return [],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            y_data = self.data
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            y_data = self.data[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            y_data = self.data[start:]
        else:
            x_data = self.xdata[start:stop]
            y_data = self.data[start:stop]
        return x_data,y_data
    
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    
    def update_worker(self,candle):
        self.worker.submit(self.update,candle)

    def add_worker(self,candle):
        self.worker.submit(self.add,candle)
    
    def add_historic_worker(self,n):
        self.worker.submit(self.add_historic,n)

    def started_worker(self):
        self.worker.submit(self.fisrt_gen_data)
    
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        
        if isinstance(INDICATOR,pd.Series):
            y_data = INDICATOR
        else:
            column_names = INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("VWMA_"):
                    roc_name = name
            y_data = INDICATOR[roc_name]
        return y_data
    def calculate(self,df: pd.DataFrame):
        INDICATOR = vwma(close=df[self.source],
                         volume=df["volume"],
                        length=self.length,
                        offset=self.offset).dropna().round(6)
        return self.paire_data(INDICATOR)
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        data = self.calculate(df)
        
        _len = len(data)
        _index = df["index"].tail(_len)

        self.df = pd.DataFrame({
                            'index':_index,
                            "data":data,
                            })
                
        self.xdata,self.data = self.df["index"].to_numpy(),self.df["data"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        self.is_current_update = True
        self.sig_reset_all.emit()
        
    def add_historic(self,n:int):
        self.is_histocric_load = False
        self.is_genering = True
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        data = self.calculate(df)
        
        _len = len(data)
        _index = df["index"].tail(_len)

        _df = pd.DataFrame({
                            'index':_index,
                            "data":data,
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        
        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata)) 
        self.data = np.concatenate((_df["data"].to_numpy(), self.data))   

        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
                    
            data = self.calculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "data":[data.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                            
            self.xdata = np.concatenate((self.xdata,np.array([new_candle.index])))
            self.data = np.concatenate((self.data,np.array([data.iloc[-1]])))
            
            self.sig_add_candle.emit()
        self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
                    
            data = self.calculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,data.iloc[-1]]
                    
            self.xdata[-1],self.data[-1] = new_candle.index,data.iloc[-1]
            self.sig_update_candle.emit()
        self.is_current_update = True
            
