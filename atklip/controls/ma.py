# -*- coding: utf-8 -*-
from pandas import Series
from atklip.controls.pandas_ta._typing import DictLike
from atklip.controls.overlap.dema import dema
from atklip.controls.overlap.ema import ema
from atklip.controls.overlap.fwma import fwma
from atklip.controls.overlap.hma import hma
from atklip.controls.overlap.linreg import linreg
from atklip.controls.overlap.midpoint import midpoint
from atklip.controls.overlap.pwma import pwma
from atklip.controls.overlap.rma import rma
from atklip.controls.overlap.sinwma import sinwma
from atklip.controls.overlap.sma import sma
from atklip.controls.overlap.ssf import ssf
from atklip.controls.overlap.swma import swma
from atklip.controls.overlap.t3 import t3
from atklip.controls.overlap.tema import tema
from atklip.controls.overlap.trima import trima
from atklip.controls.overlap.vidya import vidya
from atklip.controls.overlap.wma import wma



def ma(name: str = None, source: Series = None, **kwargs: DictLike) -> Series:
    """Simple MA Utility for easier MA selection

    Available MAs:
        dema, ema, fwma, hma, linreg, midpoint, pwma, rma, sinwma, sma, ssf,
        swma, t3, tema, trima, vidya, wma

    Examples:
        ema8 = ta.ma("ema", df.close, length=8)
        sma50 = ta.ma("sma", df.close, length=50)
        pwma10 = ta.ma("pwma", df.close, length=10, asc=False)

    Args:
        name (str): One of the Available MAs. Default: "ema"
        source (pd.Series): The 'source' Series.

    Kwargs:
        Any additional kwargs the MA may require.

    Returns:
        pd.Series: New feature generated.
    """
    _mas = [
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma",
        "sinwma", "sma", "ssf", "swma", "t3", "tema", "trima", "vidya", "wma"
    ]
    if name is None and source is None:
        return _mas
    elif isinstance(name, str) and name.lower() in _mas:
        name = name.lower()
    else:  # "ema"
        name = _mas[1]

    if   name == "dema": return dema(source, **kwargs)
    elif name == "fwma": return fwma(source, **kwargs)
    elif name == "hma": return hma(source, **kwargs)
    elif name == "linreg": return linreg(source, **kwargs)
    elif name == "midpoint": return midpoint(source, **kwargs)
    elif name == "pwma": return pwma(source, **kwargs)
    elif name == "rma": return rma(source, **kwargs)
    elif name == "sinwma": return sinwma(source, **kwargs)
    elif name == "sma": return sma(source, **kwargs)
    elif name == "ssf": return ssf(source, **kwargs)
    elif name == "swma": return swma(source, **kwargs)
    elif name == "t3": return t3(source, **kwargs)
    elif name == "tema": return tema(source, **kwargs)
    elif name == "trima": return trima(source, **kwargs)
    elif name == "vidya": return vidya(source, **kwargs)
    elif name == "wma": return wma(source, **kwargs)
    else: return ema(source, **kwargs)


import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from .ma_type import PD_MAType
from .ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class MA(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    def __init__(self,parent,_candles,source,ma_type,length) -> None:
        super().__init__(parent=parent)
        self.ma_type:PD_MAType = ma_type
        self.source:str = source
        self.length:int= length
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"{self.ma_type.name.lower()} {self.source} {self.length}"

        self.df = pd.DataFrame([])
        
        self.xdata = np.array([])
        self.ydata = np.array([])

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
        return self.xdata,self.ydata
    
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
        
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        data = ma(self.ma_type.name.lower(),source=df[self.source],length=self.length)
        data = data.astype('float32')
        
        _index = df["index"]
            
        self.df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        
        self.xdata,self.ydata = _index.to_numpy(),data.to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                        
            data = ma(self.ma_type.name.lower(),source=df[self.source],length=self.length)
            data = data.astype('float32')
            
            _data = data.iloc[-1]
            
            new_frame = pd.DataFrame({
                                'index':[new_candle.index],
                                "data":[_data]
                                })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.ydata = self.xdata,self.ydata = self.df["index"].to_numpy(),self.df["data"].to_numpy()
            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                        
            data = ma(self.ma_type.name.lower(),source=df[self.source],length=self.length)
            data = data.astype('float32')
            
            self.df.iloc[-1] = [new_candle.index,data.iloc[-1]]
            
            self.xdata,self.ydata = self.df["index"].to_numpy(),self.df["data"].to_numpy()
            
            self.sig_update_candle.emit()
            
            