from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtWidgets import QWidget


from atklip.gui.qfluentwidgets import *
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui import qconfig, Config

class _SplitDropButton(SplitDropButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""QToolButton {
                            border: none;
                            border-radius: 4px;
                            background-color: transparent;}""")
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.setStyleSheet(f"""QToolButton {{
                                    border: none;
                                    border-radius: 4px;
                                    background-color: {background_color};}}""")
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet("""QToolButton {
                                    border: none;
                                    border-radius: 4px;
                                    background-color: transparent;}""")
        super().leaveEvent(event)


class _TitleLabel(TitleLabel):
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        self.setFixedHeight(35)
        self.setMinimumWidth(120)
        self.setContentsMargins(0,0,0,0)

    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QLabel {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 12pt "Segoe UI" 'PingFang SC';
                            font-weight: SemiBold;
                        }}""")
    # def enterEvent(self, event):
    #     background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
    #     if self.isChecked():
    #         color = "#0055ff"
    #     else:
    #         color = "#d1d4dc" if isDarkTheme() else  "#161616"
    #     self.setStyleSheet(f"""QPushButton {{
    #         background-color: {background_color};
    #         border: none;
    #         border-radius: 4px;
    #         color: {color};
    #         font: 12pt "Segoe UI";
    #         font-weight: Bold;
    #         }}""")

    #     super().enterEvent(event)
    # def leaveEvent(self, event):
    #     #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
    #     if self.isChecked():
    #         color = "#0055ff"
    #     else:
    #         color = "#d1d4dc" if isDarkTheme() else  "#161616"
    #     self.set_stylesheet(color)
    #     super().leaveEvent(event)


class LayoutButton(SplitWidgetBase):

    clicked = Signal()
    #@singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.setObjectName('IndicatorButton')

        self.cfg:Config = qconfig._cfg

        self.titleLabel:_TitleLabel = _TitleLabel("ATK main layout",self)

        self.setWidget(self.titleLabel)
        #self.indicator.show()
        self.setDropButton(_SplitDropButton(self))
        self.setDropIcon(FIF.ARROW_DOWN)
        self.setDropIconSize(QSize(10, 10))
        self.dropButton.setFixedSize(16,30)
        self._postInit()

    def get_current_inteval(self):
        return self.current_active.title()

    def save_favorites(self):
        if self.favorites != []:
            for item in  self.favorites:
                pass
    def setWidget(self, widget: QWidget):
        """ set the widget on left side """

        self.hBoxLayout.insertWidget(0, widget, 1, Qt.AlignLeft)

    def uncheck_items(self,btn):
        pass
    def set_text_color(self):
        pass
        # btn = self.sender()
        # if btn.isChecked():
        #     self.uncheck_items(btn)
        #     btn.setStyleSheet("""QPushButton {
        #             background-color: transparent;
        #             border: none;
        #             border-radius: 4px;
        #             margin: 0;
        #             color: "#0055ff";
        #             font: 15px 'Segoe UI', 'PingFang SC';
        #             font-weight: Bold;
        #             }""")

    def _postInit(self):
        pass
        
    
    def setcurrent_item(self,current_active):
        pass

    def setFlyout(self, flyout):
        self.flyout = flyout
    def showFlyout(self):
        """ show flyout """
        w = self.flyout
        if not w:
            return
        if isinstance(w, RoundMenu):
            #w.view.setMinimumWidth(self.width())
            #w.view.adjustSize()
            #w.adjustSize()
            x = self.width()
            #y = self.height()
            y = 0
            w.exec(self.mapToGlobal(QPoint(x, y)))
    
    def add_remove_to_favorites(self, title:str=None):
        """ add item to favorites """
        pass
    def change_item(self, title:str=None):
        """ change item """
        pass