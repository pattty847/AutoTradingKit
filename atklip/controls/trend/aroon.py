# -*- coding: utf-8 -*-
from concurrent.futures import Future
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta import aroon
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


class Aroon(QObject):
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

        self.length: int = dict_ta_params.get("length", 14)
        self.scalar: int = dict_ta_params.get("scalar", 100)

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"Aroon {self.length}-{self.scalar}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

        self.xdata, self.aroon_up, self.aroon_down = (
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
            self.length: int = dict_ta_params.get("length", 14)
            self.scalar: int = dict_ta_params.get("scalar", 100)

            ta_name: str = dict_ta_params.get("ta_name")
            obj_id: str = dict_ta_params.get("obj_id")

            ta_param = f"{obj_id}-{ta_name}-{self.length}-{self.scalar}"

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
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker)

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
            return [], [], []
        if start == 0 and stop == 0:
            x_data = self.xdata
            aroon_up, aroon_down = self.aroon_up, self.aroon_down
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            aroon_up, aroon_down = self.aroon_up[:stop], self.aroon_down[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            aroon_up, aroon_down = self.aroon_up[start:], self.aroon_down[start:]
        else:
            x_data = self.xdata[start:stop]
            aroon_up, aroon_down = (
                self.aroon_up[start:stop],
                self.aroon_down[start:stop],
            )
        return x_data, aroon_up, aroon_down

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

    @staticmethod
    def calculate(df: pd.DataFrame, length, scalar):
        df = df.copy()
        df = df.reset_index(drop=True)

        INDICATOR = (
            aroon(
                high=df["high"],
                low=df["low"],
                length=length,
                scalar=scalar,
            )
            .dropna()
            .round(6)
        )

        aroon_up_name = f"AROONU_{length}"
        aroon_down_name = f"AROOND_{length}"
        aroon_osc_name = f"AROONOSC_{length}"

        aroon_up = INDICATOR[aroon_up_name].dropna().round(6)
        aroon_down = INDICATOR[aroon_down_name].dropna().round(6)

        _len = min([len(aroon_up), len(aroon_down)])
        _index = df["index"].tail(_len)

        return pd.DataFrame(
            {
                "index": _index,
                "aroon_up": aroon_up.tail(_len),
                "aroon_down": aroon_down.tail(_len),
            }
        )

    def first_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df: pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(
            self.calculate, self.callback_first_gen, df, self.length, self.scalar
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
            self.length,
            self.scalar,
        )
        process.start()

    def add(self, new_candles: List[OHLCV]):
        new_candle: OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df: pd.DataFrame = self._candles.get_df((self.length + self.scalar) * 2)
            process = HeavyProcess(
                self.calculate, self.callback_add, df, self.length, self.scalar
            )
            process.start()
        else:
            pass
            # self.is_current_update = True

    def update(self, new_candles: List[OHLCV]):
        new_candle: OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df: pd.DataFrame = self._candles.get_df((self.length + self.scalar) * 2)
            process = HeavyProcess(
                self.calculate, self.callback_update, df, self.length, self.scalar
            )
            process.start()
        else:
            pass
            # self.is_current_update = True

    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata, self.aroon_up, self.aroon_down = (
            self.df["index"].to_numpy(),
            self.df["aroon_up"].to_numpy(),
            self.df["aroon_down"].to_numpy(),
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
        self.aroon_up = np.concatenate((_df["aroon_up"].to_numpy(), self.aroon_up))
        self.aroon_down = np.concatenate(
            (_df["aroon_down"].to_numpy(), self.aroon_down)
        )
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)

    def callback_add(self, future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_aroon_up = df["aroon_up"].iloc[-1]
        last_aroon_down = df["aroon_down"].iloc[-1]
        new_frame = pd.DataFrame(
            {
                "index": [last_index],
                "aroon_up": [last_aroon_up],
                "aroon_down": [last_aroon_down],
            }
        )
        self.df = pd.concat([self.df, new_frame], ignore_index=True)
        self.xdata = np.concatenate((self.xdata, np.array([last_index])))
        self.aroon_up = np.concatenate((self.aroon_up, np.array([last_aroon_up])))
        self.aroon_down = np.concatenate((self.aroon_down, np.array([last_aroon_down])))
        # self.is_current_update = True
        self.sig_add_candle.emit()

    def callback_update(self, future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_aroon_up = df["aroon_up"].iloc[-1]
        last_aroon_down = df["aroon_down"].iloc[-1]
        self.df.loc[self.df.index[-1], ["index", "aroon_up", "aroon_down"]] = [
            last_index,
            last_aroon_up,
            last_aroon_down,
        ]
        self.xdata[-1], self.aroon_up[-1], self.aroon_down[-1] = (
            last_index,
            last_aroon_up,
            last_aroon_down,
        )
        # self.is_current_update = True
        self.sig_update_candle.emit()
