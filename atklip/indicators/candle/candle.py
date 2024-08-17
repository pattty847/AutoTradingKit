from functools import lru_cache
from typing import Dict, List,Tuple
from dataclasses import dataclass
from atklip.indicators import OHLCV
import pandas as pd
import numpy as np,array

from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication

#@dataclass
class JAPAN_CANDLE(QObject):
    """
    lastcandle: chính là lastcandle signal của chartview, hiện tại chưa dùng"
    """
    candles: List[OHLCV] = []
    dict_index_ohlcv: Dict[int, OHLCV] = {}
    dict_time_ohlcv: Dict[int, OHLCV] = {}
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_reset_all = Signal()
    signal_delete = Signal()
    sig_update_source = Signal()
    def __init__(self) -> None:
        super().__init__(parent=None)
        self.first_gen = False
        self._source_name = "JAPAN_CANDLE"
        self.signal_delete.connect(self.deleteLater)
        self.df = pd.DataFrame([])

    @property
    def source_name(self):
        return self._source_name
    @source_name.setter
    def source_name(self,_name):
        self._source_name = _name
    
    def get_df(self):
        return self.df
    
    def get_last_row_df(self):
        return self.df.iloc[-1]

    #@lru_cache(maxsize=128)
    def get_times(self,start:int=0,stop:int=0) -> List[int]:
        if start == 0 and stop == 0:
            return [candle.time for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.time for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.time for candle in self.candles[start:]]
        else:
            return [candle.time for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_indexs(self,start:int=0,stop:int=0) -> List[int]:
        if start == 0 and stop == 0:
            return [candle.index for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.index for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.index for candle in self.candles[start:]]
        else:
            return [candle.index for candle in self.candles[start:stop]]
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
    def get_candles(self,n:int=0) -> List[OHLCV]:
        if n == 0:
            return self.candles
        else:
            return self.candles[n:]
    #@lru_cache(maxsize=128)
    def get_n_first_candles(self,n:int=0) -> List[OHLCV]:
        if n == 0:
            return self.candles
        else:
            return self.candles[:n]
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
    def get_list_index_data(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_values(start,stop)
        return all_index,all_data

    def last_data(self)->OHLCV:
        if self.candles != []:
            return self.candles[-1]
        else:
            return []
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

    def gen_data(self,ohlcv,_precision):
        self.first_gen = False
        self.candles = []
        [self.gen_update(OHLCV(ohlcv[i][1],ohlcv[i][2],ohlcv[i][3],ohlcv[i][4],round((ohlcv[i][2]+ohlcv[i][3])/2,_precision), round((ohlcv[i][2]+ohlcv[i][3]+ohlcv[i][4])/3,_precision), round((ohlcv[i][1]+ohlcv[i][2]+ohlcv[i][3]+ohlcv[i][4])/4,_precision),ohlcv[i][5],ohlcv[i][0]/1000,i)) for i in range(len(ohlcv))]
        self.first_gen = True
        self.df = pd.DataFrame([data.__dict__ for data in self.candles])
        self.sig_reset_all.emit()
        #QCoreApplication.processEvents()
        return self.candles

    def gen_update(self,new_candle:OHLCV):
        if len(self.candles) == 0:
            "lấy mốc thời gian 2018 thời điểm data bắt đầu"
            new_candle.index = 1514754000
            self.candles.append(new_candle)
            self.dict_index_ohlcv[new_candle.index] = new_candle
            self.dict_time_ohlcv[new_candle.time] = new_candle
        _time = self.candles[-1].time
        if _time == new_candle.time:
            self.candles[-1].open = new_candle.open
            self.candles[-1].high = new_candle.high
            self.candles[-1].low = new_candle.low
            self.candles[-1].close = new_candle.close
            
            self.candles[-1].hl2 = new_candle.hl2
            self.candles[-1].hlc3 = new_candle.hlc3
            self.candles[-1].ohlc4 = new_candle.ohlc4
            
            self.candles[-1].volume = new_candle.volume
            self.candles[-1].time = new_candle.time
            
            self.dict_index_ohlcv[new_candle.index] = new_candle
            self.dict_time_ohlcv[new_candle.time] = new_candle
 
        else:
            _index = self.candles[-1].index + 1
            _new_candle = OHLCV(new_candle.open,new_candle.high,new_candle.low,new_candle.close,new_candle.hl2,new_candle.hlc3,new_candle.ohlc4,new_candle.volume,new_candle.time,_index)
            self.candles.append(_new_candle)
            self.dict_index_ohlcv[_new_candle.index] = _new_candle
            self.dict_time_ohlcv[_new_candle.time] = _new_candle


    def update(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if self.first_gen:
            if len(self.candles) == 0:
                "lấy mốc thời gian 2018 thời điểm data bắt đầu"
                new_candle.index = 1514754000
                self.candles.append(new_candle)
                self.dict_index_ohlcv[new_candle.index] = new_candle
                self.dict_time_ohlcv[new_candle.time] = new_candle
                return False
            _time = self.candles[-1].time
            if _time == new_candle.time:
                if new_candle.close != self.candles[-1].close or\
                new_candle.high != self.candles[-1].high or\
                new_candle.low != self.candles[-1].low or\
                new_candle.open != self.candles[-1].open:
                    self.candles[-1].open = new_candle.open
                    self.candles[-1].high = new_candle.high
                    self.candles[-1].low = new_candle.low
                    self.candles[-1].close = new_candle.close
                    
                    self.candles[-1].hl2 = new_candle.hl2
                    self.candles[-1].hlc3 = new_candle.hlc3
                    self.candles[-1].ohlc4 = new_candle.ohlc4
                    
                    self.candles[-1].volume = new_candle.volume
                    self.candles[-1].time = new_candle.time
                    self.dict_index_ohlcv[self.candles[-1].index] = self.candles[-1]
                    self.dict_time_ohlcv[self.candles[-1].time] = self.candles[-1]
                    
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

                    self.sig_update_candle.emit(self.candles[-2:])
                    #QCoreApplication.processEvents()
            else:
                pre_candle:OHLCV = new_candles[-2]
                
                self.candles[-1].open = pre_candle.open
                self.candles[-1].high = pre_candle.high
                self.candles[-1].low = pre_candle.low
                self.candles[-1].close = pre_candle.close
                
                self.candles[-1].hl2 = pre_candle.hl2
                self.candles[-1].hlc3 = pre_candle.hlc3
                self.candles[-1].ohlc4 = pre_candle.ohlc4
                
                self.candles[-1].volume = pre_candle.volume
                self.candles[-1].time = pre_candle.time
                _index = self.candles[-1].index + 1
                _new_candle = OHLCV(new_candle.open,new_candle.high,new_candle.low,new_candle.close,new_candle.hl2,new_candle.hlc3,new_candle.ohlc4,new_candle.volume,new_candle.time,_index)
                self.candles.append(_new_candle)
                self.dict_index_ohlcv[_new_candle.index] = _new_candle
                self.dict_time_ohlcv[_new_candle.time] = _new_candle
                
                new_row = pd.DataFrame([data.__dict__ for data in self.candles[-1:]])
                self.df = pd.concat([self.df, new_row], ignore_index=True)

                self.sig_add_candle.emit(self.candles[-2:])
                #QCoreApplication.processEvents()
                return True
            return False
        return False
            
