import numpy as np
import talib
import time,datetime
close = np.random.random(1000000)

t1 = time.time()
output = talib.SMA(close)
t2= time.time()

print(f"Thời gian xử lý: {t1 - t2} giây", len(close))