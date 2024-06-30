from typing import List, Any

from atklip.indicators.talipp.indicator_util import has_valid_values
from atklip.indicators.talipp.indicators.EMA import EMA
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.input import SamplingPeriodType


class TRIX(Indicator):
    """TRIX.

    Input type: `float`

    Output type: `float`

    Args:
        period: Period.
        input_values: List of input values.
        input_indicator: Input indicator.
        input_modifier: Input modifier.
        input_sampling: Input sampling type.
    """

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

        self.ema1 = EMA(period,_type=_type)
        self.ema2 = EMA(period, input_indicator = self.ema1,_type=_type)
        self.ema3 = EMA(period, input_indicator = self.ema2,_type=_type)

        self.add_sub_indicator(self.ema1)

        self.initialize(input_values, input_indicator)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.ema3, 2):
            return None
        if self.ema3[-2] == 0:
            return None
        return 10000.0 * (self.ema3[-1] - self.ema3[-2]) / self.ema3[-2]
