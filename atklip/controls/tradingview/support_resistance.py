from concurrent.futures import Future
import pandas as pd
import numpy as np
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta import ema, pivots


def crossover(series1, series2):
    """Kiểm tra xem series1 có cắt lên trên series2 không."""
    return (series1 > series2) & (series1.shift(1) <= series2.shift(1))


def crossunder(series1, series2):
    """Kiểm tra xem series1 có cắt xuống dưới series2 không."""
    return (series1 < series2) & (series1.shift(1) >= series2.shift(1))


def crossabove(series1, value):
    """Kiểm tra xem series1 có cắt lên trên một giá trị cụ thể không."""
    return (series1 > value) & (series1.shift(1) <= value)


def support_resistance_with_breaks(df, left_bars=15, right_bars=15, volume_thresh=20):

    # Calculate pivot highs and lows
    df["high_pivot"] = (
        df["high"]
        .rolling(window=left_bars + right_bars + 1, center=True)
        .apply(
            lambda x: np.nan if np.isnan(x).any() else x[left_bars] == max(x), raw=True
        )
    )
    df["low_pivot"] = (
        df["low"]
        .rolling(window=left_bars + right_bars + 1, center=True)
        .apply(
            lambda x: np.nan if np.isnan(x).any() else x[left_bars] == min(x), raw=True
        )
    )

    df.loc[df["high_pivot"] == 1, "high_use_pivot"] = df["high"]
    df.loc[df["low_pivot"] == 1, "low_use_pivot"] = df["low"]

    # Forward fill the pivot points
    df["high_use_pivot"] = df["high_use_pivot"].ffill()
    df["low_use_pivot"] = df["low_use_pivot"].ffill()

    # Calculate EMAs for volume
    df["volume_ema_5"] = ema(df["volume"], length=5)
    df["volume_ema_10"] = ema(df["volume"], length=10)

    # Calculate volume oscillator
    df["osc"] = 100 * (df["volume_ema_5"] - df["volume_ema_10"]) / df["volume_ema_10"]

    # Conditions for breaks with volume
    df["break_down"] = (
        (df["close"] < df["low_use_pivot"])
        & (df["osc"] > volume_thresh)
        & (df["open"] - df["close"] < df["high"] - df["open"])
    )
    df["break_up"] = (
        (df["close"] > df["high_use_pivot"])
        & (df["osc"] > volume_thresh)
        & (df["open"] - df["low"] > df["close"] - df["open"])
    )

    # Conditions for bull / bear wicks
    df["bull_wick"] = (df["close"] > df["high_use_pivot"]) & (
        df["open"] - df["low"] > df["close"] - df["open"]
    )
    df["bear_wick"] = (df["close"] < df["low_use_pivot"]) & (
        df["open"] - df["close"] < df["high"] - df["open"]
    )

    # Alert conditions
    df["alert_support_broken"] = crossunder(df["close"], df["low_use_pivot"]) & (
        df["osc"] > volume_thresh
    )
    df["alert_resistance_broken"] = crossover(df["close"], df["high_use_pivot"]) & (
        df["osc"] > volume_thresh
    )

    return df


