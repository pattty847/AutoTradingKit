
from atklip.gui.qfluentwidgets.components import DateEdit,TimeEdit
from atklip.gui.qfluentwidgets.components.container import HWIDGET,HBoxLayout
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from atklip.gui.qfluentwidgets import FluentIcon as FIF
from atklip.gui.components import TextButton,MovingWidget

from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt,QDate


from .calendar_ui import Ui_Frame as CalendarView

class GotoButton(HWIDGET):
    def __init__(self,parent:QWidget=None):
        super(GotoButton, self).__init__(parent)
        self._parent = parent
        self.btn_goto = TextButton("Goto",self,None)
        self.btn_goto.setFixedSize(100,35)
        self.btn_goto.clicked.connect(self._onGotoClicked)

        self.btn_cancel = TextButton("Cancel",self,None)
        self.btn_cancel.setFixedSize(100,35)
        self.btn_cancel.clicked.connect(self._onCancelClicked)

        self.addSpacer()

        self.addWidget(self.btn_cancel)
        self.addWidget(self.btn_goto)
        self.setSpacing(5)
        self.setContentsMargins(8,1,8,5)
        
    def _onGotoClicked(self):
        self.close()
    def _onCancelClicked(self):
        self.hide()


class DatePicker(DateEdit):
    def __init__(self,parent:QWidget=None):
        super(DatePicker, self).__init__(parent)
        #FluentStyleSheet.DATEPICKER.apply(self)

class TimePicker(TimeEdit):
    def __init__(self,parent:QWidget=None):
        super(TimePicker,self).__init__(parent)
        

class Calendar(QFrame,CalendarView):
    def __init__(self,parent:QWidget=None):
        super(Calendar,self).__init__(parent)
        self.setupUi(self)
        self.setObjectName("calendarWidget")
        #self.setFixedHeight(350)

        #FluentStyleSheet.CALENDAR.apply(self)
    def _onDayItemClicked(self, date: QDate):
        print(date)

    def setDate(self, date: QDate):
        print(date)


class DateTimeMenu(MovingWidget):
    def __init__(self,sig_remove_menu,parent:QWidget=None):
        super(DateTimeMenu, self).__init__(parent,"Goto")
        self.title.btn_close.clicked.connect(sig_remove_menu,Qt.ConnectionType.AutoConnection)
        self.setContentsMargins(0,0,0,10)
        #self.setSpacing(5)
        #self.setFixedSize(380,520)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)

        self.datetime_widget = QWidget()
        self.date_time_layout = HBoxLayout(self.datetime_widget)
        self.date_time_layout.setContentsMargins(0,0,0,0)
        self.date_time_layout.setSpacing(5)

        self._DatePicker = DatePicker(self)
        self.date_time_layout.addWidget(self._DatePicker)
        
        self._TimePicker = TimePicker(self)
        self.date_time_layout.addWidget(self._TimePicker)

        self.addWidget(self.datetime_widget)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        
        self._CalendarPicker = Calendar(self.window())
        self.addWidget(self._CalendarPicker)
        
        w = self._CalendarPicker.width()
        self.addSeparator(_type = "HORIZONTAL",w=w,h=2)

        self.btn_goto_close = GotoButton(self.parent().window())
        self.addWidget(self.btn_goto_close)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        _height = self.height()
        
        _height += self.title.height()
        _height +=  self._DatePicker.height()
        _height +=  self._CalendarPicker.height()
        _height += self.btn_goto_close.height()
        
        self.setFixedSize(w,_height+2)

        FluentStyleSheet.DATETIMEMENU.apply(self)
    # def exec(self):
    #     self.show()
        