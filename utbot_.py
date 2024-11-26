import pandas as pd
import numpy as np
import pandas_ta as ta

# Tạo DataFrame mẫu với dữ liệu OHLC
# Giả định bạn có dữ liệu OHLC (Open, High, Low, Close) trong DataFrame
data = {
    'open': np.random.uniform(100, 200, 100),
    'high': np.random.uniform(150, 250, 100),
    'low': np.random.uniform(50, 100, 100),
    'close': np.random.uniform(100, 200, 100),
}
df = pd.DataFrame(data)

# Các tham số đầu vào
a = 15.0
length = 1
smoothing = "EMA"  # Options: ["RMA", "SMA", "EMA", "WMA"]
use_heikin_ashi = False
length_bb = 20
mult_bb = 2.0
length_kc = 400
mult_kc = 1.5
use_true_range = True

# Hàm chọn hàm MA (Moving Average) tương ứng
def ma_function(source, length, smoothing):
    if smoothing == "RMA":
        return ta.rma(source, length)
    elif smoothing == "SMA":
        return ta.sma(source, length)
    elif smoothing == "EMA":
        return ta.ema(source, length)
    elif smoothing == "WMA":
        return ta.wma(source, length)
    else:
        return ta.ema(source, length)  # Default to EMA if not specified

# Tính toán ATR (Average True Range)
df['tr'] = ta.true_range(df['high'], df['low'], df['close'])
df['xATR'] = ma_function(df['tr'], length, smoothing)

# Tính toán nLoss
df['nLoss'] = a * df['xATR']

# Tính toán Heikin Ashi nếu được chọn
df['ohlc4'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
df['haOpen'] = df['ohlc4'].shift(1).combine_first(df['ohlc4']).expanding().mean()
df['haC'] = (df['ohlc4'] + df['haOpen'] + df['high'].combine_first(df['haOpen']).expanding().max() +
             df['low'].combine_first(df['haOpen']).expanding().min()) / 4

# Chọn giá trị src
df['src'] = np.where(use_heikin_ashi, df['haC'], df['close'])

# Tính toán ATR Trailing Stop
df['xATRTrailingStop'] = 0.0
for i in range(1, len(df)):
    if df['src'][i] > df['xATRTrailingStop'][i-1] and df['src'][i-1] > df['xATRTrailingStop'][i-1]:
        df.at[i, 'xATRTrailingStop'] = max(df['xATRTrailingStop'][i-1], df['src'][i] - df['nLoss'][i])
    elif df['src'][i] < df['xATRTrailingStop'][i-1] and df['src'][i-1] < df['xATRTrailingStop'][i-1]:
        df.at[i, 'xATRTrailingStop'] = min(df['xATRTrailingStop'][i-1], df['src'][i] + df['nLoss'][i])
    elif df['src'][i] > df['xATRTrailingStop'][i-1]:
        df.at[i, 'xATRTrailingStop'] = df['src'][i] - df['nLoss'][i]
    else:
        df.at[i, 'xATRTrailingStop'] = df['src'][i] + df['nLoss'][i]

# Tính EMA
df['ema'] = ta.ema(df['src'], 1)

# Điều kiện Buy và Sell
df['above'] = df['ema'] > df['xATRTrailingStop']
df['below'] = df['ema'] < df['xATRTrailingStop']

df['buy'] = (df['src'] > df['xATRTrailingStop']) & df['above']
df['sell'] = (df['src'] < df['xATRTrailingStop']) & df['below']

# Tính toán BB (Bollinger Bands)
df['basis'] = ta.sma(df['close'], length_bb)
df['dev'] = mult_bb * ta.stdev(df['close'], length_bb)
df['upperBB'] = df['basis'] + df['dev']
df['lowerBB'] = df['basis'] - df['dev']

# Tính toán KC (Keltner Channel)
df['ma'] = ta.sma(df['close'], length_kc)
df['range'] = ta.true_range(df['high'], df['low'], df['close']) if use_true_range else (df['high'] - df['low'])
df['rangema'] = ta.sma(df['range'], length_kc)
df['upperKC'] = df['ma'] + df['rangema'] * mult_kc
df['lowerKC'] = df['ma'] - df['rangema'] * mult_kc

# Tính toán squeeze
df['sqzOn'] = (df['lowerBB'] > df['lowerKC']) & (df['upperBB'] < df['upperKC'])
df['sqzOff'] = (df['lowerBB'] < df['lowerKC']) & (df['upperBB'] > df['upperKC'])
df['noSqz'] = (~df['sqzOn']) & (~df['sqzOff'])

# Tính toán giá trị val
df['val'] = ta.linreg(df['close'] - (ta.highest(df['high'], length_kc) + ta.lowest(df['low'], length_kc) + ta.sma(df['close'], length_kc)) / 3, length_kc, 0)

# Điều kiện vào/ra lệnh dựa trên giá trị val và buy/sell conditions
df['buy_signal'] = df['buy'] & (df['val'] > 400) & (df['val'] < df['val'].shift(1))
df['sell_signal'] = df['sell'] & (df['val'] < -400) & (df['val'] > df['val'].shift(1))

# Kết quả
print(df[['close', 'xATRTrailingStop', 'buy_signal', 'sell_signal']])
