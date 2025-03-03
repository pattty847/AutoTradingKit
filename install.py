import platform
import subprocess
import sys

# Danh sách các thư viện cần cài đặt
libraries = [
    "PySide6",
    "PySide6-stubs",
    "PySideSix-Frameless-Window",
    "darkdetect",
    "colorthief",
    "scipy",
    "pillow",
    "qasync",
    "numpy",
    "pyqtgraph",
    "pandas",
    "numba",
    "ccxt",
    "PyOpenGL",
    "cython",
    "pandas-datareader",
    "pyarrow",
    "arrow",
    "setuptools",
    "python-rapidjson",
    "humanize",
    "websockets",
    "psygnal",
    "click",
]

def install(package):
    """Hàm cài đặt thư viện sử dụng pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    # Xác định hệ điều hành
    system = platform.system().lower()

    print(f"Đang chạy trên hệ điều hành: {system.capitalize()}")

    # Cài đặt các thư viện chung
    print("Đang cài đặt các thư viện chung...")
    for lib in libraries:
        try:
            print(f"Đang cài đặt {lib}...")
            install(lib)
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi cài đặt {lib}: {e}")

    # Cài đặt thư viện riêng cho từng hệ điều hành
    if system == "windows":
        print("Đang cài đặt winloop cho Windows...")
        install("winloop")
    elif system == "linux" or system == "darwin":  # 'darwin' là tên hệ điều hành của macOS
        print("Đang cài đặt uvloop cho Linux/macOS...")
        install("uvloop")
    else:
        print(f"Hệ điều hành {system} không được hỗ trợ cho các thư viện riêng biệt.")

    print("Cài đặt hoàn tất!")

if __name__ == "__main__":
    main()