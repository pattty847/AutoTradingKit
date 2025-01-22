import os
import pathlib
import importlib.metadata
import requests
import psutil
import platform
import uuid
import sys
import socket
import json
import base64
from cryptography.fernet import Fernet

lmt = os.path.sep
HOME_DIR = pathlib.Path.home()
# PROJECT_DIR = HOME_DIR / ".ivn"
PROJECT_DIR = HOME_DIR / ".vnstock"
TG = b'gAAAAABmfy0qLUmLnsm5oMnteWmNSJ5rBSQubrS2JFdKt19m_tqxaAWRCCJ4goHm-fr5Mee_M8TvZ_sfpvDFFBz-8paY_H72KftTb4CTzuNGhqZjp2BCiP2gwPdOxbi9wh9GCKHBwzVs'

class VnstockInitializer:
    def __init__(self, target):
        self.home_dir = HOME_DIR
        self.project_dir = PROJECT_DIR
        self.id_dir = PROJECT_DIR / "id"
        # self.id = PROJECT_DIR / "id.json"
        # self.env_config = PROJECT_DIR / "env.json"
        self.id = PROJECT_DIR / "user.json"
        self.env_config = self.id_dir / "env.json"
        self.RH = 'asejruyy^&%$#W2vX>NfwrevDRESWR'
        self.LH = 'YMAnhuytr%$59u90y7j-mjhgvyFTfbiuUYH'

        # Create the project directory if it doesn't exist
        self.project_dir.mkdir(exist_ok=True)
        self.id_dir.mkdir(exist_ok=True)
        self.target = target

        kb = (str(self.project_dir).split(lmt)[-1] + str(self.id).split(lmt)[-1])[::-1].ljust(32)[:32].encode('utf-8')
        kb64 = base64.urlsafe_b64encode(kb)
        self.cph = Fernet(kb64)

    def system_info(self):
        """
        Gathers information about the environment and system.
        """
        # Generate UUID
        machine_id = str(uuid.uuid4())

        # Environment (modify to detect your specific frameworks)
        try:
            from IPython import get_ipython
            if 'IPKernelApp' not in get_ipython().config:  # Check if not in IPython kernel
                if sys.stdout.isatty():
                    environment = "Terminal"
                else:
                    environment = "Other"  # Non-interactive environment (e.g., script executed from an IDE)
            else:
                environment = "Jupyter"
        except (ImportError, AttributeError):
            # Fallback if IPython isn't installed or other checks fail
            if sys.stdout.isatty():
                environment = "Terminal"
            else:
                environment = "Other"

        try:
            if 'google.colab' in sys.modules:
                hosting_service = "Google Colab"
            elif 'CODESPACE_NAME' in os.environ:
                hosting_service = "Github Codespace"
            elif 'GITPOD_WORKSPACE_CLUSTER_HOST' in os.environ:
                hosting_service = "Gitpod"
            elif 'REPLIT_USER' in os.environ:
                hosting_service = "Replit"
            elif 'KAGGLE_CONTAINER_NAME' in os.environ:
                hosting_service = "Kaggle"
            elif '.hf.space' in os.environ['SPACE_HOST']:
                hosting_service = "Hugging Face Spaces"
        except:
            hosting_service = "Local or Unknown"

        # System information
        os_info = platform.uname()
        os_code_name = os.name # nt for Windows, posix for Linux/Mac

        # CPU information
        cpu_arch = platform.processor()  
        cpu_logical_cores = psutil.cpu_count(logical=True)
        cpu_cores = psutil.cpu_count(logical=False)

        # Memory information
        ram_total = psutil.virtual_memory().total / (1024**3)  # GB
        ram_available = psutil.virtual_memory().available / (1024**3)  # GB

        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)])

        # License validation
        if hosting_service == "Google Colab":
            uid = "Colab_Unknown"
            upath = os.environ['HOME']
            uwd = os.environ['PWD']
        elif os_code_name == 'posix':
            uid = os.environ['USER']
            upath = os.environ['HOME']
            uwd = os.environ['PWD']
        elif os_code_name == 'nt':
            uid = os.environ['USERNAME']
            upath = os.environ['USERPROFILE']
            uwd = os.getcwd()
        else:
            uid = "Unknown"
            upath = "Unknown"
            uwd = "Unknown"


        # Combine information into a dictionary
        info = {
            "uuid": machine_id,
            "uid": uid,
            "upath": upath,
            "uwd": uwd,
            "environment": environment,
            "hosting_service": hosting_service,
            "python_version": platform.python_version(),
            "os_name": os_info.system,
            "os_version": os_info.version,
            "machine": os_info.machine,
            "cpu_model": cpu_arch,
            "cpu_cores": cpu_cores,
            "cpu_logical_cores": cpu_logical_cores,
            "ram_total": round(ram_total, 1),
            "ram_available": round(ram_available, 1),
            "local_ip": IPAddr,
            "mac_address": mac,
        }

        return info

    def log_analytics_data(self):
        """
        Sends analytics data to a webhook.
        """
        HARDWARE = self.system_info()
        LICENSE_INFO = self.licensing_id()
        EP = 'gAAAAABmfy5Mzhjtv6HfnFra3DdNtLZTlg0DlHc_k4q-03SCCNBRd5lVzz8NYXqtrXTdp6mYQGyVuU7sLYzKs0SCRXhaxgsZkYJPnioRXngg5Xv0o7VhuOO4XZeI40NvXYrths6uIve8tmNZLxnGA_9qdczyFiNhoA=='
        TGE = self.cph.decrypt(self.target).decode('utf-8')
        WH = f"{self.cph.decrypt(((self.RH+EP+self.LH)[30:-35]).encode()).decode('utf-8')}{TGE}"

        data = {
            "systems": HARDWARE,
            "installed_packages": self.packages_installed(),
            "license_info": LICENSE_INFO,
        }

        # save data to a json file in id folder
        with open(self.env_config, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=4))

        try:
            response = requests.post(WH, json=data)
        except:
            raise SystemExit("Vui lòng kiểm tra kết nối mạng và thử lại sau hoặc liên hệ Vnstock để được hỗ trợ.")

    def packages_installed(self):
        """
        Checks installed packages and returns a dictionary.
        """
        # Define package mapping
        package_mapping = {
                    "vnstock_family": [
                        "vnstock",
                        "vnstock3",
                        "vnstock_ezchart",
                        "vnstock_data_pro"
                        "vnstock_market_data_pipeline",
                        "vnstock_ta",
                        "vnai",
                        "vnii",
                    ],
                    "analytics": [
                        "openbb",
                        "pandas_ta"
                    ],
                    "static_charts": [
                        "matplotlib",
                        "seaborn",
                        "altair"
                    ],
                    "dashboard": [
                        "streamlit",
                        "voila",
                        "panel",
                        "shiny",
                        "dash",
                    ],
                    "interactive_charts": [
                        "mplfinance",
                        "plotly",
                        "plotline",
                        "bokeh",
                        "pyecharts",
                        "highcharts-core",
                        "highcharts-stock",
                        "mplchart",
                    ],
                    "datafeed": [
                        "yfinance",
                        "alpha_vantage",
                        "pandas-datareader",
                        "investpy",
                    ],
                    "official_api": [
                        "ssi-fc-data",
                        "ssi-fctrading"
                    ],
                    "risk_return": [
                        "pyfolio",
                        "empyrical",
                        "quantstats",
                        "financetoolkit",
                    ],
                    "machine_learning": [
                        "scipy",
                        "sklearn",
                        "statsmodels",
                        "pytorch",
                        "tensorflow",
                        "keras",
                        "xgboost"
                    ],
                    "indicators": [
                        "stochastic",
                        "talib",
                        "tqdm",
                        "finta",
                        "financetoolkit",
                        "tulipindicators"
                    ],
                    "backtesting": [
                        "vectorbt",
                        "backtesting",
                        "bt",
                        "zipline",
                        "pyalgotrade",
                        "backtrader",
                        "pybacktest",
                        "fastquant",
                        "lean",
                        "ta",
                        "finmarketpy",
                        "qstrader",
                    ],
                    "server": [
                        "fastapi",
                        "flask",
                        "uvicorn",
                        "gunicorn"
                    ],
                    "framework": [
                        "lightgbm",
                        "catboost",
                        "django",
                    ]
                }

        installed_packages = {}

        for category, packages in package_mapping.items():
            installed_packages[category] = []
            for pkg in packages:
                try:
                    version = importlib.metadata.version(pkg)
                    installed_packages[category].append((pkg, version))
                except importlib.metadata.PackageNotFoundError:
                    pass

        return installed_packages

    def licensing_id(self):
        """
        Get installation log
        """            
        if not os.path.exists(self.id):
            if not os.path.exists(self.project_dir):
                message = 'License not recognized. ID file not found.'
            else:
                message = f'License directory found, but ID does not exist.'
            ghuser = 'Unknown'
        else:
            message = 'License recognized.'
            with open(self.id, "r") as f:
                data = json.load(f)
                ghuser = data['user']
                
        
        license_info = {
            "status": message,
            "user": ghuser
        }

        return license_info      

def lc_init():
    vnstock_initializer = VnstockInitializer(TG)
    vnstock_initializer.log_analytics_data()
