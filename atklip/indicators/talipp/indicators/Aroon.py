from dataclasses import dataclass
from typing import List, Any

from atklip.indicators.talipp.indicator_util import has_valid_values
from atklip.indicators.talipp.indicators.Indicator import Indicator, InputModifierType
from atklip.indicators.talipp.input import SamplingPeriodType
from atklip.indicators.talipp.ohlcv import OHLCV


@dataclass
class AroonVal:
    """`Aroon` output type.

    Args:
        up: Aroon up.
        down: Aroon down.
    """

    up: float = None
    down: float = None


class Aroon(Indicator):
    """Aroon Up/Down

    Input type: [OHLCV][talipp.ohlcv.OHLCV]

    Output type: [AroonVal][talipp.indicators.Aroon.AroonVal]

    Args:
        period: Aroon period.
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
                         output_value_type=AroonVal,
                         input_sampling=input_sampling)

        self.period = period

        self.initialize(input_values, input_indicator)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.input_values, self.period+1):
            return None

        # search in reversed list in order to get the right-most index
        days_high = self.period - max(reversed(range(self.period + 1)),
                                      key = lambda x: self.input_values[-self.period - 1:][x].high)
        days_low = self.period - min(reversed(range(self.period + 1)),
                                     key = lambda x: self.input_values[-self.period - 1:][x].low)

        return AroonVal(100.0 * (self.period - days_high) / self.period,
                        100.0 * (self.period - days_low) / self.period)

@dataclass
class AroonVal:
    """`Aroon` output type.

    Args:
        up: Aroon up.
        down: Aroon down.
    """

    up: float = None
    down: float = None


class Aroon(Indicator):
    """Aroon Up/Down

    Input type: [OHLCV][talipp.ohlcv.OHLCV]

    Output type: [AroonVal][talipp.indicators.Aroon.AroonVal]

    Args:
        period: Aroon period.
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
                         output_value_type=AroonVal,
                         input_sampling=input_sampling)

        self.period = period

        self.initialize(input_values, input_indicator)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.input_values, self.period+1):
            return None
        if self.period == 0:
            return None

        # search in reversed list in order to get the right-most index
        days_high = self.period - max(reversed(range(self.period + 1)),
                                      key = lambda x: self.input_values[-self.period - 1:][x].high)
        days_low = self.period - min(reversed(range(self.period + 1)),
                                     key = lambda x: self.input_values[-self.period - 1:][x].low)

        return AroonVal(100.0 * (self.period - days_high) / self.period,
                        100.0 * (self.period - days_low) / self.period)
