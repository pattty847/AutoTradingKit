from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import  QApplication

from atklip.gui.qfluentwidgets.common.icon import get_real_path



class ReadmeViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Readme Viewer")
        # self.setWindowFlag(Qt.FramelessWindowHint)
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(1000, 800)
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1,1,1,1)
        self.webView = QWebEngineView()
        self.webView.setContentsMargins(1,1,1,1)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)
        readme_path:str = get_real_path("atklip/appdata/readme.pdf")
        self.webView.setUrl(QUrl("file:///" + readme_path.replace('\\', '/')))
    def show(self):
        readme_path:str = get_real_path("atklip/appdata/readme.pdf")
        self.webView.setUrl(QUrl("file:///" + readme_path.replace('\\', '/')))
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(1000, 800)
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        return super().show()
        
