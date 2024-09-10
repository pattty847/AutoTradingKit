import numpy as np
from atklip.indicators import talib as ta
import time,datetime
close = np.random.random(1000000)

t1 = time.time()
output = ta.SMA(close)
t2= time.time()

print(f"Thời gian xử lý: {t1 - t2} giây", len(close))


import pandas as pd

# Tạo một pandas Series mà không có chỉ mục
s = pd.Series([10, 20, 30])

# Thêm một giá trị mới vào cuối
s = pd.concat([s, pd.Series([40], index=[len(s)])])

print(s)
