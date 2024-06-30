from typing import List, Any

from atklip.indicators.talipp.indicator_util import has_valid_values
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.input import SamplingPeriodType


class ROC(Indicator):
    """Rate Of Change.

    Input type: `float`

    Output type: `float`

    Args:
        period: Look-back period.
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

        self.initialize(input_values, input_indicator)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.input_values, self.period+1):
            return None
        else:
            if self.input_values[-self.period - 1] == 0:
                return None
            return 100.0 * (self.input_values[-1] - self.input_values[-self.period - 1]) / self.input_values[-self.period - 1]
