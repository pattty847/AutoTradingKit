import numpy as np

# Tạo một numpy array một chiều ban đầu
arr = np.array([1, 2, 3, 4, 5])
print("Original Array:", arr)

# Thêm một phần tử mới vào numpy array
new_element = np.array([1, 2, 3, 4, 5])
arr = np.append(arr, new_element)
print("Array after adding new element:", arr)

# Cập nhật phần tử cuối cùng
arr[-1] = 10  # Gán giá trị mới cho phần tử cuối cùng
print("Array after updating the last element:", arr)
