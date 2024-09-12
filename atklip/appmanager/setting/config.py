import json
import threading
from PySide6.QtCore import QCoreApplication,Signal,QObject,Qt
from atklip.gui.qfluentwidgets.common.icon import *
# Gets or creates a logger

config_path = get_real_path("atklip/appdata")

class ConfigManager(QObject):
    sig_set_single_data = Signal(tuple)
    def __init__(self, filepath=f"{config_path}/config.json"):
        super().__init__()
        #self.moveToThread(QCoreApplication.instance().thread())
        self.config_lock = threading.Lock()
        self.config = {}
        self.filepath = filepath
        if filepath:
            self.load_config_file(filepath)
        self.sig_set_single_data.connect(self.set_config_value,Qt.ConnectionType.AutoConnection)
  
    def create_config_file(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.config, f)
            f.close()

    def set_config_value(self, args):
        key, value = args[0], args[1]
        keys = key.split('.')
        current = self.config 
        if len(keys) == 1:
            current[keys[-1]] = value
            self.save_config_file()
            return
        current = self.config   
        for k in keys[:-1]:
            if current != {}:
                if k not in list(current.keys()):
                    current[k] = {}
            else:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save_config_file()
        return self.get_config_value(key)
        #self.load_config_file(self.filepath)

    def set_config_values(self, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, tuple) or len(arg) != 2:
                raise ValueError('Arguments must be passed as tuples with two elements')
            key, value = arg[0], arg[1]
            self.sig_set_single_data.emit((key, value))
            QCoreApplication.processEvents()

        for key, value in kwargs.items():
            self.sig_set_single_data.emit((key, value))
            QCoreApplication.processEvents()

    def get_config_value(self, key, default=None):
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                return default
            current = current[k]
        return current.get(keys[-1], default)

    def delete_config_value(self, key):
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                return
            current = current[k]
        if keys[-1] in current:
            del current[keys[-1]]
            self.save_config_file()
            #self.load_config_file(self.filepath)
        else:
            return
        
    def save_config_file(self):
        self.create_config_file(self.filepath)

    
    def load_config_file(self, filepath):
        with self.config_lock:
            try:
                with open(filepath, 'r') as f:
                    self.config = json.load(f)
            except (IOError, json.JSONDecodeError):
                self.config = {}
                self.save_config_file()
    
    # def load_config_file(self, filepath):
    #     try:
    #         with open(filepath) as f:
    #             self.config = json.load(f)
    #             f.close()
    #     except (IOError, json.JSONDecodeError):
    #         self.config = {}
    #         self.save_config_file()
    def get_all_config(self):
        return self.config


# global AppConfig

AppConfig = ConfigManager()