def calculate_support_resistance(
    df, left_bars=15, right_bars=15, volume_thresh=20, toggle_breaks=True
):
    """
    Tính toán hỗ trợ, kháng cự, và các điều kiện phá vỡ.

    :param df: DataFrame chứa các cột: time, open, close, high, low, volume
    :param left_bars: Số thanh bên trái để xác định Pivot
    :param right_bars: Số thanh bên phải để xác định Pivot
    :param volume_thresh: Ngưỡng volume để xác định phá vỡ
    :param toggle_breaks: Bật/tắt tính toán phá vỡ
    :return: DataFrame với các cột mới được thêm vào
    """
    # Tính toán Pivot High và Pivot Low
    df["pivot_high"] = (
        df["high"]
        .rolling(window=left_bars + right_bars + 1)
        .apply(lambda x: x[left_bars] if x[left_bars] == max(x) else np.nan, raw=True)
    )
    df["pivot_low"] = (
        df["low"]
        .rolling(window=left_bars + right_bars + 1)
        .apply(lambda x: x[left_bars] if x[left_bars] == min(x) else np.nan, raw=True)
    )

    # Điền giá trị NaN bằng phương pháp forward fill
    df["pivot_high"] = df["pivot_high"].ffill()
    df["pivot_low"] = df["pivot_low"].ffill()

    # Tính toán Volume %
    # short_ema = df['volume'].ewm(span=5, adjust=False).mean()
    # long_ema = df['volume'].ewm(span=10, adjust=False).mean()

    short_ema = ema(df["volume"], length=5)
    long_ema = ema(df["volume"], length=10)

    df["osc"] = 100 * (short_ema - long_ema) / long_ema

    # Tính toán các điều kiện phá vỡ với volume
    if toggle_breaks:
        df["break_support"] = (
            crossunder(df["close"], df["pivot_low"].shift(right_bars + 1))
            & ~(df["open"] - df["close"] < df["high"] - df["open"])
            & (df["osc"] > volume_thresh)
        )
        df["break_resistance"] = (
            crossover(df["close"], df["pivot_high"].shift(right_bars + 1))
            & ~(df["open"] - df["low"] > df["close"] - df["open"])
            & (df["osc"] > volume_thresh)
        )

    # Tính toán Bull/Bear Wicks
    if toggle_breaks:
        df["bull_wick"] = crossover(
            df["close"], df["pivot_high"].shift(right_bars + 1)
        ) & (df["open"] - df["low"] > df["close"] - df["open"])
        df["bear_wick"] = crossunder(
            df["close"], df["pivot_low"].shift(right_bars + 1)
        ) & (df["open"] - df["close"] < df["high"] - df["open"])

    # Tính toán các điều kiện cảnh báo
    df["alert_support_broken"] = crossunder(
        df["close"], df["pivot_low"].shift(right_bars + 1)
    ) & (df["osc"] > volume_thresh)
    df["alert_resistance_broken"] = crossover(
        df["close"], df["pivot_high"].shift(right_bars + 1)
    ) & (df["osc"] > volume_thresh)

    return df


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import OHLCV
from atklip.controls.candle import (
    JAPAN_CANDLE,
    HEIKINASHI,
    SMOOTH_CANDLE,
    N_SMOOTH_CANDLE,
)
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal, QObject


