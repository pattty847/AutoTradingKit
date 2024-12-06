import pandas as pd
import numpy as np

def candle_pattern(df:pd.DataFrame,doji_size: float= 0.05):
    
    output_df = pd.DataFrame([])
    
    output_df["index"] = df["index"]
    # df['doji'] = (abs(df['open'] - df['close']) <= (df['high'] - df['low']) * doji_size)
    output_df['evening_star'] = (df['close'].shift(2) > df['open'].shift(2)) & \
                        (np.minimum(df['open'].shift(1), df['close'].shift(1)) > df['close'].shift(2)) & \
                        (df['open'] < np.minimum(df['open'].shift(1), df['close'].shift(1))) & \
                        (df['close'] < df['open'])

    output_df['morning_star'] = (df['close'].shift(2) < df['open'].shift(2)) & \
                        (np.maximum(df['open'].shift(1), df['close'].shift(1)) < df['close'].shift(2)) & \
                        (df['open'] > np.maximum(df['open'].shift(1), df['close'].shift(1))) & \
                        (df['close'] > df['open'])

    output_df['shooting_star'] = (df['open'].shift(1) < df['close'].shift(1)) & \
                        (df['open'] > df['close'].shift(1)) & \
                        ((df['high'] - np.maximum(df['open'], df['close'])) >= abs(df['open'] - df['close']) * 3) & \
                        ((np.minimum(df['close'], df['open']) - df['low']) <= abs(df['open'] - df['close']))

    # df['hammer'] = ((df['high'] - df['low']) > 3 * abs(df['open'] - df['close'])) & \
    #             (((df['close'] - df['low']) / (0.001 + df['high'] - df['low'])) > 0.6) & \
    #             (((df['open'] - df['low']) / (0.001 + df['high'] - df['low'])) > 0.6)

    # df['inverted_hammer'] = ((df['high'] - df['low']) > 3 * abs(df['open'] - df['close'])) & \
    #                         (((df['high'] - df['close']) / (0.001 + df['high'] - df['low'])) > 0.6) & \
    #                         (((df['high'] - df['open']) / (0.001 + df['high'] - df['low'])) > 0.6)

    output_df['bearish_harami'] = (df['close'].shift(1) > df['open'].shift(1)) & \
                        (df['open'] > df['close']) & \
                        (df['open'] <= df['close'].shift(1)) & \
                        (df['open'].shift(1) <= df['close']) & \
                        (abs(df['open'] - df['close']) < abs(df['close'].shift(1) - df['open'].shift(1)))

    output_df['bullish_harami'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                        (df['close'] > df['open']) & \
                        (df['close'] <= df['open'].shift(1)) & \
                        (df['close'].shift(1) <= df['open']) & \
                        (abs(df['close'] - df['open']) < abs(df['open'].shift(1) - df['close'].shift(1)))

    output_df['bearish_engulfing'] = (df['close'].shift(1) > df['open'].shift(1)) & \
                            (df['open'] > df['close']) & \
                            (df['open'] >= df['close'].shift(1)) & \
                            (df['close'] <= df['open'].shift(1)) & \
                            (abs(df['open'] - df['close']) > abs(df['close'].shift(1) - df['open'].shift(1)))

    output_df['bullish_engulfing'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                            (df['close'] > df['open']) & \
                            (df['close'] >= df['open'].shift(1)) & \
                            (df['open'] <= df['close'].shift(1)) & \
                            (abs(df['close'] - df['open']) > abs(df['open'].shift(1) - df['close'].shift(1)))
    # df['piercing_line'] = (df['close'].shift(1) < df['open'].shift(1)) & \
    #                     (df['open'] < df['low'].shift(1)) & \
    #                     (df['close'] > (df['close'].shift(1) + (df['open'].shift(1) - df['close'].shift(1)) / 2)) & \
    #                     (df['close'] < df['open'].shift(1))

    # df['bullish_belt'] = (df['low'] == df['open']) & \
    #                     (df['open'] < df['low'].rolling(10).min().shift(1)) & \
    #                     (df['close'] > ((df['high'].shift(1) - df['low'].shift(1)) / 2) + df['low'].shift(1))

    output_df['bullish_kicker'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                        (df['open'] >= df['open'].shift(1)) & \
                        (df['close'] > df['open'])

    output_df['bearish_kicker'] = (df['open'].shift(1) < df['close'].shift(1)) & \
                        (df['open'] <= df['open'].shift(1)) & \
                        (df['close'] <= df['open'])
    # df['hanging_man'] = ((df['high'] - df['low']) > 4 * abs(df['open'] - df['close'])) & \
    #                     (((df['close'] - df['low']) / (0.001 + df['high'] - df['low'])) >= 0.75) & \
    #                     (((df['open'] - df['low']) / (0.001 + df['high'] - df['low'])) >= 0.75) & \
    #                     (df['high'].shift(1) < df['open']) & \
    #                     (df['high'].shift(2) < df['open'])

    # df['dark_cloud_cover'] = (df['close'].shift(1) > df['open'].shift(1)) & \
    #                         (((df['close'].shift(1) + df['open'].shift(1)) / 2) > df['close']) & \
    #                         (df['open'] > df['close']) & \
    #                         (df['open'] > df['close'].shift(1)) & \
    #                         (df['close'] > df['open'].shift(1)) & \
    #                         ((df['open'] - df['close']) / (0.001 + (df['high'] - df['low'])) > 0.6)
    return output_df
# # Các mẫu nến khác có thể được bổ sung tương tự theo mã Pine Script gốc.

# # In kết quả kiểm tra mẫu nến
# patterns = ['doji', 'evening_star', 'morning_star', 'shooting_star', 'hammer', 'inverted_hammer', 'bearish_harami', 
#             'bullish_harami', 'bearish_engulfing', 'bullish_engulfing', 'piercing_line', 'bullish_belt', 
#             'bullish_kicker', 'bearish_kicker', 'hanging_man', 'dark_cloud_cover']


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool
from PySide6.QtCore import Signal,QObject

class AllCandlePattern(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params:dict={}) -> None:
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"ALL CDL PATTERN"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

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
        if len(self.df) == 0:
            return []
        if start == 0 and stop == 0:
            df=self.df
        elif start == 0 and stop != 0:
            df=self.df.iloc[:stop]
        elif start != 0 and stop == 0:
            df=self.df.iloc[start:]
        else:
            df=self.df.iloc[start:stop]
        return df
    
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
        column_names = INDICATOR.columns.tolist()
        
        vortex_name = ''
        signalma_name = ''
        
        patterns = ['doji', 'evening_star', 'morning_star', 'shooting_star', 'hammer', 'inverted_hammer', 'bearish_harami', 
            'bullish_harami', 'bearish_engulfing', 'bullish_engulfing', 'piercing_line', 'bullish_belt', 
            'bullish_kicker', 'bearish_kicker', 'hanging_man', 'dark_cloud_cover']
        
        
        for name in column_names:
            if name.__contains__("VTXP_"):
                vortex_name = name
            elif name.__contains__("VTXM_"):
                signalma_name = name

        vortex_ = INDICATOR[vortex_name].dropna().round(4)
        signalma = INDICATOR[signalma_name].dropna().round(4)
        
        return vortex_,signalma
    
    def calculate(self,df: pd.DataFrame):
        INDICATOR = candle_pattern(df)
        return INDICATOR#self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        self.df = self.calculate(df)
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        self.is_current_update = True
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        _df= self.calculate(df)
        _len = len(_df)
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
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
            df:pd.DataFrame = self._candles.get_df(10)
            _df:pd.DataFrame  = self.calculate(df)
            
            _new_df = _df.iloc[[-1]]
            
            # print(type(_new_df),_new_df)
            
            self.df = pd.concat([self.df,_new_df],ignore_index=True)
            self.sig_add_candle.emit()
        self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(10)
            _df = self.calculate(df)
            self.df.iloc[-1] = _df.iloc[-1]
            self.sig_update_candle.emit()
        self.is_current_update = True
           