import numpy as np
import pandas as pd
import pandas_ta as ta

# Inputs
a = 1  # Key Value, this changes sensitivity
c = 10  # ATR Period
h = False  # Use Heikin Ashi Candles
BandType = "Bollinger Bands"  # Channel Type
ChannelLength = 20
StdDev = 1
pvtLen = 2
Pd = 22  # ATR Period for trailing stop
Mult = 1  # ATR Multiplier
wicks = False

# Sample OHLC Data (replace with real data)
data = pd.DataFrame({
    "open": np.random.random(100),
    "high": np.random.random(100),
    "low": np.random.random(100),
    "close": np.random.random(100)
})

# Ensure consistent Heikin Ashi Data if required
if h:
    ha_data = ta.heikinashi(data)
    src = ha_data["HA_close"]
else:
    src = data["close"]

# ATR Calculation
xATR = ta.atr(data["high"], data["low"], data["close"], length=c)
nLoss = a * xATR

# ATR Trailing Stop
xATRTrailingStop = np.zeros(len(data))
for i in range(1, len(data)):
    if src[i] > xATRTrailingStop[i - 1] and src[i - 1] > xATRTrailingStop[i - 1]:
        xATRTrailingStop[i] = max(xATRTrailingStop[i - 1], src[i] - nLoss[i])
    elif src[i] < xATRTrailingStop[i - 1] and src[i - 1] < xATRTrailingStop[i - 1]:
        xATRTrailingStop[i] = min(xATRTrailingStop[i - 1], src[i] + nLoss[i])
    else:
        xATRTrailingStop[i] = src[i] - nLoss[i] if src[i] > xATRTrailingStop[i - 1] else src[i] + nLoss[i]

# EMA for crossover logic
ema = ta.ema(src, length=1)

above = (ema > xATRTrailingStop).astype(int).diff() > 0
below = (xATRTrailingStop > ema).astype(int).diff() > 0

# Pivot Points Calculation
# def calculate_pivots(data, length):
#     pivot_highs = data["high"].rolling(window=2 * length + 1, center=True).apply(lambda x: x[length] if x[length] == x.max() else np.nan)
#     pivot_lows = data["low"].rolling(window=2 * length + 1, center=True).apply(lambda x: x[length] if x[length] == x.min() else np.nan)
#     return pivot_highs, pivot_lows

# pivot_highs, pivot_lows = calculate_pivots(data, pvtLen)

# Bands Calculation
def calculate_bands(data, band_type, length, std_dev):
    if band_type == "Bollinger Bands":
        bb = ta.bbands(data["close"], length=length, std=std_dev)
        print(bb)
        return bb["BBL_20_1"], bb["BBM_20_1"], bb["BBU_20_1"]
    elif band_type == "Keltner Channel":
        kc = ta.kc(data, length=length)
        return kc["KCL_20"], kc["KCM_20"], kc["KCU_20"]
    elif band_type == "Donchian Channel":
        dc_high = data["high"].rolling(window=length).max()
        dc_low = data["low"].rolling(window=length).min()
        return dc_low, (dc_high + dc_low) / 2, dc_high
    else:
        return None, None, None

lower_band, middle_band, upper_band = calculate_bands(data, BandType, ChannelLength, StdDev)

# Trailing Stop Calculation
def calculate_trailing_stop(data, lower, upper, atr, mult, wicks):
    dir = np.ones(len(data))
    long_stop = lower - atr * mult
    short_stop = upper + atr * mult

    for i in range(1, len(data)):
        if dir[i - 1] == 1 and data["low"][i] < long_stop[i - 1]:
            dir[i] = -1
        elif dir[i - 1] == -1 and data["high"][i] > short_stop[i - 1]:
            dir[i] = 1
        else:
            dir[i] = dir[i - 1]

    return dir, long_stop, short_stop

barState, buyStop, sellStop = calculate_trailing_stop(data, lower_band, upper_band, xATR, Mult, wicks)

# Trade Conditions
buy_condition = (src > xATRTrailingStop) & above & (barState == 1)
sell_condition = (src < xATRTrailingStop) & below & (barState == -1)

# Output Results
data["Buy Signal"] = buy_condition
data["Sell Signal"] = sell_condition
data["Trailing Stop"] = np.where(barState == 1, buyStop, sellStop)

print(data[["Buy Signal", "Sell Signal", "Trailing Stop"]])
