from typing import List, Any

from atklip.indicators.talipp.indicator_util import has_valid_values
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.indicators.OBV import OBV
from atklip.indicators.talipp.input import SamplingPeriodType
from atklip.indicators.talipp.ohlcv import OHLCV


class SOBV(Indicator):
    """Smoothed On Balance Volume.

    Input type: [OHLCV][talipp.ohlcv.OHLCV]

    Output type: `float`

    Args:
        period: Moving average period.
        input_values: List of input values.
        input_indicator: Input indicator.
        input_modifier: Input modifier.
        input_sampling: Input sampling type.
    """

    def __init__(self, period: int,
                 input_values: List[OHLCV] = None,
                 input_indicator: Indicator = None,
                 input_modifier: InputModifierType = None,
                 input_sampling: SamplingPeriodType = None):
        super().__init__(input_modifier=input_modifier,
                         input_sampling=input_sampling)

        self.period = period

        self.obv = OBV()
        self.add_sub_indicator(self.obv)

        self.initialize(input_values, input_indicator)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.obv, self.period):
            return None
        if float(self.period) == 0:
            return None
        return sum(self.obv[-self.period:]) / float(self.period)
