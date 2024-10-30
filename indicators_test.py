"UT BOT --- Buy Sell Signal"

import numpy as np
import matplotlib.pyplot as plt

# Các thông số đầu vào
a = 1      # Key Value
c = 10     # ATR Period
h = False  # Dùng Heikin Ashi hay không

# Dữ liệu giả (thay thế bằng dữ liệu thực tế của bạn)
np.random.seed(0)
n = 100
close = np.random.rand(n) * 100 + 100  # Dữ liệu giá đóng cửa ngẫu nhiên

# Tính ATR
def atr(period, data):
    return np.convolve(np.abs(np.diff(data)), np.ones(period)/period, mode='valid')

xATR = atr(c, close)
nLoss = a * xATR

# Heikin Ashi hoặc giá đóng cửa thực tế
src = close if not h else np.cumsum(close)  # Giả sử Heikin Ashi là giá tăng dần

# Tính toán xATRTrailingStop
xATRTrailingStop = np.zeros(n)
for i in range(1, n):
    if src[i] > xATRTrailingStop[i-1] and src[i-1] > xATRTrailingStop[i-1]:
        xATRTrailingStop[i] = max(xATRTrailingStop[i-1], src[i] - nLoss[min(i-1, len(nLoss)-1)])
    elif src[i] < xATRTrailingStop[i-1] and src[i-1] < xATRTrailingStop[i-1]:
        xATRTrailingStop[i] = min(xATRTrailingStop[i-1], src[i] + nLoss[min(i-1, len(nLoss)-1)])
    else:
        xATRTrailingStop[i] = src[i] - nLoss[min(i-1, len(nLoss)-1)] if src[i] > xATRTrailingStop[i-1] else src[i] + nLoss[min(i-1, len(nLoss)-1)]

# Tính toán tín hiệu mua/bán
pos = np.zeros(n)
for i in range(1, n):
    if src[i-1] < xATRTrailingStop[i-1] and src[i] > xATRTrailingStop[i-1]:
        pos[i] = 1
    elif src[i-1] > xATRTrailingStop[i-1] and src[i] < xATRTrailingStop[i-1]:
        pos[i] = -1
    else:
        pos[i] = pos[i-1]

# Vẽ biểu đồ
plt.figure(figsize=(12, 6))
plt.plot(src, label="Price", color="blue")
plt.plot(xATRTrailingStop, label="ATR Trailing Stop", color="orange")

buy_signals = np.where(pos == 1)[0]
sell_signals = np.where(pos == -1)[0]

plt.scatter(buy_signals, src[buy_signals], marker="^", color="green", label="Buy Signal")
plt.scatter(sell_signals, src[sell_signals], marker="v", color="red", label="Sell Signal")

plt.legend()
plt.title("UT Bot Alerts in Python")
plt.show()
