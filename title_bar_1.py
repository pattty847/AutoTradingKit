def count_significant_decimals(number):
    # Chuyển số thành chuỗi
    str_number = str(number)
    
    # Kiểm tra xem có dấu chấm không
    if '.' not in str_number:
        return 0  # Không có phần thập phân
    
    # Tách phần nguyên và phần thập phân
    integer_part, decimal_part = str_number.split('.')
    
    # Loại bỏ các số 0 ở cuối phần thập phân
    decimal_part = decimal_part.rstrip('0')
    
    # Đếm số lượng chữ số có nghĩa
    return len(decimal_part)

# Ví dụ sử dụng
numbers = [3.1400, 0.0025, 123.456, 7.0, 0.0000000001, 100.0010, 1e-02]


from decimal import Decimal

def count_decimal_places(number):
    decimal_part = Decimal(str(number)).normalize()  # Chuẩn hóa số
    return abs(decimal_part.as_tuple().exponent)  # Lấy số chữ số thập phân

for num in numbers:
    print(f"Số {num} có {count_decimal_places(num)} số thập phân có nghĩa.")