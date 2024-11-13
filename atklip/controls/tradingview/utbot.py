import numpy as np
import pandas as pd
import atklip.controls.talib.abstract as ta

import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool
from PySide6.QtCore import Signal,QObject


def utbot(dataframe:pd.DataFrame, key_value=1, atr_period=3, ema_period=200)->pd.DataFrame:
    # Calculate ATR and xATRTrailingStop
    xATR = np.array(ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=atr_period))
    nLoss = key_value * xATR
    src = dataframe['close']

    # Initialize arrays
    xATRTrailingStop = np.zeros(len(dataframe))
    xATRTrailingStop[0] = src[0] - nLoss[0]

    # Calculate xATRTrailingStop using vectorized operations
    mask_1 = (src > np.roll(xATRTrailingStop, 1)) & (np.roll(src, 1) > np.roll(xATRTrailingStop, 1))
    mask_2 = (src < np.roll(xATRTrailingStop, 1)) & (np.roll(src, 1) < np.roll(xATRTrailingStop, 1))
    mask_3 = src > np.roll(xATRTrailingStop, 1)

    xATRTrailingStop = np.where(mask_1, np.maximum(np.roll(xATRTrailingStop, 1), src - nLoss), xATRTrailingStop)
    xATRTrailingStop = np.where(mask_2, np.minimum(np.roll(xATRTrailingStop, 1), src + nLoss), xATRTrailingStop)
    xATRTrailingStop = np.where(mask_3, src - nLoss, xATRTrailingStop)

    # Calculate pos using vectorized operations
    mask_buy = (np.roll(src, 1) < xATRTrailingStop) & (src > np.roll(xATRTrailingStop, 1))
    mask_sell = (np.roll(src, 1) > xATRTrailingStop)  & (src < np.roll(xATRTrailingStop, 1))

    pos = np.zeros(len(dataframe))
    pos = np.where(mask_buy, 1, pos)
    pos = np.where(mask_sell, -1, pos)
    pos[~((pos == 1) | (pos == -1))] = 0

    ema = np.array(ta.EMA(dataframe['close'], timeperiod=ema_period))

    buy_condition_utbot = (xATRTrailingStop > ema) & (pos > 0) & (src > ema)
    sell_condition_utbot = (xATRTrailingStop < ema) & (pos < 0) & (src < ema)    

    trend = np.where(buy_condition_utbot, 1, np.where(sell_condition_utbot, -1, 0))

    trend = np.array(trend)

    dataframe['trend'] = trend
    return dataframe
    


class UTBOT_ALERT(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        
        self.key_value:float=dict_ta_params.get("key_value",1)
        self.atr_period:float=dict_ta_params.get("atr_period",3)
        self.ema_period:int=dict_ta_params.get("ema_period",200) 

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"UTBot {self.key_value} {self.atr_period} {self.ema_period}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.ut = np.array([]),np.array([])

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
            
            self.key_value:float=dict_ta_params.get("key_value",1)
            self.atr_period:float=dict_ta_params.get("atr_period",3)
            self.ema_period:int=dict_ta_params.get("ema_period",200) 
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.key_value}-{self.atr_period}-{self.ema_period}"

            self.indicator_name = ta_param
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.started_worker()
    
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
        if self.xdata == []:
            return [],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            ut =self.ut
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            ut =self.ut[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            ut =self.ut[start:]
        else:
            x_data = self.xdata[start:stop]
            ut =self.ut[start:stop]
        return np.array(x_data),np.array(ut)
    
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
        ut = INDICATOR["trend"].dropna()
        return ut
    
    def calculate(self,df: pd.DataFrame):
        INDICATOR = utbot(dataframe=df,
                            key_value=self.key_value,
                            atr_period=self.atr_period,
                            ema_period=self.ema_period
                            ).dropna().round(4)
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
                
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
                
        ut = self.calculate(df)
        _index = df["index"]
        
        _len = len(ut)
        _index = df["index"].tail(_len)
                
        self.df = pd.DataFrame({
                            'index':_index,
                            "ut":ut,
                            })
        self.xdata,self.ut = self.df["index"].to_list(),self.df["ut"].to_list()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
        self.is_current_update = True
          
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        
        ut = self.calculate(df)
        _index = df["index"]
        
        _len = len(ut)
        _index = df["index"].tail(_len)
        
        _df = pd.DataFrame({
                            'index':_index,
                            "ut":ut
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "ut":ut,
                            })
        self.xdata,self.ut = self.df["index"].to_list(),self.df["ut"].to_list()
        
        
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
            df:pd.DataFrame = self._candles.get_df(self.ema_period*2)
            
            ut = self.calculate(df)            
            _len = len(ut)
            _index = df["index"].tail(_len)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "ut":[ut.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.ut = self.df["index"].to_list(),self.df["ut"].to_list()
            
            self.sig_add_candle.emit()
            self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.ema_period*5)
            
            ut = self.calculate(df)
            
            self.df.iloc[-1] = [new_candle.index,ut.iloc[-1]]
            self.xdata,self.ut = self.df["index"].to_list(),self.df["ut"].to_list()
            
            self.sig_update_candle.emit()
            self.is_current_update = True

