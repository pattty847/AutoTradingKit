# type: ignore # coding:utf-8
import sys,asyncio
from typing import Union, TYPE_CHECKING
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QApplication, QApplication, QStackedWidget

from atklip.gui.qfluentwidgets import isDarkTheme
from atklip.gui.qfluentwidgets.common import CryptoIcon as CI
from atklip.gui.qfluentwidgets.common import screen,FluentIconBase,qconfig, qrouter, FluentStyleSheet, isDarkTheme, BackgroundAnimationWidget
from atklip.gui.qfluentwidgets.common.icon import *
from qframelesswindow import FramelessWindow

from .titlebar import TitleBar
from .mainlayout import MainWidget
from atklip.app_utils import *
from atklip.appmanager.setting import AppConfig
from atklip.appmanager.worker.threadpool import ThreadPoolExecutor_global
if TYPE_CHECKING:
    from atklip.gui.qfluentwidgets.components import TabBar
"thiếu quản lý tab khi xóa 1 tab bất kỳ, switch to tab khác và xóa tab muốn xóa, thử lưu router key vào 1 dict"
class WindowBase(BackgroundAnimationWidget, FramelessWindow):
    """ Fluent window base class """
    #currentInterface = Signal(object)
    def __init__(self, parent=None):
        self._isMicaEnabled = False
        super().__init__(parent=parent)
        self.setTitleBar(TitleBar(self))
        self.tabBar:TabBar = self.titleBar.tabBar
        
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 45, 0, 0)

        self.setLayout(self.hBoxLayout)

        self.stackedWidget = QStackedWidget(self)

        self.stackedWidget.setContentsMargins(0,0,0,0)

        self.hBoxLayout.addWidget(self.stackedWidget)
        
        # enable mica effect on win11
        self.setMicaEffectEnabled(False)

        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)
        self.tabBar.tabCloseRequested.connect(self.onTabCloseRequested)
        qconfig.themeChangedFinished.connect(self._onThemeChangedFinished)
        FluentStyleSheet.FLUENT_WINDOW.apply(self)
        self.onTabAddRequested()
        self.initWindow()
        

    def initWindow(self):
        self.resize(800, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        # self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.resize(w, h)
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        # self.showMaximized()
        self.resize(self.width(), self.height())
        self.show()
        # QApplication.processEvents()
    

    def load_pre_config(self):
        curent_tab = AppConfig.get_config_value("profiles.current_tab")
        if curent_tab == None:
            AppConfig.sig_set_single_data.emit(("profiles.current_tab", {"exchangeID":"binanceusdm","symbol":"BTC/USDT"}))
            curent_tab = AppConfig.get_config_value("profiles.current_tab")
        
        current_ex = curent_tab["exchangeID"]
        current_symbol = curent_tab["symbol"]

        curent_interval = AppConfig.get_config_value(f"topbar.interval.acticebtn")
        if curent_interval == None:
            AppConfig.sig_set_single_data.emit((f"topbar.interval.acticebtn","1m"))
            curent_interval = AppConfig.get_config_value(f"topbar.interval.acticebtn")
        
        return current_ex,current_symbol,curent_interval
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.titleBar.resize(self.width(), self.titleBar.height())
        self.stackedWidget.resize(self.width(), self.height() - 45)
        self.resize(self.width(),self.height())
        interface = self.stackedWidget.currentWidget()
        if isinstance(interface,MainWidget):
            if interface.progress.isVisible():
                interface.progress.run_process(True)

    def resize(self,w=None,h=None):
        if w == None or h== None:
            _w = self.width()
            _h = self.height()
        else:
            _w = w
            _h = h
        super().resize(_w,_h)
    
    def addInterface(self, interface: MainWidget) -> None:
        """ add sub interface """
        self.stackedWidget.addWidget(interface)
        self.resize(self.width(), self.height() - 45)
        interface.resize(self.width(), self.height())
        

    def removeInterface(self, interface: MainWidget) -> None:
        """ add sub interface """
        self.stackedWidget.removeWidget(interface)
        asyncio.run(interface.chartbox_splitter.chart.close())
        interface.deleteLater()
        
    def onTabCloseRequested(self, index):
        self.tabBar.removeTab(index)
        self.removeInterface(self.stackedWidget.widget(index))
    def close_window(self):
        interfaces = self.stackedWidget.children()
        if interfaces != []:
            for interface in interfaces:
                if isinstance(interface,MainWidget):
                    asyncio.run(interface.chartbox_splitter.chart.close())
        self.hide()
        ThreadPoolExecutor_global.shutdown()
        self.deleteLater()
    
    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        TabInterface = self.findChild(MainWidget, objectName)
        old_interface = self.stackedWidget.currentWidget()
        old_interface.hide()
        TabInterface.resize(old_interface.width(),old_interface.height())
        self.switchTo(TabInterface)
    def onTabAddRequested(self):
        current_ex,current_symbol,curent_interval = self.load_pre_config()
        _is_icon_exist = check_icon_exist(current_symbol)
        if _is_icon_exist:
            icon_path = CI.crypto_url(current_symbol)
        else :
            icon_path = CI.BTC.path()

        routeKey = f'{current_symbol}-{curent_interval}-{self.tabBar.count()}'
        self.addTab(routeKey, f"{current_symbol} {curent_interval}", icon_path,current_ex,current_symbol,curent_interval)
        

    def addTab(self, routeKey, text, icon,current_ex,current_symbol,curent_interval):
        tabItem = self.tabBar.addTab(routeKey, text, icon)
        self.tabBar.setCurrentTab(routeKey)
        # self.stackedWidget.resize(self.width(), self.height() - self.titleBar.height())
        TabInterface = MainWidget(self,tabItem,routeKey,current_ex,current_symbol,curent_interval)
        
        # old_interface = self.stackedWidget.currentWidget()
        # if isinstance(old_interface,MainWidget):
        #     old_interface.hide()
        #     TabInterface.resize(old_interface.width(),old_interface.height())
            
        self.addInterface(TabInterface)
        self.switchTo(TabInterface)

    def setTabIcon(self, index: int, icon: Union[QIcon, FluentIconBase, str]):
        """ set tab icon """
        self.tabBar.tabItem(index).setIcon(icon)

    def setTabText(self, index: int, text: str):
        """ set tab text """
        self.tabBar.tabItem(index).setText(text)
    def switchTo(self, interface: MainWidget):
        if not interface.isVisible():
            interface.show()
        # interface.progress.run_process(True)
        self.stackedWidget.setCurrentWidget(interface)

    def _onCurrentInterfaceChanged(self, widget: MainWidget):
        #widget = self.stackedWidget.widget(index)
        qrouter.push(self.stackedWidget, widget.objectName())
        old_interface = self.stackedWidget.currentWidget()
        old_interface.hide()
        widget.resize(old_interface.width(),old_interface.height())
        self.switchTo(widget)
        self._updateStackedBackground()

    def _updateStackedBackground(self):
        isTransparent = self.stackedWidget.currentWidget().property("isStackedTransparent")
        if bool(self.stackedWidget.property("isTransparent")) == isTransparent:
            return
        
        self.stackedWidget.setProperty("isTransparent", isTransparent)
        self.stackedWidget.setStyle(QApplication.style())
        self.update()

    def _normalBackgroundColor(self):
        if not self.isMicaEffectEnabled():
            return QColor(32, 32, 32) if isDarkTheme() else QColor(243, 243, 243)

        return QColor(0, 0, 0, 0)

    def _onThemeChangedFinished(self):
        if self.isMicaEffectEnabled():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.backgroundColor)
        painter.drawRect(self.rect())

    def setMicaEffectEnabled(self, isEnabled: bool):
        """ set whether the mica effect is enabled, only available on Win11 """
        if sys.platform != 'win32' or sys.getwindowsversion().build < 22000:
            return

        self._isMicaEnabled = isEnabled

        if isEnabled:
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
        else:
            self.windowEffect.removeBackgroundEffect(self.winId())

        self.setBackgroundColor(self._normalBackgroundColor())

    def isMicaEffectEnabled(self):
        return self._isMicaEnabled
