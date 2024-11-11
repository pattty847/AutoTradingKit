# coding:utf-8
import sys

from PySide6.QtCore import Qt, QCalendar, QDate
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout

from qfluentwidgets import  setTheme, Theme, FluentTranslator, FlyoutAnimationType

from qfluentwidgets.components.date_time.fast_calendar_view import FastCalendarView

from atklip.gui.top_bar.goto.goto_menu import DateTimeMenu
class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        self.setStyleSheet('Demo{background: white}')

        # self.picker = FastCalendarPicker(self)
        # self.picker.dateChanged.connect(print)
        
        self.picker = FastCalendarView(self)

        # customize animation
        # self.picker.setFlyoutAnimationType(FlyoutAnimationType.SLIDE_RIGHT)

        # set date
        # self.picker.setDate(QDate(2023, 5, 30))

        # customize date format
        # self.picker.setDateFormat(Qt.TextDate)
        # self.picker.setDateFormat('yyyy-M-d')

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.picker, 0, Qt.AlignCenter)
        self.resize(500, 500)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = Demo()
    w.show()
    app.exec()