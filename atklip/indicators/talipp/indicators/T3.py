from typing import List, Any

from atklip.indicators.talipp.indicator_util import has_valid_values
from atklip.indicators.talipp.indicators.EMA import EMA
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.input import SamplingPeriodType


class T3(Indicator):
    """T3 Moving Average.

    Input type: `float`

    Output type: `float`

    Args:
        period: Period.
        factor: Multiplicative factor.
        input_values: List of input values.
        input_indicator: Input indicator.
        input_modifier: Input modifier.
        input_sampling: Input sampling type.
    """

    def __init__(self, period: int,
                 factor: float = 0.7,
                 input_values: List[float] = None,
                 input_indicator: Indicator = None,
                 input_modifier: InputModifierType = None,
                 input_sampling: SamplingPeriodType = None,
                 _type: str=""):
        super().__init__(input_modifier=input_modifier,
                         input_sampling=input_sampling,
                        _type= _type)

        self.period = period

        self.ema1 = EMA(period,_type= _type)
        self.ema2 = EMA(period, input_indicator=self.ema1,_type= _type)
        self.ema3 = EMA(period, input_indicator=self.ema2,_type= _type)
        self.ema4 = EMA(period, input_indicator=self.ema3,_type= _type)
        self.ema5 = EMA(period, input_indicator=self.ema4,_type= _type)
        self.ema6 = EMA(period, input_indicator=self.ema5,_type= _type)

        self.add_sub_indicator(self.ema1)

        self.c1 = -(factor**3)
        self.c2 = 3 * factor**2 + 3 * factor**3
        self.c3 = -6 * factor**2 - 3 * factor - 3 * factor**3
        self.c4 = 1 + 3 * factor + factor**3 + 3 * factor**2

        self.initialize(input_values, input_indicator)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.ema6, 1):
            return None

        return (self.c1 * self.ema6[-1] +
                self.c2 * self.ema5[-1] +
                self.c3 * self.ema4[-1] +
                self.c4 * self.ema3[-1])
