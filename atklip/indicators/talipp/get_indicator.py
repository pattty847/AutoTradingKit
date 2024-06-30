from enum import Enum, auto
from typing import List
from atklip.indicators.talipp.exceptions import TalippException
from atklip.indicators.talipp.indicators import  AccuDist, ADX, ALMA, AO, Aroon, ATR, BB, BOP, CCI, ChaikinOsc, ChandeKrollStop, CHOP, \
    CoppockCurve, DEMA, DonchianChannels, DPO, EMA, EMV, ForceIndex, HMA, Ichimoku, KAMA, KeltnerChannels, KST, KVO, \
    MACD, MassIndex,McGinleyDynamic, MeanDev, OBV, PivotsHL, ROC, RSI, ParabolicSAR, SFX, SMA, SMMA, SOBV, STC, StdDev, Stoch, StochRSI, \
    SuperTrend, T3, TEMA, TRIX, TSI, TTM, UO, VTX, VWAP, VWMA, WMA, ZLEMA, IBS,SUPERSMOOTH
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.ohlcv import OHLCV
from atklip.indicators.talipp.input import SamplingPeriodType
from atklip.indicators.talipp.ma import MAType, MAFactory

class IndicatorType(Enum):
    IBS = "IBS"
    MACD = "Moving Average Convergence Divergence (MACD)"
    AccuDist = "Accumulation/Distribution (ADL)"
    ADX = "Average Directional Index (ADX)"
    ALMA = "ALMA-Arnaud Legoux Moving Average"
    AO = "Awesome Oscillator (AO)"
    Aroon = "Aroon"
    ATR = "Average True Range (ATR)"
    BB = "Bollinger Bands (BB)"
    BOP = "Balance of Power (BOP)"
    CCI = "Commodity Channel Index (CCI)"
    ChaikinOsc = "Chaikin Oscillator"
    ChandeKrollStop = "Chande Kroll Stop"
    CHOP = "Choppiness Index (CHOP)"
    CoppockCurve = "Coppock Curve"
    DEMA = "DEMA-Double Exponential Moving Average"
    DonchianChannels = "Donchian Channel (DC)"
    DPO = "Detrended Price Oscillator (DPO)"
    EMA = "EMA-Exponential Moving Average"
    EMV = "Ease of Movement (EMV)"
    ForceIndex = "Force Index"
    HMA = "HMA-Hull Moving Average"
    Ichimoku = "Ichimoku Kinko Hyo"
    KAMA = "KAMA-Kaufman's Adaptive Moving Average"
    KeltnerChannels = "Keltner Channel (KC)"
    KST = "Know Sure Thing (KST)"
    KVO = "Klinger Volume Oscillator (KVO)"
    MassIndex = "Mass Index"
    McGinleyDynamic = "McGinley Dynamic"
    MeanDev = "Mean Deviation"
    PivotsHL = "Pivots High/Low"
    ROC = "Rate of Change (ROC)"
    RSI = "Relative strength index (RSI)"
    ParabolicSAR = "Parabolic SAR"
    SFX = "SFX TOR"
    SMA = "SMA-Simple Moving Average"
    SMMA = "SMMA-Smoothed Moving Average"
    OBV = "On-balance Volume (OBV)"
    SOBV = "Smoothed On-balance Volume (SOBV)"
    STC = "Schaff Trend Cycle (STC)"
    StdDev = "StdDev"
    Stoch = "Stochastic Oscillator"
    StochRSI = "Stochastic RSI"
    SuperTrend = "Super Trend"
    T3 = "T3-T3 Moving Average"
    TEMA = "TEMA-Triple Exponential Moving Average"
    TRIX = "TRIX"
    TSI = "True Strength Index (TSI)"
    TTM = "TTM Squeeze"
    UO = "Ultimate Oscillator (UO)"
    VTX = "Vortex Indicator (VTX)"
    VWAP = "VWAP"
    VWMA = "VWMA-Volume Weighted Moving Average"
    WMA = "WMA-Weighted Moving Average"
    ZLEMA = "ZLEMA-Zero Lag Exponential Moving Average"
    SUPERSMOOTH = "Super Smooth Aglorizm"
    CANDLE_PATTERN = "Candle Pattern"
    CHART_PATTERN = "Chart pattern"
    JAPAN_CANDLE = "japan"
    HEIKINASHI_CANDLE = "heikin"
    SMOOTH_JAPAN_CANDLE = "smooth_jp"
    SMOOTH_HEIKINASHI_CANDLE = "smooth_heikin"
    N_SMOOTH_HEIKIN = "n_smooth_heikin"
    N_SMOOTH_JP = "n_smooth_jp"
    VOLUME = "Volume"
    HISTOGRAM = "Histogram"
    CANDLESTICK = "CandleStick"
    SUB_CHART = "Sub_Chart"

