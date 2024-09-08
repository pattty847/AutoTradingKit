from functools import lru_cache
import numpy as np
import time
import pandas as pd
from typing import List,Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication,QThreadPool

from atklip.indicators.talipp import OHLCV, INDICATOR, IndicatorType,MAType
from .candle import JAPAN_CANDLE
from .heikinashi import HEIKINASHI
from atklip.appmanager import FastWorker,CandleWorker

class SMOOTH_CANDLE(QObject):
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
    signal_delete = Signal()
    sig_update_source = Signal()
    def __init__(self,precision,_candles: JAPAN_CANDLE|HEIKINASHI,ma_type,period) -> None:
        super().__init__(parent=None)
        self.ma_type:MAType = ma_type
        self.period:int= period
        self._candles =_candles
        
        if not isinstance(self._candles,JAPAN_CANDLE):
            self._candles.setParent(self)
            self.signal_delete.connect(self._candles.signal_delete)
        self.signal_delete.connect(self.deleteLater)
        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
        self._precision = precision
        self.first_gen = False
        self.is_genering = True
        self._source_name = "SMOOTH_CANDLE"
        self.threadpool = QThreadPool(self)
        self.df = pd.DataFrame([])
        self.threadpool.setMaxThreadCount(1)
        self._candles.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update,Qt.ConnectionType.AutoConnection)
        self._candles.sig_add_candle.connect(self.update,Qt.ConnectionType.AutoConnection)

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

    def threadpool_asyncworker(self,_candle):
        self.worker = None
        self.worker = CandleWorker(self.update,_candle)
        self.worker.start()
        
    def get_candles_as_dataframe(self):
        df = pd.DataFrame([data.__dict__ for data in self.candles])
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
            return []
    #@lru_cache(maxsize=128)
    def get_ma_ohlc_at_index(self,index):
        #print(index,)
        _index = self.opens.output_times[index]
        ohlc = [self.opens.output_values[index],self.highs.output_values[index],self.lows.output_values[index],self.closes.output_values[index],\
            self.hl2s.output_values[index],self.hlc3s.output_values[index],self.ohlc4s.output_values[index]]
        return _index, ohlc
    
    def update_ma_ohlc(self,lastcandle:OHLCV):
        _new_time = lastcandle.time
        if self.candles != []:
            _last_time = self.candles[-1].time

            if _new_time == _last_time:
                self.highs.update(lastcandle)
                self.lows.update(lastcandle)
                self.closes.update(lastcandle)
                self.opens.update(lastcandle)
                self.hl2s.update(lastcandle)
                self.hlc3s.update(lastcandle)
                self.ohlc4s.update(lastcandle)
            else:
                self.highs.add(lastcandle)
                self.lows.add(lastcandle)
                self.closes.add(lastcandle)
                self.opens.add(lastcandle)
                self.hl2s.add(lastcandle)
                self.hlc3s.add(lastcandle)
                self.ohlc4s.add(lastcandle)

    def compute(self, i:int):
        _index, ohlc = self.get_ma_ohlc_at_index(i)
        _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6]
        if _open != None and  _high != None and _low != None and _close != None:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = round(ohlc[0],self._precision),round(ohlc[1],self._precision),round(ohlc[2],self._precision),round(ohlc[3],self._precision),\
                round(ohlc[4],self._precision),round(ohlc[5],self._precision),round(ohlc[6],self._precision)
            self.candles.append(OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,self._candles.candles[i].volume,self._candles.candles[i].time,_index))

    def reset(self):
        self.candles = []
    def fisrt_gen_data(self):
        self.candles = []
        self.is_genering = True
        self.highs = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="high")
        self.lows = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="low")
        self.closes = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="close")
        self.opens = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="open")
        
        self.hl2s = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="hl2")
        self.hlc3s = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="hlc3")
        self.ohlc4s = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="ohlc4")
        
        [self.compute(i) for i in range(len(self._candles.candles))]
        
        self.df = pd.DataFrame([data.__dict__ for data in self.candles])
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
            #self.gen_data(setdata)
        self.sig_reset_all.emit()
        return self.candles
    
    def gen_data(self,setdata):
        if self.is_genering == False:
            self.is_genering = True
            self.first_gen = False
            self.candles = []
            self.highs = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="high")
            self.lows = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="low")
            self.closes = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="close")
            self.opens = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="open")
            
            self.hl2s = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="hl2")
            self.hlc3s = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="hlc3")
            self.ohlc4s = INDICATOR.get_ma(self.ma_type,period=self.period,input_values=self._candles.candles,_type="ohlc4")
            
            [self.compute(i) for i in range(len(self._candles.candles))]
            
            self.df = pd.DataFrame([data.__dict__ for data in self.candles])
            self.first_gen = True
            self.is_genering = False
            return self.candles
    

    def update(self, _candle:List[OHLCV]):
        if (self.first_gen == True) and (self.is_genering == False):
            if self._candles.candles != []:
                # new_candle =  self._candles.candles[-1]
                new_candle = _candle[-1]
                self.update_ma_ohlc(new_candle)
                _index, ohlc = self.get_ma_ohlc_at_index(-1)
                _open, _high, _low, _close = round(ohlc[0],self._precision),round(ohlc[1],self._precision),round(ohlc[2],self._precision),round(ohlc[3],self._precision)
                
                hl2 = round(ohlc[4],self._precision)
                hlc3 = round(ohlc[5],self._precision)
                ohlc4 = round(ohlc[6],self._precision)

                if new_candle.time == self.candles[-1].time:
                    _index = self.candles[-1].index
                    ha_candle = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,new_candle.volume,new_candle.time,_index)
                    if ha_candle.close != self.candles[-1].close or\
                        ha_candle.high != self.candles[-1].high or\
                        ha_candle.low != self.candles[-1].low or\
                        ha_candle.open != self.candles[-1].open:
                        self.candles[-1] = ha_candle
                        
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
                        return False
                else:
                    _index = self.candles[-1].index + 1
                    ha_candle = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,new_candle.volume,new_candle.time,_index)
                    self.candles.append(ha_candle)
                    
                    new_row = pd.DataFrame([data.__dict__ for data in self.candles[-1:]])
                    self.df = pd.concat([self.df, new_row], ignore_index=True)
                    
                    self.sig_add_candle.emit(self.candles[-2:])
                    #QCoreApplication.processEvents()
                    return True
        return False
            