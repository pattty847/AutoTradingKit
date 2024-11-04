import pandas as pd
import numpy as np

# Tạo DataFrame với dữ liệu OHLC (thay thế bằng dữ liệu thực tế của bạn)
df = pd.DataFrame({
    'open': np.random.uniform(100, 110, 100),
    'high': np.random.uniform(110, 120, 100),
    'low': np.random.uniform(90, 100, 100),
    'close': np.random.uniform(100, 110, 100)
})

# Tính toán các mẫu nến
doji_size = 0.05
df['doji'] = (abs(df['open'] - df['close']) <= (df['high'] - df['low']) * doji_size)

df['evening_star'] = (df['close'].shift(2) > df['open'].shift(2)) & \
                     (np.minimum(df['open'].shift(1), df['close'].shift(1)) > df['close'].shift(2)) & \
                     (df['open'] < np.minimum(df['open'].shift(1), df['close'].shift(1))) & \
                     (df['close'] < df['open'])

df['morning_star'] = (df['close'].shift(2) < df['open'].shift(2)) & \
                     (np.maximum(df['open'].shift(1), df['close'].shift(1)) < df['close'].shift(2)) & \
                     (df['open'] > np.maximum(df['open'].shift(1), df['close'].shift(1))) & \
                     (df['close'] > df['open'])

df['shooting_star'] = (df['open'].shift(1) < df['close'].shift(1)) & \
                      (df['open'] > df['close'].shift(1)) & \
                      ((df['high'] - np.maximum(df['open'], df['close'])) >= abs(df['open'] - df['close']) * 3) & \
                      ((np.minimum(df['close'], df['open']) - df['low']) <= abs(df['open'] - df['close']))

df['hammer'] = ((df['high'] - df['low']) > 3 * abs(df['open'] - df['close'])) & \
               (((df['close'] - df['low']) / (0.001 + df['high'] - df['low'])) > 0.6) & \
               (((df['open'] - df['low']) / (0.001 + df['high'] - df['low'])) > 0.6)

df['inverted_hammer'] = ((df['high'] - df['low']) > 3 * abs(df['open'] - df['close'])) & \
                        (((df['high'] - df['close']) / (0.001 + df['high'] - df['low'])) > 0.6) & \
                        (((df['high'] - df['open']) / (0.001 + df['high'] - df['low'])) > 0.6)

df['bearish_harami'] = (df['close'].shift(1) > df['open'].shift(1)) & \
                       (df['open'] > df['close']) & \
                       (df['open'] <= df['close'].shift(1)) & \
                       (df['open'].shift(1) <= df['close']) & \
                       (abs(df['open'] - df['close']) < abs(df['close'].shift(1) - df['open'].shift(1)))

df['bullish_harami'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                       (df['close'] > df['open']) & \
                       (df['close'] <= df['open'].shift(1)) & \
                       (df['close'].shift(1) <= df['open']) & \
                       (abs(df['close'] - df['open']) < abs(df['open'].shift(1) - df['close'].shift(1)))

df['bearish_engulfing'] = (df['close'].shift(1) > df['open'].shift(1)) & \
                          (df['open'] > df['close']) & \
                          (df['open'] >= df['close'].shift(1)) & \
                          (df['close'] <= df['open'].shift(1)) & \
                          (abs(df['open'] - df['close']) > abs(df['close'].shift(1) - df['open'].shift(1)))

df['bullish_engulfing'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                          (df['close'] > df['open']) & \
                          (df['close'] >= df['open'].shift(1)) & \
                          (df['open'] <= df['close'].shift(1)) & \
                          (abs(df['close'] - df['open']) > abs(df['open'].shift(1) - df['close'].shift(1)))

df['piercing_line'] = (df['close'].shift(1) < df['open'].shift(1)) & \
                      (df['open'] < df['low'].shift(1)) & \
                      (df['close'] > (df['close'].shift(1) + (df['open'].shift(1) - df['close'].shift(1)) / 2)) & \
                      (df['close'] < df['open'].shift(1))

df['bullish_belt'] = (df['low'] == df['open']) & \
                     (df['open'] < df['low'].rolling(10).min().shift(1)) & \
                     (df['close'] > ((df['high'].shift(1) - df['low'].shift(1)) / 2) + df['low'].shift(1))

df['bullish_kicker'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                       (df['open'] >= df['open'].shift(1)) & \
                       (df['close'] > df['open'])

df['bearish_kicker'] = (df['open'].shift(1) < df['close'].shift(1)) & \
                       (df['open'] <= df['open'].shift(1)) & \
                       (df['close'] <= df['open'])

df['hanging_man'] = ((df['high'] - df['low']) > 4 * abs(df['open'] - df['close'])) & \
                    (((df['close'] - df['low']) / (0.001 + df['high'] - df['low'])) >= 0.75) & \
                    (((df['open'] - df['low']) / (0.001 + df['high'] - df['low'])) >= 0.75) & \
                    (df['high'].shift(1) < df['open']) & \
                    (df['high'].shift(2) < df['open'])

df['dark_cloud_cover'] = (df['close'].shift(1) > df['open'].shift(1)) & \
                         (((df['close'].shift(1) + df['open'].shift(1)) / 2) > df['close']) & \
                         (df['open'] > df['close']) & \
                         (df['open'] > df['close'].shift(1)) & \
                         (df['close'] > df['open'].shift(1)) & \
                         ((df['open'] - df['close']) / (0.001 + (df['high'] - df['low'])) > 0.6)

# Các mẫu nến khác có thể được bổ sung tương tự theo mã Pine Script gốc.

# In kết quả kiểm tra mẫu nến
patterns = ['doji', 'evening_star', 'morning_star', 'shooting_star', 'hammer', 'inverted_hammer', 'bearish_harami', 
            'bullish_harami', 'bearish_engulfing', 'bullish_engulfing', 'piercing_line', 'bullish_belt', 
            'bullish_kicker', 'bearish_kicker', 'hanging_man', 'dark_cloud_cover']

# In ra các mẫu nến được phát hiện
print(df[patterns].tail())