class INDICATOR:
    """Moving average object factory."""
    @staticmethod
    def get_ma(ma_type: MAType,
               period: int,
               input_values: List[float] = None,
               input_indicator: Indicator = None,
               input_modifier: InputModifierType = None,
               _type: str="") -> Indicator:
        if ma_type.name == "SMA":
            return SMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "SMMA":
            return SMMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "DEMA":
            return DEMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "EMA":
            return EMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "TEMA":
            return TEMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "HMA":
            return HMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "WMA":
            return WMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "TRIX":
            return TRIX(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "ZLEMA":
            return ZLEMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type.name == "SUPERSMOOTH":
            return SUPERSMOOTH(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        else:
            raise TalippException(f"Unsupported moving average type {ma_type.name}.")
  
    @staticmethod
    def ALMA(period: int,
            offset: float,
            sigma: float,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return ALMA(period=period,
                        offset=offset,
                        sigma=sigma, 
                        input_values=input_values, 
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling = input_sampling,
                        _type=_type)
    @staticmethod
    def KAMA(period: int,
            fast_ema_constant_period: int,
            slow_ema_constant_period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return KAMA(period=period,
                        fast_ema_constant_period=fast_ema_constant_period, 
                        slow_ema_constant_period=slow_ema_constant_period, 
                        input_values=input_values, 
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling,
                        _type=_type)
    @staticmethod
    def AccuDist(input_values: List[float] = None,
               input_indicator: Indicator = None,
               input_modifier: InputModifierType = None,
               input_sampling: str="") -> Indicator:
            return AccuDist(input_values=input_values, 
                            input_indicator=input_indicator, 
                            input_modifier=input_modifier,
                            input_sampling=input_sampling)
    @staticmethod
    def IBS(input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return IBS(input_values=input_values, 
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling)
    @staticmethod
    def ADX(di_period: int,
            adx_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return ADX(di_period=di_period,
                       adx_period=adx_period,
                       input_values=input_values, 
                       input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       input_sampling=input_sampling)
    @staticmethod
    def AO(fast_period: int,
            slow_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return AO(fast_period=fast_period,
                      slow_period=slow_period,
                      input_values=input_values, 
                      input_indicator=input_indicator, 
                      input_modifier=input_modifier,
                      ma_type=ma_type,
                      input_sampling=input_sampling)

    @staticmethod
    def Aroon(period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return Aroon(period=period,
                         input_values=input_values, 
                         input_indicator=input_indicator, 
                         input_modifier=input_modifier,
                         input_sampling=input_sampling)
        
    @staticmethod
    def ATR(period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return ATR(period=period,
                       input_values=input_values, 
                       input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       input_sampling=input_sampling)
        
    @staticmethod
    def BB(period: int,
            std_dev_mult: float,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return BB(period=period,
                      std_dev_mult=std_dev_mult,
                      input_values=input_values, 
                      input_indicator=input_indicator, 
                      input_modifier=input_modifier,
                      ma_type=ma_type,
                      input_sampling=input_sampling,
                      _type=_type)
        
    @staticmethod
    def BOP(input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: str="") -> Indicator:
            return BOP(input_values=input_values, 
                       input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       input_sampling=input_sampling)
        
    @staticmethod
    def CCI(input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: str="") -> Indicator:
            return CCI(input_values=input_values, 
                       input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       input_sampling=input_sampling)
        
    @staticmethod
    def ChaikinOsc(fast_period: int,
            slow_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.EMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return ChaikinOsc(fast_period=fast_period,
                              slow_period=slow_period,
                              input_values=input_values, 
                              input_indicator=input_indicator, 
                              input_modifier=input_modifier,
                              ma_type=ma_type,
                              input_sampling=input_sampling)
        
    @staticmethod
    def ChandeKrollStop(atr_period: int,
            atr_mult: float,
            period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return ChandeKrollStop(atr_period=atr_period,
                                   atr_mult=atr_mult,
                                   period=period,
                                   input_values=input_values, 
                                   input_indicator=input_indicator, 
                                   input_modifier=input_modifier,
                                   input_sampling=input_sampling)
        
        
    @staticmethod
    def CHOP(period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return CHOP(period=period,
                        input_values=input_values, 
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling)
        
    @staticmethod
    def CoppockCurve(fast_roc_period: int,
                    slow_roc_period: int,
                    wma_period: int,
                    input_values: List[float] = None,
                    input_indicator: Indicator = None,
                    input_modifier: InputModifierType = None,
                    input_sampling: SamplingPeriodType = None,
                    _type: str = "") -> Indicator:
            return CoppockCurve(fast_roc_period=fast_roc_period,
                                slow_roc_period=slow_roc_period,
                                wma_period=wma_period,
                                input_values=input_values, 
                                input_indicator=input_indicator, 
                                input_modifier=input_modifier,
                                input_sampling=input_sampling,
                                _type=_type)
        
    @staticmethod
    def DonchianChannels(period: int,
                    input_values: List[OHLCV] = None,
                    input_indicator: Indicator = None,
                    input_modifier: InputModifierType = None,
                    input_sampling: SamplingPeriodType = None) -> Indicator:
            return DonchianChannels(period=period,
                                    input_values=input_values, 
                                    input_indicator=input_indicator, 
                                    input_modifier=input_modifier,
                                    input_sampling=input_sampling)
        
    
    @staticmethod
    def DPO(period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return DPO(period=period,
                       input_values=input_values, 
                       input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       ma_type=ma_type,
                       input_sampling=input_sampling,
                       _type=_type)
        
    @staticmethod
    def EMV(period: int,
            volume_div: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return EMV(period=period,
                       volume_div=volume_div,
                       input_values=input_values, 
                       input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       ma_type=ma_type,
                       input_sampling=input_sampling)
        
    @staticmethod
    def ForceIndex(period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.EMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return ForceIndex(period=period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,ma_type=ma_type,input_sampling=input_sampling)
        
    @staticmethod
    def Ichimoku(kijun_period: int,
            tenkan_period: int,
            chikou_lag_period: int,
            senkou_slow_period: int,
            senkou_lookup_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return Ichimoku(kijun_period=kijun_period,tenkan_period=tenkan_period,chikou_lag_period=chikou_lag_period,senkou_slow_period=senkou_slow_period,senkou_lookup_period=senkou_lookup_period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling)
        
    @staticmethod
    def KeltnerChannels(    ma_period: int,
                        atr_period: int,
                        atr_mult_up: float,
                        atr_mult_down: float,
                        input_values: List[OHLCV] = None,
                        input_indicator: Indicator = None,
                        input_modifier: InputModifierType = None,
                        ma_type: MAType = MAType.EMA,
                        input_sampling: SamplingPeriodType = None) -> Indicator:
            return KeltnerChannels(ma_period=ma_period,atr_period=atr_period,atr_mult_up=atr_mult_up,atr_mult_down=atr_mult_down,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,ma_type=ma_type,input_sampling=input_sampling)
        
    @staticmethod
    def KST(roc1_period: int,
            roc1_ma_period: int,
            roc2_period: int,
            roc2_ma_period: int,
            roc3_period: int,
            roc3_ma_period: int,
            roc4_period: int,
            roc4_ma_period: int,
            signal_period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return KST(roc1_period=roc1_period,
                        roc1_ma_period=roc1_ma_period,
                        roc2_period=roc2_period,
                        roc2_ma_period=roc2_ma_period,
                        roc3_period=roc3_period,
                        roc3_ma_period=roc3_ma_period,
                        roc4_period=roc4_period,
                        roc4_ma_period=roc4_ma_period,
                        signal_period=signal_period,
                        input_values=input_values,
                        input_indicator=input_indicator,
                        input_modifier=input_modifier,
                        ma_type=ma_type,
                        input_sampling=input_sampling,
                        _type=_type)
        
   
    @staticmethod
    def KVO(fast_period: int,
            slow_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.EMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return KVO(fast_period=fast_period,slow_period=slow_period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,ma_type=ma_type)
        
    @staticmethod
    def MACD(fast_period: int,
            slow_period: int,
            signal_period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.EMA,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return MACD(fast_period=fast_period,slow_period=slow_period,signal_period=signal_period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,ma_type=ma_type,_type=_type)
        
    @staticmethod
    def MassIndex(ma_period: int,
                ma_ma_period: int,
                ma_ratio_period: int,
                input_values: List[OHLCV] = None,
                input_indicator: Indicator = None,
                input_modifier: InputModifierType = None,
                ma_type: MAType = MAType.EMA,
                input_sampling: SamplingPeriodType = None) -> Indicator:
            return MassIndex(ma_period=ma_period,ma_ma_period=ma_ma_period,ma_ratio_period=ma_ratio_period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,ma_type=ma_type)
        
    @staticmethod
    def McGinleyDynamic(period: int,
                        input_values: List[float] = None,
                        input_indicator: Indicator = None,
                        input_modifier: InputModifierType = None,
                        input_sampling: SamplingPeriodType = None,
                        _type: str = "") -> Indicator:
            return McGinleyDynamic(period=period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,_type=_type)
        
    @staticmethod
    def MeanDev(period: int,
                input_values: List[float] = None,
                input_indicator: Indicator = None,
                input_modifier: InputModifierType = None,
                ma_type: MAType = MAType.SMA,
                input_sampling: SamplingPeriodType = None,
                _type: str = "") -> Indicator:
            return MeanDev(period=period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,ma_type=ma_type,input_sampling=input_sampling,_type=_type)
        
    @staticmethod
    def OBV(input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return OBV(input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling)
        
    @staticmethod
    def PivotsHL(    high_period: int,
                low_period: int,
                input_values: List[OHLCV] = None,
                input_indicator: Indicator = None,
                input_modifier: InputModifierType = None,
                input_sampling: SamplingPeriodType = None) -> Indicator:
            return PivotsHL(high_period=high_period,low_period=low_period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling)
        
    @staticmethod
    def ROC(period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return ROC(period=period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,_type=_type)
        
    @staticmethod
    def RSI(period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return RSI(period=period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,_type=_type)
        
    @staticmethod
    def ParabolicSAR(init_accel_factor: float,
                    accel_factor_inc: float,
                    max_accel_factor: float,
                    input_values: List[OHLCV] = None,
                    input_indicator: Indicator = None,
                    input_modifier: InputModifierType = None,
                    input_sampling: SamplingPeriodType = None) -> Indicator:
            return ParabolicSAR(init_accel_factor=init_accel_factor,accel_factor_inc=accel_factor_inc,max_accel_factor=max_accel_factor,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling)
        
    @staticmethod
    def SFX(atr_period: int,
            std_dev_period: int,
            std_dev_smoothing_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return SFX(atr_period=atr_period,std_dev_period=std_dev_period,std_dev_smoothing_period=std_dev_smoothing_period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling,ma_type=ma_type)
        
    @staticmethod
    def SOBV(period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return SOBV(period=period,input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,input_sampling=input_sampling)
        
    @staticmethod
    def STC(fast_macd_period: int,
            slow_macd_period: int,
            stoch_period: int,
            stoch_smoothing_period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            stoch_ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return STC(fast_macd_period=fast_macd_period,
                       slow_macd_period=slow_macd_period,
                       stoch_period=stoch_period,
                       stoch_smoothing_period=stoch_smoothing_period,
                       input_values=input_values,
                        input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       stoch_ma_type=stoch_ma_type,
                       input_sampling=input_sampling,
                       _type=_type)
        
    @staticmethod
    def StdDev(period: int,
                input_values: List[float] = None,
                input_indicator: Indicator = None,
                input_modifier: InputModifierType = None,
                input_sampling: SamplingPeriodType = None,
                _type: str = "") -> Indicator:
            return StdDev(period=period,
                       input_values=input_values,
                        input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       input_sampling=input_sampling,
                       _type=_type)
        
    @staticmethod
    def Stoch(smoothing_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return Stoch(smoothing_period=smoothing_period,
                       input_values=input_values,
                        input_indicator=input_indicator, 
                       input_modifier=input_modifier,
                       input_sampling=input_sampling,
                       ma_type=ma_type)
        
    @staticmethod
    def StochRSI(    rsi_period: int,
                stoch_period: int,
                k_smoothing_period: int,
                d_smoothing_period: int,
                input_values: List[float] = None,
                input_indicator: Indicator = None,
                input_modifier: InputModifierType = None,
                ma_type: MAType = MAType.SMA,
                input_sampling: SamplingPeriodType = None,
                _type: str = "") -> Indicator:
            return StochRSI(rsi_period=rsi_period,
                            stoch_period=stoch_period,
                            k_smoothing_period=k_smoothing_period,
                            d_smoothing_period=d_smoothing_period,
                            input_values=input_values,
                            input_indicator=input_indicator, 
                            input_modifier=input_modifier,
                            input_sampling=input_sampling,
                            ma_type=ma_type,
                            _type=_type)
        
    @staticmethod
    def SuperTrend(atr_period: int,
                    mult: int,
                    input_values: List[OHLCV] = None,
                    input_indicator: Indicator = None,
                    input_modifier: InputModifierType = None,
                    input_sampling: SamplingPeriodType = None) -> Indicator:
            return SuperTrend(atr_period=atr_period,
                            mult=mult,
                            input_values=input_values,
                            input_indicator=input_indicator, 
                            input_modifier=input_modifier,
                            input_sampling=input_sampling)
        
    @staticmethod
    def TSI(fast_period: int,
            slow_period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.EMA,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return TSI(fast_period=fast_period,
                        slow_period=slow_period,
                        input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling,
                        ma_type=ma_type,
                        _type=_type)
        
    @staticmethod
    def TTM(period: int,
            bb_std_dev_mult: float = 2,
            kc_atr_mult: float = 1.5,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            ma_type: MAType = MAType.SMA,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return TTM(period=period,
                        bb_std_dev_mult=bb_std_dev_mult,
                        kc_atr_mult=kc_atr_mult,
                        input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling,
                        ma_type=ma_type)
        
    @staticmethod
    def UO(fast_period: int,
            mid_period: int,
            slow_period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return UO(fast_period=fast_period,
                        mid_period=mid_period,
                        slow_period=slow_period,
                        input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling)
        
    @staticmethod
    def VTX(period: int,
            input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return VTX(period=period,
                        input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling)
        
    @staticmethod
    def VWAP(input_values: List[OHLCV] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return VWAP(input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling)

    @staticmethod
    def T3(period: int,
            factor: float = 0.7,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None,
            _type: str = "") -> Indicator:
            return T3(period=period,
                      factor=factor,
                        input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling,
                        _type=_type)
        
    
    @staticmethod
    def VWMA(period: int,
            input_values: List[float] = None,
            input_indicator: Indicator = None,
            input_modifier: InputModifierType = None,
            input_sampling: SamplingPeriodType = None) -> Indicator:
            return VWMA(period=period,
                        input_values=input_values,
                        input_indicator=input_indicator, 
                        input_modifier=input_modifier,
                        input_sampling=input_sampling)
       
    