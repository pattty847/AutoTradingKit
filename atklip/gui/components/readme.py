from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import  QApplication



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
        self.webView.setUrl(QUrl("file:///" + "atklip/appdata/readme.pdf".replace('\\', '/')))
    def show(self):
        self.webView.setUrl(QUrl("file:///" + "atklip/appdata/readme.pdf".replace('\\', '/')))
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(1000, 800)
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        return super().show()
        
