import pandas as pd
import numpy as np
import pandas_ta as ta  # Hoặc sử dụng `from talib import ATR, EMA` nếu có TA-Lib

# Giả định có dữ liệu OHLCV
# Dữ liệu mẫu giả định này phải thay bằng dữ liệu thực tế khi sử dụng chiến lược
data = {
    'open': np.random.uniform(100, 200, 100),
    'high': np.random.uniform(150, 250, 100),
    'low': np.random.uniform(50, 100, 100),
    'close': np.random.uniform(100, 200, 100),
    'volume': np.random.randint(1000, 5000, 100),
}
df = pd.DataFrame(data)

# Tham số đầu vào của chiến lược
a = 1  # Key Value - Độ nhạy của chiến lược
c = 10  # ATR Period
start_date = "2018-01-01"
end_date = "2069-12-31"

# Tính ATR và đặt các điều kiện
df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=c)
df['nLoss'] = a * df['atr']

# Tính toán giá trị trailing stop dựa trên ATR
df['xATRTrailingStop'] = np.nan
for i in range(1, len(df)):
    prev_stop = df['xATRTrailingStop'].iloc[i - 1] if i > 0 else 0
    src = df['close'].iloc[i]
    src_prev = df['close'].iloc[i - 1]

    if src > prev_stop and src_prev > prev_stop:
        df['xATRTrailingStop'].iloc[i] = max(prev_stop, src - df['nLoss'].iloc[i])
    elif src < prev_stop and src_prev < prev_stop:
        df['xATRTrailingStop'].iloc[i] = min(prev_stop, src + df['nLoss'].iloc[i])
    else:
        df['xATRTrailingStop'].iloc[i] = src - df['nLoss'].iloc[i] if src > prev_stop else src + df['nLoss'].iloc[i]

# Tính EMA và điều kiện cho các tín hiệu
df['ema'] = ta.ema(df['close'], length=1)
df['above'] = (df['ema'] > df['xATRTrailingStop']) & (df['ema'].shift(1) <= df['xATRTrailingStop'].shift(1))
df['below'] = (df['xATRTrailingStop'] > df['ema']) & (df['xATRTrailingStop'].shift(1) <= df['ema'].shift(1))

# Biến để xác định xu hướng
df['position'] = 0
df['position'] = np.where((df['close'] > df['xATRTrailingStop']) & df['above'], 1, df['position'])
df['position'] = np.where((df['close'] < df['xATRTrailingStop']) & df['below'], -1, df['position'])
df['position'] = df['position'].ffill().fillna(0)

# Thực hiện lệnh mua và thoát lệnh
df['buy_signal'] = (df['position'] == 1) & (df['position'].shift(1) != 1)
df['sell_signal'] = (df['position'] == -1) & (df['position'].shift(1) != -1)

# Áp dụng bộ lọc thời gian
df = df[(df.index >= start_date) & (df.index <= end_date)]

# Kết quả tín hiệu giao dịch
df['trade'] = np.where(df['buy_signal'], "Buy", np.where(df['sell_signal'], "Sell", "Hold"))

# In ra các tín hiệu giao dịch
print(df[['close', 'atr', 'xATRTrailingStop', 'ema', 'buy_signal', 'sell_signal', 'trade']])
