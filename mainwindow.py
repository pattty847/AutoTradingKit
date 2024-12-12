import sys
from PySide6.QtCore import QCoreApplication,QSize
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication

from atklip.gui.qfluentwidgets.common import screen, setTheme,Theme
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.gui.qfluentwidgets.components.dialog_box import MessageBox
from atklip.gui.views.fluentwindow import WindowBase
from atklip.appmanager.setting.config import cfg


class MainWindow(WindowBase):
    def __init__(self):
        self.isMicaEnabled = False
        super().__init__()

    def closeEvent(self, event: QCloseEvent) -> None:
        quit_msg = QCoreApplication.translate("MainWindow", u"To close window click button OK", None)
        mgsBox = MessageBox("Quit Application?", quit_msg, self.window())
        response = mgsBox.exec()
        if response:
            self.close_window()
            self.deleteLater()
            event.accept()
        else:
            event.ignore()

def main():
    # enable dpi scale
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    
    setTheme(Theme.DARK, True, True)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    app.setStyle("Fusion")
    app.setApplicationVersion("1.0.0")
    app.setApplicationName('Auto Trading Kit')
    app.setApplicationDisplayName('ATK (v1.0.0)')
    app.setOrganizationName('ATK-Team')
    app.setOrganizationDomain('ATK.COM')
    w = MainWindow()
    w.setWindowTitle('ATK - Auto Trading Kit')
    icon = QIcon(get_real_path("atklip/appdata") + '/appico.ico')
    w.setWindowIcon(icon)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()