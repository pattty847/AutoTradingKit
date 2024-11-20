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
length = 14
smoothing = "RMA"  # Options: ["RMA", "SMA", "EMA", "WMA"]
multiplier = 1.5
show_price_lines = True

# Chọn các nguồn giá cho tính toán (src1, src2)
src1 = df['high']
src2 = df['low']

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
        return ta.rma(source, length)  # Default to RMA nếu không có lựa chọn

# Tính toán ATR (Average True Range)
df['tr'] = ta.true_range(df['high'], df['low'], df['close'])
df['atr'] = ma_function(df['tr'], length, smoothing)

# Tính toán các giá trị cho stop loss
df['a'] = df['atr'] * multiplier
df['x'] = df['a'] + src1  # ATR Short Stop Loss
df['x2'] = src2 - df['a']  # ATR Long Stop Loss

# Hiển thị kết quả
print(df[['high', 'low', 'x', 'x2', 'a']])

# Tính toán giá trị ATR hiện tại, High stop loss, và Low stop loss nếu cần
current_atr = df['a'].iloc[-1]
current_high_stop_loss = df['x'].iloc[-1]
current_low_stop_loss = df['x2'].iloc[-1]

# In giá trị hiện tại
print(f"ATR: {current_atr}")
print(f"High Stop Loss: {current_high_stop_loss}")
print(f"Low Stop Loss: {current_low_stop_loss}")
