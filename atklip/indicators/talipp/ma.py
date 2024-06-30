"""Utilities for moving averages."""

from enum import Enum, auto
from typing import List

from atklip.indicators.talipp.exceptions import TalippException
from atklip.indicators.talipp.indicators.DEMA import DEMA
from atklip.indicators.talipp.indicators.EMA import EMA
from atklip.indicators.talipp.indicators.HMA import HMA
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.indicators.SMA import SMA
from atklip.indicators.talipp.indicators.SMMA import SMMA
from atklip.indicators.talipp.indicators.T3 import T3
from atklip.indicators.talipp.indicators.TEMA import TEMA
from atklip.indicators.talipp.indicators.TRIX import TRIX
from atklip.indicators.talipp.indicators.VWMA import VWMA
from atklip.indicators.talipp.indicators.WMA import WMA
from atklip.indicators.talipp.indicators.ZLEMA import ZLEMA
from atklip.indicators.talipp.indicators.ALMA import ALMA
from atklip.indicators.talipp.indicators.KAMA import KAMA
from atklip.indicators.talipp.indicators.SuperSmooth import SUPERSMOOTH



class MAType(Enum):
    """Moving average type enum."""

    ALMA = "ALMA"
    """[Arnaud Legoux Moving Average][talipp.indicators.ALMA]"""

    DEMA = "DEMA"
    """[Double Exponential Moving Average][talipp.indicators.DEMA]"""

    EMA = "EMA"
    """[Exponential Moving Average][talipp.indicators.EMA]"""

    HMA = "HMA"
    "[Hull Moving Average][talipp.indicators.HMA]"

    KAMA = "KAMA"
    """[Kaufman's Adaptive Moving Average][talipp.indicators.KAMA]"""

    SMA = "SMA"
    """[Standard Moving Average][talipp.indicators.SMA]"""

    SMMA = "SMMA"
    """[Smoothed Moving Average][talipp.indicators.SMMA]"""

    T3 = "T3"
    """[T3 Moving Average][talipp.indicators.T3]"""

    TEMA = "TEMA"
    """[Triple Exponential Moving Average][talipp.indicators.TEMA]"""

    TRIX = "TRIX"
    """[TRIX][talipp.indicators.TRIX]"""

    VWMA = "VWMA"
    """[Volume Weighted Moving Average][talipp.indicators.VWMA]"""

    WMA = "WMA" 
    """[Weighted Moving Average][talipp.indicators.WMA]"""

    ZLEMA = "ZLEMA"
    """[Zero Lag Exponential Moving Average][talipp.indicators.ZLEMA]"""
    SUPERSMOOTH = "SUPERSMOOTH"

class MAFactory:
    """Moving average object factory."""

    @staticmethod
    def get_ma(ma_type: MAType,
               period: int,
               input_values: List[float] = None,
               input_indicator: Indicator = None,
               input_modifier: InputModifierType = None,
               _type: str="") -> Indicator:
        """Return a moving average indicator for given [moving average type][talipp.ma.MAType].

            Only moving averages which do not have other than `period` parameter can be generated (unless they provide default values for them).

            Args:
                ma_type: The moving average to be generated.
                period: The period to be passed into the moving average object.
                input_values: The input values to be passed into the moving average object.
                input_indicator: The input indicator to be passed into the moving average object.
                input_modifier: The input modifier to be passed into the moving average object.

            Returns:
                Moving average indicator.

            Raises:
                TalippException: Unsupported moving average type passed in.
            """
        if ma_type == MAType.SMA:
            return SMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.SMMA:
            return SMMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.DEMA:
            return DEMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.EMA:
            return EMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.TEMA:
            return TEMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.HMA:
            return HMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.VWMA:
            return VWMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier)
        elif ma_type == MAType.WMA:
            return WMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.T3:
            return T3(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.TRIX:
            return TRIX(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.ZLEMA:
            return ZLEMA(period=period, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        elif ma_type == MAType.SUPERSMOOTH:
            return SUPERSMOOTH(period=period,offset=0.85,sigma=6, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        # elif ma_type == MAType.KAMA:
        #     return KAMA(period=period,fast_ema_constant_period=2, slow_ema_constant_period=30, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        else:
            raise TalippException(f"Unsupported moving average type {ma_type.name}.")
    
    @staticmethod
    def get_alma(ma_type: MAType,
               period: int,
               offset: float=0.85,
               sigma: float=6,
               input_values: List[float] = None,
               input_indicator: Indicator = None,
               input_modifier: InputModifierType = None,
               _type: str="") -> Indicator:

        if ma_type == MAType.ALMA:
            return ALMA(period=period,offset=offset,sigma=sigma, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        else:
            raise TalippException(f"Unsupported moving average type {ma_type.name}.")
    @staticmethod
    def get_kama(ma_type: MAType,
               period: int,
               offset: float=0.85,
               sigma: float=6,
               input_values: List[float] = None,
               input_indicator: Indicator = None,
               input_modifier: InputModifierType = None,
               _type: str="") -> Indicator:

        if ma_type == MAType.KAMA:
            return KAMA(period=period,fast_ema_constant_period=2, slow_ema_constant_period=30, input_values=input_values, input_indicator=input_indicator, input_modifier=input_modifier,_type=_type)
        else:
            raise TalippException(f"Unsupported moving average type {ma_type.name}.")
