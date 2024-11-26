from psygnal import evented
from dataclasses import dataclass

#@evented
@dataclass
class Object:
    id: str

@dataclass
class BaseCandleModel():
    chart_id: str
    canlde_id:str
    name:str
    id_exchange:str
    symbol:str
    interval:str
#@evented
@dataclass
class SmoothCandleModel(BaseCandleModel):
    mamode:str
    ma_leng:int
    source:str
    precision:float
#@evented
@dataclass
class SuperSmoothCandleModel(BaseCandleModel):
    mamode:str
    ma_leng:int
    n_smooth:int
    source:str
    precision:float
#@evented

@dataclass
class IndicatorBase:
    obj_id:str
    ta_name:str
    source_name:str


@dataclass
class ZigzagModel(IndicatorBase):
    legs:int
    devision:float
    precision:float
#@evented
@dataclass
class MACDModel(IndicatorBase):
    source:str 
    slow_period:int 
    fast_period:int
    signal_period:int
    mamode: str 


@dataclass
class SQeezeModel(IndicatorBase):
    bb_length:int 
    bb_std:float 
    kc_length:int
    kc_scalar:float
    mom_length:int
    mom_smooth:int
    mamode: str 
    use_tr:bool
    lazybear:bool
    detailed:bool
    

#@evented
@dataclass
class MAModel(IndicatorBase):
    mamode:str 
    source:str 
    length:int
#@evented
@dataclass
class BBandsModel(IndicatorBase):
    mamode:str 
    source:str 
    length:int 
    std_dev_mult:float 
#@evented
@dataclass         
class DonchainModel(IndicatorBase):
    lower_length:int 
    upper_length:int 

@dataclass         
class ATKBOTModel(IndicatorBase):
    key_value_long:float
    key_value_short:float
    atr_long_period:float
    ema_long_period:int
    atr_short_period:float
    ema_short_period:int

#@evented
@dataclass 
class ROCModel(IndicatorBase):
    source:str    
    length:int
#@evented
@dataclass
class ROCModel(IndicatorBase):
    source:str    
    length:int 
#@evented
@dataclass
class RSIModel(IndicatorBase):
    source:str    
    length:int 
    mamode:str 

@dataclass
class CCIModel(IndicatorBase):
    length:int 
    c:float     

#@evented
@dataclass    
class STCModel(IndicatorBase):
    source:str   
    tclength:int
    fast:int 
    slow:int 
    mamode:str 
#@evented
@dataclass
class STOCHModel(IndicatorBase):
    smooth_k_period:int 
    k_period:int 
    d_period:int 
    mamode:str 
#@evented
@dataclass
class STOCHRSIModel(IndicatorBase):
    rsi_period:int 
    period:int
    k_period:int
    d_period:int 
    source:str 
    mamode:str 
#@evented
@dataclass 
class VORTEXModel(IndicatorBase):
    period :int
    drift :int
#@evented
@dataclass
class TRIXModel(IndicatorBase):
    length_period :int 
    signal_period:int 
    source:str 
    mamode:str
#@evented
@dataclass          
class TSIModel(IndicatorBase):
    fast_period :int 
    slow_period :int 
    signal_period:int 
    source:str 
    mamode:str 
#@evented
@dataclass
class UOModel(IndicatorBase):
    fast_period :int
    medium_period :int
    slow_period :int
    fast_w_value :float
    medium_w_value :float
    slow_w_value :float
    drift  :int
    offset :int
