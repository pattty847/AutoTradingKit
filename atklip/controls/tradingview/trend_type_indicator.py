import pandas as pd
import numpy as np
import pandas_ta as ta

# Sample OHLC data
data = pd.DataFrame({
    "high": np.random.random(500) * 100,
    "low": np.random.random(500) * 100,
    "close": np.random.random(500) * 100,
    "open": np.random.random(500) * 100,
    "volume": np.random.randint(100, 1000, size=500)
})

# Input Parameters
useAtr = True
atrLen = 14
atrMaType = "SMA"  # Options: "SMA", "EMA"
atrMaLen = 20
useAdx = True
adxLen = 14
diLen = 14
adxLim = 25
smooth = 3
lag = 8

# === ATR Calculations ===
data['atr'] = ta.atr(data['high'], data['low'], data['close'], length=atrLen)
if atrMaType == "SMA":
    data['atrMa'] = ta.sma(data['atr'], length=atrMaLen)
else:
    data['atrMa'] = ta.ema(data['atr'], length=atrMaLen)

# === ADX and Directional Indicators ===
data['plus_dm'] = np.where(data['high'].diff() > data['low'].diff(), data['high'].diff(), 0)
data['minus_dm'] = np.where(data['low'].diff() > data['high'].diff(), -data['low'].diff(), 0)
data['plus_di'] = 100 * ta.rma(data['plus_dm'], diLen) / ta.rma(ta.true_range(data['high'], data['low'], data['close']), diLen)
data['minus_di'] = 100 * ta.rma(data['minus_dm'], diLen) / ta.rma(ta.true_range(data['high'], data['low'], data['close']), diLen)

data['adx'] = 100 * ta.rma(np.abs(data['plus_di'] - data['minus_di']) /
                           (data['plus_di'] + data['minus_di']).replace(0, 1), adxLen)

# === Trend Type Conditions ===
data['cnd_na'] = data[['atr', 'adx', 'plus_di', 'minus_di', 'atrMa']].isna().any(axis=1)

data['cnd_sideways_atr'] = (useAtr & (data['atr'] <= data['atrMa']))
data['cnd_sideways_adx'] = (useAdx & (data['adx'] <= adxLim))
data['cnd_sideways'] = data['cnd_sideways_atr'] | data['cnd_sideways_adx']

data['cnd_up'] = data['plus_di'] > data['minus_di']
data['cnd_down'] = data['minus_di'] >= data['plus_di']

# === Trend Type and Smoothing ===
data['trend_type'] = np.where(data['cnd_na'], np.nan,
                              np.where(data['cnd_sideways'], 0,
                                       np.where(data['cnd_up'], 2, -2)))

data['smooth_type'] = (ta.sma(data['trend_type'], length=smooth) / 2).round() * 2

# Offset smooth type for lag
data['smooth_type_lagged'] = data['smooth_type'].shift(lag)

# === Output Data ===
trend_summary = data[['trend_type', 'smooth_type', 'smooth_type_lagged']].dropna()

print("Trend Summary:")
print(trend_summary.head(10))
