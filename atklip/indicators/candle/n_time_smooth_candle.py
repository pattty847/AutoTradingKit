from functools import lru_cache
import numpy as np
import time
import pandas as pd
from typing import Any, Dict, List,Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication,QThreadPool

from atklip.indicators.talipp import OHLCV, INDICATOR, IndicatorType,MAType,Indicator

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
    
    dict_n_ma:Dict[str,Indicator] = {}
    
    dict_n_ohlcv:Dict[str,List[OHLCV]] = {}

    signal_delete = Signal()
    sig_update_source = Signal()
    def __init__(self,precision,_candles,n,ma_type,period) -> None:
        super().__init__(parent=None)
        self.ma_type:MAType = ma_type
        self.period:int= period
        self._candles:JAPAN_CANDLE|HEIKINASHI =_candles
        self.n:int = n
        
        if not isinstance(self._candles,JAPAN_CANDLE):
            self._candles.setParent(self)
            self.signal_delete.connect(self._candles.signal_delete)
            
        self.signal_delete.connect(self.deleteLater)
        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
        self._precision = precision
        self.first_gen = False
        self.is_genering = True
        self._source_name = f"{self.n}_SMOOTH_CANDLE"
        
        self.df = pd.DataFrame([])
        
        self._candles.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update,Qt.ConnectionType.AutoConnection)
        self._candles.sig_add_candle.connect(self.update,Qt.ConnectionType.AutoConnection)

    @property
    def source_name(self):
        return self._source_name
    @source_name.setter
    def source_name(self,_source_name):
        self._source_name = _source_name
        
    def get_df(self):
        return self.df
    
    def get_last_row_df(self):
        return self.df.iloc[-1]
    
    def threadpool_asyncworker(self,_candle):
        self.worker = None
        self.worker = CandleWorker(self.update,_candle)
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
            self.dict_n_ohlcv[f"{self.n}-candles"][-1]
    #@lru_cache(maxsize=128)
    def get_ma_ohlc_at_index(self,index:int,opens:Indicator,highs:Indicator,lows:Indicator,closes:Indicator,hl2s:Indicator,hlc3s:Indicator,ohlc4s:Indicator):
        #_index = opens.output_times.get(index)
        ohlc = [opens._dict_time_value.get(index),highs._dict_time_value.get(index),lows._dict_time_value.get(index),closes._dict_time_value.get(index),\
            hl2s._dict_time_value.get(index),hlc3s._dict_time_value.get(index),ohlc4s._dict_time_value.get(index)]
        return index, ohlc
    
    def update_ma_ohlc(self,lastcandle:OHLCV):
        _new_time = lastcandle.time
        _last_time = self.dict_n_ohlcv[f"{self.n}-candles"][-1].time
        _is_update = False
        self.dict_n_ohlcv[f"0-candles"] = self._candles.candles
        if _new_time == _last_time:
            _is_update =  True
        for i in range(self.n):
            _last_candle = self.dict_n_ohlcv[f"{i}-candles"][-1]
            if _is_update:
                self.dict_n_ma[f"{i+1}-highs"].update(_last_candle)
                self.dict_n_ma[f"{i+1}-lows"].update(_last_candle)
                self.dict_n_ma[f"{i+1}-closes"].update(_last_candle)
                self.dict_n_ma[f"{i+1}-opens"].update(_last_candle)
                self.dict_n_ma[f"{i+1}-hl2s"].update(_last_candle)
                self.dict_n_ma[f"{i+1}-hlc3s"].update(_last_candle)
                self.dict_n_ma[f"{i+1}-ohlc4s"].update(_last_candle)
            else:
                self.dict_n_ma[f"{i+1}-highs"].add(_last_candle)
                self.dict_n_ma[f"{i+1}-lows"].add(_last_candle)
                self.dict_n_ma[f"{i+1}-closes"].add(_last_candle)
                self.dict_n_ma[f"{i+1}-opens"].add(_last_candle)
                self.dict_n_ma[f"{i+1}-hl2s"].add(_last_candle)
                self.dict_n_ma[f"{i+1}-hlc3s"].add(_last_candle)
                self.dict_n_ma[f"{i+1}-ohlc4s"].add(_last_candle)
            
            _leng_candle = self.dict_n_ma[f"{i+1}-opens"].output_times[-1]
            
            self.compute(self.dict_n_ohlcv[f"{i+1}-candles"],_leng_candle,\
                                self.dict_n_ma[f"{i+1}-opens"],\
                                self.dict_n_ma[f"{i+1}-highs"],\
                                self.dict_n_ma[f"{i+1}-lows"],\
                                self.dict_n_ma[f"{i+1}-closes"],\
                                self.dict_n_ma[f"{i+1}-hl2s"],\
                                self.dict_n_ma[f"{i+1}-hlc3s"],\
                                self.dict_n_ma[f"{i+1}-ohlc4s"],_is_update)
        return _is_update
    
    def compute(self,candles: List[OHLCV],index:int,opens,highs,lows,closes,hl2s,hlc3s,ohlc4s,is_update: bool=False):
        _index, ohlc = self.get_ma_ohlc_at_index(index,opens,highs,lows,closes,hl2s,hlc3s,ohlc4s)
        _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6]
        if _open != None and  _high != None and _low != None and _close != None:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = \
                round(ohlc[0],self._precision),round(ohlc[1],self._precision),\
                round(ohlc[2],self._precision),round(ohlc[3],self._precision),\
                round(ohlc[4],self._precision),round(ohlc[5],self._precision),round(ohlc[6],self._precision)
            if is_update:
                candles[-1] = OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,self._candles.dict_index_ohlcv[_index].volume,self._candles.dict_index_ohlcv[_index].time,_index)
            else:
                candles.append(OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,self._candles.dict_index_ohlcv[_index].volume,self._candles.dict_index_ohlcv[_index].time,_index))
    def reset(self):
        self.dict_n_ohlcv[f"{self.n}-candles"] = []
    
    def _gen_data(self):
        self.dict_n_ohlcv[f"0-candles"] = self._candles.candles
        for i in range(self.n):
            self.dict_n_ma[f"{i+1}-highs"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="high")
            self.dict_n_ma[f"{i+1}-lows"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="low")
            self.dict_n_ma[f"{i+1}-closes"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="close")
            self.dict_n_ma[f"{i+1}-opens"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="open")
            self.dict_n_ma[f"{i+1}-hl2s"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="hl2")
            self.dict_n_ma[f"{i+1}-hlc3s"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="hlc3")
            self.dict_n_ma[f"{i+1}-ohlc4s"] = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self.dict_n_ohlcv[f"{i}-candles"],_type="ohlc4")
            
            self.dict_n_ohlcv[f"{i+1}-candles"] = []
            
            [self.compute(self.dict_n_ohlcv[f"{i+1}-candles"],index,\
                                    self.dict_n_ma[f"{i+1}-opens"],\
                                    self.dict_n_ma[f"{i+1}-highs"],\
                                    self.dict_n_ma[f"{i+1}-lows"],\
                                    self.dict_n_ma[f"{i+1}-closes"],\
                                    self.dict_n_ma[f"{i+1}-hl2s"],\
                                    self.dict_n_ma[f"{i+1}-hlc3s"],\
                                    self.dict_n_ma[f"{i+1}-ohlc4s"]) for index in self.dict_n_ma[f"{i+1}-highs"].output_times]
            

    def reset_data(self,n):
        self.n = n
        self.fisrt_gen_data()
     
    def fisrt_gen_data(self):
        self.is_genering = True
        self.dict_n_ohlcv[f"{self.n}-candles"] = []
        self.candles = self.dict_n_ohlcv[f"{self.n}-candles"]
        self._gen_data()
        self.candles = self.dict_n_ohlcv[f"{self.n}-candles"]
        
        self.df = pd.DataFrame([data.__dict__ for data in self.candles])
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()


    def update(self, _candle:List[OHLCV]):
        if (self.first_gen == True) and (self.is_genering == False):
            if self._candles.candles != []:
                new_candle = _candle[-1]
                is_update = self.update_ma_ohlc(new_candle)
                self.candles = self.dict_n_ohlcv[f"{self.n}-candles"]
                
                if is_update:
                    
                    self.df.iloc[-1] = [self.candles[-1].open,
                                        self.candles[-1].high,
                                        self.candles[-1].low,
                                        self.candles[-1].close,
                                        self.candles[-1].hl2,
                                        self.candles[-1].hlc3,
                                        self.candles[-1].ohlc4,
                                        self.candles[-1].volume,
                                        self.candles[-1].time,
                                        self.candles[-1].index
                                        ]
                    
                    self.sig_update_candle.emit(self.dict_n_ohlcv[f"{self.n}-candles"][-2:])
                    #QCoreApplication.processEvents()
                    return False
                else:
                    new_row = pd.DataFrame([data.__dict__ for data in self.candles[-1:]])
                    self.df = pd.concat([self.df, new_row], ignore_index=True)
                    self.sig_add_candle.emit(self.dict_n_ohlcv[f"{self.n}-candles"][-2:])
                    #QCoreApplication.processEvents()
                    return True
                
        return False
            