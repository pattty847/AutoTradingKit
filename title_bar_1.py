import polars as pl
from datetime import datetime

# Dữ liệu nến của bạn
data = [
    [1740566160000, 89077.1, 89078.4, 89050.0, 89070.8, 25.042],
    [1740566220000, 89070.8, 89129.7, 89070.7, 89129.7, 75.091],
    [1740566280000, 89129.8, 89158.9, 89129.7, 89156.6, 80.99],
    [1740566340000, 89156.5, 89156.6, 89092.2, 89108.8, 94.683],
    [1740566400000, 89108.8, 89148.4, 89108.8, 89148.4, 27.478],
    [1740566460000, 89148.3, 89199.7, 89148.3, 89199.6, 85.693],
    [1740566520000, 89199.6, 89199.7, 89173.2, 89173.3, 53.001],
    [1740566580000, 89173.2, 89188.6, 89133.5, 89133.5, 43.83],
    [1740566640000, 89133.6, 89137.9, 89112.1, 89132.5, 32.275]
]

# Chuyển đổi timestamp sang datetime
data = [[datetime.fromtimestamp(row[0] / 1000)] + row[1:] for row in data]

# Tạo DataFrame
df = pl.DataFrame(
    data,
    schema=["datetime", "open", "high", "low", "close", "volume"]
)

# Hàm tính EMA
def calculate_ema(series: pl.Series, span: int) -> pl.Series:
    alpha = 2 / (span + 1)  # Tính alpha
    ema = series[0]  # Khởi tạo EMA đầu tiên bằng giá trị đầu tiên của series
    ema_values = [ema]  # Lưu trữ các giá trị EMA

    # Tính toán EMA cho các giá trị tiếp theo
    for value in series[1:]:
        ema = alpha * value + (1 - alpha) * ema
        ema_values.append(ema)

    return pl.Series(ema_values)

# Tính EMA với chu kỳ 5
ema_5 = calculate_ema(df["close"], 5)

# Thêm cột EMA vào DataFrame
df = df.with_columns(ema_5.alias("EMA_5"))

# In DataFrame với cột EMA
print(df)