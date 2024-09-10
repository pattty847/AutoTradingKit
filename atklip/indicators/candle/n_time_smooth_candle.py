from functools import lru_cache
import numpy as np
import time
import pandas as pd
from typing import Any, Dict, List,Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication,QThreadPool

from atklip.indicators.ma_type import PD_MAType
from atklip.indicators.ohlcv import OHLCV

from .candle import JAPAN_CANDLE
from .heikinashi import HEIKINASHI
from .smooth_candle import SMOOTH_CANDLE

from atklip.appmanager import FastWorker,CandleWorker

class N_SMOOTH_CANDLE(QObject):
    """
    _candles: JAPAN_CANDLE|HEIKINASHI 
    lastcandle: signal(list)  - the list of 2 last candle of para "_candles: JAPAN_CANDLE|HEIKINASHI"
    ma_type: IndicatorType  - IndicatorType.SMA
    period: int - 20
    """
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_reset_all = Signal()
    candles : List[OHLCV] = []
    dict_index_time = {}
    dict_n_ma:Dict[str,pd.Series] = {}
    dict_n_ohlcv:Dict[str,JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE] = {}
    signal_delete = Signal()
    sig_update_source = Signal()
    
    def __init__(self,precision,_candles,n,ma_type,period) -> None:
        super().__init__(parent=None)
        self.ma_type:PD_MAType = ma_type
        self.period:int= period
        self._candles:JAPAN_CANDLE|HEIKINASHI =_candles
        self.n:int = n
        
        if not isinstance(self._candles,JAPAN_CANDLE) and not isinstance(self._candles,HEIKINASHI):
            self._candles.setParent(self)
            self.signal_delete.connect(self._candles.signal_delete)
            
        self.signal_delete.connect(self.delete_)
        
        self._precision = precision
        self.first_gen = False
        self.is_genering = True
        self._source_name = f"{self.n}_SMOOTH_CANDLE"
        
        self.df = pd.DataFrame([])
        
        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
        self._candles.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        
    def delete_smooth_candle(self):
        self.sig_update_candle = Signal(list)
        self.sig_add_candle = Signal(list)
        self.candles : List[OHLCV] = []
        self.df = pd.DataFrame([])
        if self.dict_n_ohlcv != {}:
            _list_smooth_candles = self.dict_n_ohlcv.items()
            for key,value in _list_smooth_candles:
                if not isinstance(value,JAPAN_CANDLE) and not isinstance(value,HEIKINASHI):
                    self.dict_n_ohlcv[key] = None
                    value.deleteLater()
        self.dict_n_ohlcv = {}

    def delete_(self):
        self.delete_smooth_candle()
        self.deleteLater()
    @property
    def source_name(self):
        return self._source_name
    @source_name.setter
    def source_name(self,_source_name):
        self._source_name = _source_name
        
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_last_row_df(self):
        return self.df.iloc[-1]
    
    def threadpool_asyncworker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
        
    def get_candles_as_dataframe(self, candles: List[OHLCV]=[]):
        if candles == []:
            candles = self.dict_n_ohlcv[f"{self.n}-candles"]
        df = pd.DataFrame([data.__dict__ for data in candles])
        # Đặt cột 'time' làm chỉ số (index) của DataFrame
        df.set_index('time', inplace=True)
        # Tùy chỉnh tên các cột
        new_column_names = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'hl2': 'HL2',
            'hlc3': 'HLC3',
            'ohlc4': 'OHLC4',
            'volume': 'Volume',
            'index': 'Index'
        }
        df.rename(columns=new_column_names, inplace=True)
        # Loại bỏ các cột 'hl2', 'hlc3', và 'ohlc4'
        df.drop(columns=['HL2', 'HLC3', 'OHLC4'], inplace=True)
        return df
    #@lru_cache(maxsize=128)
    def get_times(self,start:int=0,stop:int=0) -> List[str]:
        if start == 0 and stop == 0:
            return [candle.time for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.time for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.time for candle in self.candles[start:]]
        else:
            return [candle.time for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_values(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles]
        elif start == 0 and stop != 0:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles[start:]]
        else:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_indexs(self,start:int=0,stop:int=0) -> List[str]:
        if start == 0 and stop == 0:
            return [candle.index for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.index for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.index for candle in self.candles[start:]]
        else:
            return [candle.index for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_candles(self,n:int=0) -> List[OHLCV]:
        if n == 0:
            return self.dict_n_ohlcv[f"{self.n}-candles"]
        else:
            return self.dict_n_ohlcv[f"{self.n}-candles"][n:]
    #@lru_cache(maxsize=128)
    def get_n_first_candles(self,n:int=0) -> List[OHLCV]:
        if n == 0:
            return self.dict_n_ohlcv[f"{self.n}-candles"]
        else:
            return self.dict_n_ohlcv[f"{self.n}-candles"][:n]
        
    def getspecialvalues(self,_type):
        if _type == 'open':
            return [candle.index for candle in self.candles], [candle.open for candle in self.candles]
        elif _type == 'high':
            return [candle.index for candle in self.candles], [candle.high for candle in self.candles]
        elif _type == 'low':
            return [candle.index for candle in self.candles], [candle.low for candle in self.candles]
        elif _type == 'close':
            return [candle.index for candle in self.candles], [candle.close for candle in self.candles]
        elif _type == 'volume':
            return [candle.index for candle in self.candles], [candle.volume for candle in self.candles]
        elif _type == 'hl2':
            return [candle.index for candle in self.candles], [candle.hl2 for candle in self.candles]
        elif _type == 'hlc3':
            return [candle.index for candle in self.candles], [candle.hlc3 for candle in self.candles]
        elif _type == 'ohlc4':
            return [candle.index for candle in self.candles], [candle.ohlc4 for candle in self.candles]
        else:
            return [], []
    
    #@lru_cache(maxsize=128)
    def get_data(self,start:int=0,stop:int=0):
        all_time = self.get_times(start,stop)
        all_data = self.get_values(start,stop)
        all_time_np = np.array(all_time)
        all_data_np = np.array(all_data)
        return all_time_np,all_data_np
    
    #@lru_cache(maxsize=128)
    def get_volumes(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles]
        elif start == 0 and stop != 0:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles[start:]]
        else:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_ohlc4(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles]
        elif start == 0 and stop != 0:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles[start:]]
        else:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_hlc3(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles]
        elif start == 0 and stop != 0:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles[start:]]
        else:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_hl2(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [sum([candle.high, candle.low])/2 for candle in self.candles]
        elif start == 0 and stop != 0:
            return [sum([candle.high, candle.low])/2 for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [sum([candle.high, candle.low])/2 for candle in self.candles[start:]]
        else:
            return [sum([candle.high, candle.low])/2 for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_index_hl2(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_hl2(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    #@lru_cache(maxsize=128)
    def get_index_hlc3(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_hlc3(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    #@lru_cache(maxsize=128)
    def get_index_ohlc4(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_ohlc4(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    
    #@lru_cache(maxsize=128)
    def get_index_data(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_values(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    #@lru_cache(maxsize=128)
    def get_index_volumes(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_volumes(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    #@lru_cache(maxsize=128)
    def last_data(self)->OHLCV:
        if self.candles != []:
            return self.candles[-1]
        else:
            self.dict_n_ohlcv[f"{self.n}-candles"].candles[-1]

    def _gen_data(self):
        self.dict_n_ohlcv[f"0-candles"] = self._candles
        for i in range(self.n):
            self.dict_n_ohlcv[f"{i+1}-candles"] = SMOOTH_CANDLE(self._precision,self.dict_n_ohlcv[f"{i}-candles"],self.ma_type,self.period)
            self.dict_n_ohlcv[f"{i+1}-candles"].fisrt_gen_data()

    def fisrt_gen_data(self):
        self.delete_smooth_candle()
        self._gen_data()
        self.sig_update_candle = self.dict_n_ohlcv[f"{self.n}-candles"].sig_update_candle
        self.sig_add_candle = self.dict_n_ohlcv[f"{self.n}-candles"].sig_add_candle
        # self.sig_reset_all = self.dict_n_ohlcv[f"{self.n}-candles"].sig_reset_all
        self.candles = self.dict_n_ohlcv[f"{self.n}-candles"].candles
        self.df = self.dict_n_ohlcv[f"{self.n}-candles"].df
        self.sig_reset_all.emit()
         
