import sys
from atklip.gui_components.qfluentwidgets.common import setTheme,Theme
from atklip.gui_components.qfluentwidgets.common.icon import *
from atklip.gui_components.qfluentwidgets.components.dialog_box import MessageBox
from atklip.views.fluentwindow import WindowBase
from PySide6.QtCore import QCoreApplication,QSize
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication
import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings("ignore", category=RuntimeWarning)

class MainWindow(WindowBase):
    def __init__(self):
        self.isMicaEnabled = False
        super().__init__()
    def closeEvent(self, event: QCloseEvent) -> None:
        quit_msg = QCoreApplication.translate("MainWindow", u"To close window click button OK", None)   
        mgsBox = MessageBox("Quit Application?", quit_msg, self.window())
        if mgsBox.exec():
            self.close_window()
            self.deleteLater()
            event.accept()
        else:
            event.ignore()

def main():
    setTheme(Theme.DARK,True,True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationVersion("1.0.0")
    app.setApplicationName('Auto Trading Kit')
    app.setApplicationDisplayName('ATK (v1.0.0)')
    app.setOrganizationName('ATK-Team')
    app.setOrganizationDomain('ATK.COM')
    w = MainWindow()
    w.setWindowTitle('ATK - Auto Trading Kit')
    icon = QIcon()
    app_icon = get_real_path("atklip/appdata")
    icon.addFile(f'{app_icon}/appico.ico',QSize(), QIcon.Normal, QIcon.Off)
    w.setWindowIcon(icon)
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()