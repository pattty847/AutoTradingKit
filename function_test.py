import numpy as np
# from atklip.indicators import talib as ta
import time,datetime
close = np.random.random(1000000)

# t1 = time.time()
# output = ta.SMA(close)
# t2= time.time()

# print(f"Thời gian xử lý: {t1 - t2} giây", len(close))


import pandas as pd
import polars as pl
# # Tạo một pandas Series mà không có chỉ mục
# s = pd.Series([10, 20, 30])

# # Thêm một giá trị mới vào cuối
# s = pd.concat([s, pd.Series([40], index=[len(s)])])

# print(s)

t1 = time.time()
new_df_ = pl.DataFrame({ "open": np.random.random(1000000),
                        "high": np.random.random(1000000),
                        "low": np.random.random(1000000)
                    })
df = new_df_.to_numpy()
t2= time.time()
print(f"Thời gian xử lý polar: {t1 - t2} giây")


t1 = time.time()
new_df = pd.DataFrame({ "open": np.random.random(1000000),
                        "high": np.random.random(1000000),
                        "low": np.random.random(1000000)
                    })
df = new_df.to_numpy()
t2= time.time()
print(f"Thời gian xử lý pandas: {t1 - t2} giây")

from atklip.controls import talib
from atklip.controls.talib import stream

close = np.random.random(100)

# the Function API
output = talib.SMA(close)

# the Streaming API
latest = stream.SMA(close,10)

# the latest value is the same as the last output value
print(latest)



