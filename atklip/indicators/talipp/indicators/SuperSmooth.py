from typing import List, Any

import numpy as np
from numba import njit
from atklip.indicators.talipp.indicator_util import has_valid_values
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.input import SamplingPeriodType
from atklip.indicators.talipp.ohlcv import OHLCV
ListAny = List[OHLCV]

class SUPERSMOOTH(Indicator):

    def __init__(self, period: int,
                 input_values: List[float] = None,
                 input_indicator: Indicator = None,
                 input_modifier: InputModifierType = None,
                 input_sampling: SamplingPeriodType = None,
                 _type: str=""):
        super().__init__(input_modifier=input_modifier,
                         input_sampling=input_sampling,
                        _type= _type)

        self.period = period
        
        if self.period == 0:
            raise ValueError("period is not be zero")
        
        self.a = np.exp(-1.414 * np.pi / self.period)
        self.b = 2 * self.a * np.cos(1.414 * np.pi / self.period)

        self.initialize(input_values)
    
    def initialize(self, input_values: ListAny = None) -> None:
        if input_values is not None:
            for value in input_values:
                self.add(value)

    def caculate_new_value(self,input_value:OHLCV|Any):
        _time = None    
        if self._type in ["close", "low", "high", "volume", "open","hl2","hlc3","ohlc4"]:
            if isinstance(input_value, OHLCV):
                _time = input_value.index
                if self._type == "close":
                    input_value = input_value.close
                elif self._type == "open":
                    input_value = input_value.open
                elif self._type == "high":
                    input_value = input_value.high
                elif self._type == "low":
                    input_value = input_value.low
                elif self._type == "volume":
                    input_value = input_value.volume
                elif self._type == "hl2":
                    input_value = input_value.hl2
                elif self._type == "hlc3":
                    input_value = input_value.hlc3
                elif self._type == "ohlc4":
                    input_value = input_value.ohlc4
        else:
            if isinstance(input_value, tuple) or isinstance(input_value, list):
                _time = input_value[0]
                input_value = input_value[1]
            else:
                return
        if len(self.input_values) <= 3:
            self.input_values.append(input_value)
            self.output_values.append(input_value)
            self.output_times.append(_time)
            return

        if _time == self.output_times[-1]:
            self.input_values[-1] = input_value
        else:
            self.input_values.append(input_value)
        new_value = self._calculate_new_value()
        self._add_to_output_values(new_value, _time)
        
    def _add_to_output_values(self, value: Any,_time) -> None:
        self._dict_time_value[_time] = value
        if _time == self.output_times[-1]:
            self.output_values[-1] = value
            self.output_times[-1] = _time
            return
        self.output_values.append(value)
        self.output_times.append(_time)
    
    def add(self,_input:OHLCV):
        self.caculate_new_value(_input)
    
    def update(self,_input: OHLCV):
        self.caculate_new_value(_input)
    
    def _calculate_new_value(self) -> Any:
        result = (1 + self.a ** 2 - self.b) / 2 * (self.input_values[-1] + self.input_values[-2]) \
                        + self.b * self.output_values[-2] - self.a ** 2 * self.output_values[-3]
        return result