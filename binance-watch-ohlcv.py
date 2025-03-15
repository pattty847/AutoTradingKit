# -*- coding: utf-8 -*-

import os
import sys
# -----------------------------------------------------------------------------
import asyncio
import winloop
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    try:
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        winloop.install()
    except:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -----------------------------------------------------------------------------
import ccxt  # noqa: E402
# -----------------------------------------------------------------------------
binance = ccxt.binanceusdm({
    'apiKey': '',
    'secret': '',
})
symbol = 'BTC/USDT'
timeframe = '1m'
# each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
index = 4  # use close price from each ohlcv candle
height = 15
length = 80
import polars as pl
import pandas as pd
from atklip.controls.jesse.indicators.support_resistance_with_break import *
from atklip.controls.tradingview.support_resistance import calculate_support_resistance,support_resistance_with_breaks

def print_chart(exchange, symbol, timeframe):

    # get a list of ohlcv candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1500)

    df_pandas = pd.DataFrame(ohlcv, columns=["time", "open", "high", "low", "close", "volume"])

    print(df_pandas)

    # s_r = calculate_support_resistance(df_pandas)
    # print(s_r.loc[s_r['break_support'] | s_r['break_resistance']| s_r['bull_wick'] | s_r['bear_wick']|s_r['alert_support_broken']|s_r['alert_resistance_broken']])
    
    s_r_with_breaks = support_resistance_with_breaks(df_pandas)
    _df = s_r_with_breaks.loc[s_r_with_breaks['break_down'] | s_r_with_breaks['break_up'] | 
                               s_r_with_breaks['bull_wick'] | s_r_with_breaks['bear_wick']|
                               s_r_with_breaks['alert_support_broken'] | s_r_with_breaks['alert_resistance_broken']]
    print(_df[["high_pivot", "low_pivot"]])
    
last = print_chart(binance, symbol, timeframe)