from functools import lru_cache
import numpy as np
import time
import pandas as pd
from typing import List,Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication,QThreadPool

from atklip.indicators import pandas_ta as ta
from atklip.indicators.ma_type import  PD_MAType
from atklip.indicators.ohlcv import   OHLCV

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
    def __init__(self,precision,_candles,ma_type,period) -> None:
        super().__init__(parent=None)
        self.ma_type:PD_MAType = ma_type
        self.period:int= period
        self._candles: JAPAN_CANDLE|HEIKINASHI|self =_candles
        
        if not isinstance(self._candles,JAPAN_CANDLE) and not isinstance(self._candles,HEIKINASHI):
            self._candles.setParent(self)
            self.signal_delete.connect(self._candles.signal_delete)
        
        self.signal_delete.connect(self.deleteLater)
        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
        self._precision = precision
        self.first_gen = False
        self.is_genering = True
        self._source_name = "SMOOTH_CANDLE"

        self.df = pd.DataFrame([])

        self._candles.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update,Qt.ConnectionType.AutoConnection)
        self._candles.sig_add_candle.connect(self.update,Qt.ConnectionType.AutoConnection)

    @property
    def source_name(self):
        return self._source_name
    @source_name.setter
    def source_name(self,_name):
        self._source_name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
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
        # _index = self.opens.iloc[index]
        _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = self.opens.iloc[index],self.highs.iloc[index],self.lows.iloc[index],self.closes.iloc[index],\
            self.hl2s.iloc[index],self.hlc3s.iloc[index],self.ohlc4s.iloc[index]
        
        if _open != None and  _high != None and _low != None and _close != None:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = round(_open,self._precision),round(_high,self._precision),round(_low,self._precision),round(_close,self._precision),\
                    round(_hl2,self._precision),round(_hlc3,self._precision),round(_ohlc4,self._precision)
            return [_open, _high, _low, _close, _hl2, _hlc3, _ohlc4]
        return []
    
    def update_ma_ohlc(self,lastcandle:OHLCV):
        _new_time = lastcandle.time
        if self.candles != []:
            _last_time = self.candles[-1].time

            if _new_time == _last_time:
                df:pd.DataFrame = self._candles.get_df(self.period*5) #self.period+1
                highs = ta.ma(f"{self.ma_type.name}".lower(), df["high"],length=self.period)
                highs = highs.astype('float32')
                self.highs.iloc[-1] = highs.iloc[-1]

                lows = ta.ma(f"{self.ma_type.name}".lower(), df["low"],length=self.period)
                lows = lows.astype('float32')
                self.lows.iloc[-1] = lows.iloc[-1]

                closes = ta.ma(f"{self.ma_type.name}".lower(), df["close"],length=self.period)
                closes = closes.astype('float32')
                self.closes.iloc[-1] = closes.iloc[-1]

                opens = ta.ma(f"{self.ma_type.name}".lower(), df["open"],length=self.period)
                opens = opens.astype('float32')
                self.opens.iloc[-1] = opens.iloc[-1]

                hl2s = ta.ma(f"{self.ma_type.name}".lower(), df["hl2"],length=self.period)
                hl2s = hl2s.astype('float32')
                self.hl2s.iloc[-1] = hl2s.iloc[-1]

                hlc3s = ta.ma(f"{self.ma_type.name}".lower(), df["hlc3"],length=self.period)
                hlc3s = hlc3s.astype('float32')
                self.hlc3s.iloc[-1] = hlc3s.iloc[-1]

                ohlc4s = ta.ma(f"{self.ma_type.name}".lower(), df["ohlc4"],length=self.period)
                ohlc4s = ohlc4s.astype('float32')
                self.ohlc4s.iloc[-1] = ohlc4s.iloc[-1]

            else:
                df:pd.DataFrame = self._candles.get_df(self.period+1)
                highs = ta.ma(f"{self.ma_type.name}".lower(), df["high"],length=self.period)
                highs = highs.astype('float32')
                self.highs = pd.concat([self.highs, pd.Series([highs.iloc[-1]], index=[len(self.highs)])])

                lows = ta.ma(f"{self.ma_type.name}".lower(), df["low"],length=self.period)
                lows = lows.astype('float32')
                self.lows = pd.concat([self.lows, pd.Series([lows.iloc[-1]], index=[len(self.lows)])])

                closes = ta.ma(f"{self.ma_type.name}".lower(), df["close"],length=self.period)
                closes = closes.astype('float32')
                self.closes = pd.concat([self.closes, pd.Series([closes.iloc[-1]], index=[len(self.closes)])])

                opens = ta.ma(f"{self.ma_type.name}".lower(), df["open"],length=self.period)
                opens = opens.astype('float32')
                self.opens = pd.concat([self.opens, pd.Series([opens.iloc[-1]], index=[len(self.opens)])])

                hl2s = ta.ma(f"{self.ma_type.name}".lower(), df["hl2"],length=self.period)
                hl2s = hl2s.astype('float32')
                self.hl2s = pd.concat([self.hl2s, pd.Series([hl2s.iloc[-1]], index=[len(self.hl2s)])])

                hlc3s = ta.ma(f"{self.ma_type.name}".lower(), df["hlc3"],length=self.period)
                hlc3s = hlc3s.astype('float32')
                self.hlc3s = pd.concat([self.hlc3s, pd.Series([hlc3s.iloc[-1]], index=[len(self.hlc3s)])])

                ohlc4s = ta.ma(f"{self.ma_type.name}".lower(), df["ohlc4"],length=self.period)
                ohlc4s = ohlc4s.astype('float32')
                self.ohlc4s = pd.concat([self.ohlc4s, pd.Series([ohlc4s.iloc[-1]], index=[len(self.ohlc4s)])])
                

    def compute(self,index, i:int):
        _index = index[i]
        ohlc = self.get_ma_ohlc_at_index(i)
        if ohlc != []:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6]
            self.candles.append(OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,self._candles.candles[i].volume,self._candles.candles[i].time,_index))

    def reset(self):
        self.candles = []
    def fisrt_gen_data(self):
        self.candles = []
        self.is_genering = True
        
        df:pd.DataFrame = self._candles.get_df()
        self.highs = ta.ma(f"{self.ma_type.name}".lower(), df["high"],length=self.period)
        self.highs = self.highs.astype('float32')

        self.lows = ta.ma(f"{self.ma_type.name}".lower(), df["low"],length=self.period)
        self.lows = self.lows.astype('float32')

        self.closes = ta.ma(f"{self.ma_type.name}".lower(), df["close"],length=self.period)
        self.closes = self.closes.astype('float32')

        self.opens = ta.ma(f"{self.ma_type.name}".lower(), df["open"],length=self.period)
        self.opens = self.opens.astype('float32')

        self.hl2s = ta.ma(f"{self.ma_type.name}".lower(), df["hl2"],length=self.period)
        self.hl2s = self.hl2s.astype('float32')

        self.hlc3s = ta.ma(f"{self.ma_type.name}".lower(), df["hlc3"],length=self.period)
        self.hlc3s = self.hlc3s.astype('float32')

        self.ohlc4s = ta.ma(f"{self.ma_type.name}".lower(), df["ohlc4"],length=self.period)
        self.ohlc4s = self.ohlc4s.astype('float32')

   
        _index = df["index"].to_numpy()
        
        
        [self.compute(_index,i) for i in range(len(df))]
        
        self.df = pd.DataFrame([data.__dict__ for data in self.candles])
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
        return self.candles
    
    def update(self, _candle:List[OHLCV]):
        if (self.first_gen == True) and (self.is_genering == False):
            if self._candles.candles != []:
                new_candle = _candle[-1]
                self.update_ma_ohlc(new_candle)
                ohlc = self.get_ma_ohlc_at_index(-1)
                _open, _high, _low, _close = ohlc[0],ohlc[1],ohlc[2],ohlc[3]
                hl2 = ohlc[4]
                hlc3 = ohlc[5]
                ohlc4 = ohlc[6]

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
            