class SuperTrendWithStopLoss(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()
    sig_add_historic = Signal(int)

    def __init__(self, _candles, dict_ta_params) -> None:
        super().__init__(parent=None)

        self._candles: JAPAN_CANDLE | HEIKINASHI | SMOOTH_CANDLE | N_SMOOTH_CANDLE = (
            _candles
        )

        self.supertrend_length = dict_ta_params.get("supertrend_length", 14)
        self.supertrend_atr_length = dict_ta_params.get("supertrend_atr_length", 14)
        self.supertrend_multiplier = dict_ta_params.get("supertrend_multiplier", 3)
        self.supertrend_atr_mamode = dict_ta_params.get("supertrend_atr_mamode", "rma")

        self.atr_length = dict_ta_params.get("atr_length", 14)
        self.atr_mamode = dict_ta_params.get("atr_mamode", "rma")
        self.atr_multiplier = dict_ta_params.get("atr_multiplier", 1.5)

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"SuperTrendWithStopLoss"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

        self.xdata, self.long_stoploss, self.short_stoploss, self.SUPERTd = (
            np.array([]),
            np.array([]),
            np.array([]),
            np.array([]),
        )

        self.connect_signals()

    @property
    def is_current_update(self) -> bool:
        return self._is_current_update

    @is_current_update.setter
    def is_current_update(self, _is_current_update):
        self._is_current_update = _is_current_update

    @property
    def source_name(self) -> str:
        return self._source_name

    @source_name.setter
    def source_name(self, source_name):
        self._source_name = source_name

    def change_input(self, candles=None, dict_ta_params: dict = {}):
        if candles != None:
            self.disconnect_signals()
            self._candles: (
                JAPAN_CANDLE | HEIKINASHI | SMOOTH_CANDLE | N_SMOOTH_CANDLE
            ) = candles
            self.connect_signals()

        if dict_ta_params != {}:
            self.supertrend_length = dict_ta_params.get("supertrend_length", 7)
            self.supertrend_atr_length = dict_ta_params.get("supertrend_atr_length", 7)
            self.supertrend_multiplier = dict_ta_params.get("supertrend_multiplier", 3)
            self.supertrend_atr_mamode = dict_ta_params.get(
                "supertrend_atr_mamode", "rma"
            )

            self.atr_length = dict_ta_params.get("atr_length", 14)
            self.atr_mamode = dict_ta_params.get("atr_mamode", "rma")
            self.atr_multiplier = dict_ta_params.get("atr_multiplier", 1)

            ta_name: str = dict_ta_params.get("ta_name")
            obj_id: str = dict_ta_params.get("obj_id")

            ta_param = f"{obj_id}-{ta_name}-{self.atr_length}-{self.atr_mamode}-{self.atr_multiplier}"

            self._name = ta_param

        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False

        self.first_gen_data()

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
        self._candles.sig_add_historic.connect(self.add_historic_worker)
        self._candles.signal_delete.connect(self.signal_delete)

    def change_source(
        self, _candles: JAPAN_CANDLE | HEIKINASHI | SMOOTH_CANDLE | N_SMOOTH_CANDLE
    ):
        self.disconnect_signals()
        self._candles = _candles
        self.connect_signals()
        self.started_worker()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, _name):
        self._name = _name

    def get_df(self, n: int = None):
        if not n:
            return self.df
        return self.df.tail(n)

    def get_data(self, start: int = 0, stop: int = 0):
        if len(self.xdata) == 0:
            return [], [], [], []
        if start == 0 and stop == 0:
            x_data = self.xdata
            long_stoploss, short_stoploss, SUPERTd = (
                self.long_stoploss,
                self.short_stoploss,
                self.SUPERTd,
            )
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            long_stoploss, short_stoploss, SUPERTd = (
                self.long_stoploss[:stop],
                self.short_stoploss[:stop],
                self.SUPERTd[:stop],
            )
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            long_stoploss, short_stoploss, SUPERTd = (
                self.long_stoploss[start:],
                self.short_stoploss[start:],
                self.SUPERTd[start:],
            )
        else:
            x_data = self.xdata[start:stop]
            long_stoploss, short_stoploss, SUPERTd = (
                self.long_stoploss[start:stop],
                self.short_stoploss[start:stop],
                self.SUPERTd[start:stop],
            )
        return x_data, long_stoploss, short_stoploss, SUPERTd

    def get_last_row_df(self):
        return self.df.iloc[-1]

    def update_worker(self, candle):
        self.worker.submit(self.update, candle)

    def add_worker(self, candle):
        self.worker.submit(self.add, candle)

    def add_historic_worker(self, n):
        self.worker.submit(self.add_historic, n)

    def started_worker(self):
        self.worker.submit(self.first_gen_data)

    def paire_data(self, INDICATOR: pd.DataFrame):
        try:
            long_stoploss = INDICATOR["long_stoploss"].dropna().round(6)
            short_stoploss = INDICATOR["short_stoploss"].dropna().round(6)
            SUPERTd = INDICATOR["SUPERTd"].dropna()
            return long_stoploss, short_stoploss, SUPERTd
        except:
            return pd.Series([]), pd.Series([]), pd.Series([])

    @staticmethod
    def calculate(
        df: pd.DataFrame,
        left_bars: int = 15,
        right_bars: int = 15,
        volume_thresh: int = 20,
    ):
        df = df.copy()
        _index = df["index"]
        df = df.reset_index(drop=True)

        INDICATOR = support_resistance_with_breaks(
            df, left_bars=left_bars, right_bars=right_bars, volume_thresh=volume_thresh
        )

        long_stoploss = INDICATOR["long_stoploss"].dropna().round(6)
        short_stoploss = INDICATOR["short_stoploss"].dropna().round(6)
        SUPERTd = INDICATOR["SUPERTd"].dropna()

        _len = min([len(long_stoploss), len(short_stoploss), len(SUPERTd)])

        return pd.DataFrame(
            {
                "index": _index.tail(_len),
                "long_stoploss": long_stoploss.tail(_len),
                "short_stoploss": short_stoploss.tail(_len),
                "SUPERTd": SUPERTd.tail(_len),
            }
        )

    def first_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df: pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(
            self.calculate,
            self.callback_first_gen,
            df,
            self.supertrend_length,
            self.supertrend_atr_length,
            self.supertrend_multiplier,
            self.supertrend_atr_mamode,
            self.atr_length,
            self.atr_mamode,
            self.atr_multiplier,
        )
        process.start()

    def add_historic(self, n: int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        candle_df = self._candles.get_df()
        df: pd.DataFrame = candle_df.head(-_pre_len)

        process = HeavyProcess(
            self.calculate,
            self.callback_gen_historic_data,
            df,
            self.supertrend_length,
            self.supertrend_atr_length,
            self.supertrend_multiplier,
            self.supertrend_atr_mamode,
            self.atr_length,
            self.atr_mamode,
            self.atr_multiplier,
        )
        process.start()

    def add(self, new_candles: List[OHLCV]):
        new_candle: OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df: pd.DataFrame = self._candles.get_df(
                self.supertrend_length
                + self.atr_length
                + self.supertrend_atr_length
                + 10
            )
            process = HeavyProcess(
                self.calculate,
                self.callback_add,
                df,
                self.supertrend_length,
                self.supertrend_atr_length,
                self.supertrend_multiplier,
                self.supertrend_atr_mamode,
                self.atr_length,
                self.atr_mamode,
                self.atr_multiplier,
            )
            process.start()
        else:
            pass
            # self.is_current_update = True

    def update(self, new_candles: List[OHLCV]):
        new_candle: OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df: pd.DataFrame = self._candles.get_df(
                self.supertrend_length
                + self.atr_length
                + self.supertrend_atr_length
                + 10
            )
            process = HeavyProcess(
                self.calculate,
                self.callback_update,
                df,
                self.supertrend_length,
                self.supertrend_atr_length,
                self.supertrend_multiplier,
                self.supertrend_atr_mamode,
                self.atr_length,
                self.atr_mamode,
                self.atr_multiplier,
            )
            process.start()
        else:
            pass
            # self.is_current_update = True

    def callback_first_gen(self, future: Future):
        self.df = future.result()

        self.xdata, self.long_stoploss, self.short_stoploss, self.SUPERTd = (
            self.df["index"].to_numpy(),
            self.df["long_stoploss"].to_numpy(),
            self.df["short_stoploss"].to_numpy(),
            self.df["SUPERTd"].to_numpy(),
        )
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        # self.is_current_update = True
        self.sig_reset_all.emit()

    def callback_gen_historic_data(self, future: Future):
        _df = future.result()
        _len = len(_df)

        self.df = pd.concat([_df, self.df], ignore_index=True)

        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata))
        self.long_stoploss = np.concatenate(
            (_df["long_stoploss"].to_numpy(), self.long_stoploss)
        )
        self.short_stoploss = np.concatenate(
            (_df["short_stoploss"].to_numpy(), self.short_stoploss)
        )
        self.SUPERTd = np.concatenate((_df["SUPERTd"].to_numpy(), self.SUPERTd))

        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)

    def callback_add(self, future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_long_stoploss = df["long_stoploss"].iloc[-1]
        last_short_stoploss = df["short_stoploss"].iloc[-1]
        last_SUPERTd = df["SUPERTd"].iloc[-1]

        new_frame = pd.DataFrame(
            {
                "index": [last_index],
                "long_stoploss": [last_long_stoploss],
                "short_stoploss": [last_short_stoploss],
                "SUPERTd": [last_SUPERTd],
            }
        )

        self.df = pd.concat([self.df, new_frame], ignore_index=True)

        self.xdata = np.concatenate((self.xdata, np.array([last_index])))
        self.long_stoploss = np.concatenate(
            (self.long_stoploss, np.array([last_long_stoploss]))
        )
        self.short_stoploss = np.concatenate(
            (self.short_stoploss, np.array([last_short_stoploss]))
        )
        self.SUPERTd = np.concatenate((self.SUPERTd, np.array([last_SUPERTd])))

        self.sig_add_candle.emit()
        # self.is_current_update = True

    def callback_update(self, future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_long_stoploss = df["long_stoploss"].iloc[-1]
        last_short_stoploss = df["short_stoploss"].iloc[-1]
        last_SUPERTd = df["SUPERTd"].iloc[-1]

        self.df.iloc[-1] = [
            last_index,
            last_long_stoploss,
            last_short_stoploss,
            last_SUPERTd,
        ]
        (
            self.xdata[-1],
            self.long_stoploss[-1],
            self.short_stoploss[-1],
            self.SUPERTd[-1],
        ) = (last_index, last_long_stoploss, last_short_stoploss, last_SUPERTd)
        self.sig_update_candle.emit()
        # self.is_current_update = True
