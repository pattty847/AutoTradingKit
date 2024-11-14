from datetime import datetime
from zoneinfo import ZoneInfo

# Lấy múi giờ địa phương từ hệ thống
local_timezone = datetime.now().astimezone().tzinfo
print("Local timezone:", local_timezone)

import time

# Lấy múi giờ địa phương (giờ lệch so với UTC)
timezone_offset = -time.timezone // 3600  # Đổi từ giây sang giờ
print("Timezone offset (hours):", timezone_offset)

# Lấy tên múi giờ địa phương
local_timezone_name = time.tzname
print("Local timezone name:", local_timezone_name)
