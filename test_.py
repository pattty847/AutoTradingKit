import pandas as pd
import numpy as np

# Giả định có dữ liệu OHLC trong một DataFrame
data = {
    'open': np.random.uniform(100, 200, 100),
    'high': np.random.uniform(150, 250, 100),
    'low': np.random.uniform(50, 100, 100),
    'close': np.random.uniform(100, 200, 100)
}
df = pd.DataFrame(data)

# Tham số đầu vào
leftLenH = 10  # Pivot High Left Length
rightLenH = 10  # Pivot High Right Length
leftLenL = 10  # Pivot Low Left Length
rightLenL = 10  # Pivot Low Right Length

# Hàm tính toán pivot high
def pivot_high(df, left_len, right_len):
    pivots = []
    for i in range(left_len, len(df) - right_len):
        high_segment = df['high'].iloc[i - left_len:i + right_len + 1]
        if df['high'].iloc[i] == high_segment.max():
            pivots.append(df['high'].iloc[i])
        else:
            pivots.append(np.nan)
    return  pivots 

# Hàm tính toán pivot low
def pivot_low(df, left_len, right_len):
    pivots = []
    for i in range(left_len, len(df) - right_len):
        low_segment = df['low'].iloc[i - left_len:i + right_len + 1]
        if df['low'].iloc[i] == low_segment.min():
            pivots.append(df['low'].iloc[i])
        else:
            pivots.append(np.nan)
    return  pivots

# Tính toán Pivot High và Pivot Low
df['Pivot_High'] = [pivot_high(df, leftLenH, rightLenH)]
df['Pivot_Low'] = [pivot_low(df, leftLenL, rightLenL)]

# Kết quả
print(df[['high', 'Pivot_High', 'low', 'Pivot_Low']])
