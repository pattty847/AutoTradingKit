# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLayout,
    QSizePolicy, QSplitter, QVBoxLayout, QWidget)

from atklip.graphics.chart_component.graph_spliter import GraphSplitter
from atklip.gui.draw_bar.draw_bar import DRAW_BAR
from atklip.gui.qfluentwidgets.components.container.vspliter import VSplitter
from atklip.gui.right_bar.right_bar import RIGHT_BAR
from atklip.gui.top_bar.top_bar import TopBar

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        if not MainWidget.objectName():
            MainWidget.setObjectName(u"MainWidget")
        MainWidget.setWindowModality(Qt.NonModal)
        MainWidget.resize(941, 657)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWidget.sizePolicy().hasHeightForWidth())
        MainWidget.setSizePolicy(sizePolicy)
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        MainWidget.setFont(font)
        MainWidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(MainWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.frame_3 = QFrame(MainWidget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 2))
        self.frame_3.setMaximumSize(QSize(16777215, 2))
        self.frame_3.setStyleSheet(u"background-color: #474747;")
        self.frame_3.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_4.addWidget(self.frame_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_6 = QFrame(MainWidget)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setMinimumSize(QSize(2, 0))
        self.frame_6.setMaximumSize(QSize(2, 45))
        self.frame_6.setStyleSheet(u"background-color: #474747;")
        self.frame_6.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_2.addWidget(self.frame_6)

        self.topbar = TopBar(MainWidget)
        self.topbar.setObjectName(u"topbar")
        self.topbar.setMinimumSize(QSize(0, 45))
        self.topbar.setMaximumSize(QSize(16777215, 45))
        self.topbar.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_2.addWidget(self.topbar)

        self.frame_10 = QFrame(MainWidget)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setMinimumSize(QSize(2, 0))
        self.frame_10.setMaximumSize(QSize(2, 16777215))
        self.frame_10.setStyleSheet(u"background-color: #474747;")
        self.frame_10.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_2.addWidget(self.frame_10)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.frame_2 = QFrame(MainWidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 2))
        self.frame_2.setMaximumSize(QSize(16777215, 2))
        self.frame_2.setStyleSheet(u"background-color: #474747;")
        self.frame_2.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_4.addWidget(self.frame_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_8 = QFrame(MainWidget)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setMinimumSize(QSize(2, 0))
        self.frame_8.setMaximumSize(QSize(2, 16777215))
        self.frame_8.setStyleSheet(u"background-color: #474747;")
        self.frame_8.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.frame_8)

        self.drawbar = DRAW_BAR(MainWidget)
        self.drawbar.setObjectName(u"drawbar")
        sizePolicy.setHeightForWidth(self.drawbar.sizePolicy().hasHeightForWidth())
        self.drawbar.setSizePolicy(sizePolicy)
        self.drawbar.setMaximumSize(QSize(60, 16777215))
        self.drawbar.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.drawbar)

        self.frame_4 = QFrame(MainWidget)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(2, 0))
        self.frame_4.setMaximumSize(QSize(2, 16777215))
        self.frame_4.setStyleSheet(u"background-color: #474747;")
        self.frame_4.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.frame_4)

        self.chartview = QFrame(MainWidget)
        self.chartview.setObjectName(u"chartview")
        self.chartview.setMinimumSize(QSize(0, 600))
        self.chartview.setStyleSheet(u"background-color: rgb(71, 71, 71);")
        self.chartview.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_2 = QVBoxLayout(self.chartview)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.splitter_2 = QSplitter(self.chartview)
        self.splitter_2.setObjectName(u"splitter_2")
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setHandleWidth(2)
        self.splitter = VSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setFrameShape(QFrame.NoFrame)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(True)
        self.chartframe = QFrame(self.splitter)
        self.chartframe.setObjectName(u"chartframe")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.chartframe.sizePolicy().hasHeightForWidth())
        self.chartframe.setSizePolicy(sizePolicy1)
        self.chartframe.setMinimumSize(QSize(0, 0))
        self.chartframe.setStyleSheet(u"background-color: rgb(22, 22, 22);")
        self.chartframe.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_6 = QVBoxLayout(self.chartframe)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.chartbox_splitter = GraphSplitter(self.chartframe)
        self.chartbox_splitter.setObjectName(u"chartbox_splitter")
        sizePolicy1.setHeightForWidth(self.chartbox_splitter.sizePolicy().hasHeightForWidth())
        self.chartbox_splitter.setSizePolicy(sizePolicy1)

        self.verticalLayout_6.addWidget(self.chartbox_splitter)

        self.splitter.addWidget(self.chartframe)
        self.tradebox = QFrame(self.splitter)
        self.tradebox.setObjectName(u"tradebox")
        sizePolicy.setHeightForWidth(self.tradebox.sizePolicy().hasHeightForWidth())
        self.tradebox.setSizePolicy(sizePolicy)
        self.tradebox.setMaximumSize(QSize(16777215, 0))
        self.tradebox.setStyleSheet(u"background-color: rgb(22, 22, 22);\n"
"background-color: rgb(72, 72, 72);")
        self.tradebox.setFrameShape(QFrame.NoFrame)
        self.splitter.addWidget(self.tradebox)
        self.splitter_2.addWidget(self.splitter)
        self.rightview = QFrame(self.splitter_2)
        self.rightview.setObjectName(u"rightview")
        sizePolicy.setHeightForWidth(self.rightview.sizePolicy().hasHeightForWidth())
        self.rightview.setSizePolicy(sizePolicy)
        self.rightview.setMaximumSize(QSize(0, 16777215))
        self.rightview.setFont(font)
        self.rightview.setStyleSheet(u"background-color: rgb(22, 22, 22);\n"
"background-color: rgb(72, 72, 72);")
        self.rightview.setFrameShape(QFrame.NoFrame)
        self.splitter_2.addWidget(self.rightview)

        self.verticalLayout_2.addWidget(self.splitter_2)


        self.horizontalLayout.addWidget(self.chartview)

        self.rightbar = RIGHT_BAR(MainWidget)
        self.rightbar.setObjectName(u"rightbar")
        sizePolicy.setHeightForWidth(self.rightbar.sizePolicy().hasHeightForWidth())
        self.rightbar.setSizePolicy(sizePolicy)
        self.rightbar.setMaximumSize(QSize(60, 16777215))
        self.rightbar.setStyleSheet(u"background-color: rgb(255, 85, 0);\n"
"background-color: rgb(33, 33, 33);")
        self.rightbar.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.rightbar)

        self.frame_7 = QFrame(MainWidget)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setMinimumSize(QSize(2, 0))
        self.frame_7.setMaximumSize(QSize(2, 16777215))
        self.frame_7.setStyleSheet(u"background-color: #474747;")
        self.frame_7.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.frame_7)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.frame_5 = QFrame(MainWidget)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(0, 2))
        self.frame_5.setMaximumSize(QSize(16777215, 2))
        self.frame_5.setStyleSheet(u"background-color: #474747;")
        self.frame_5.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_4.addWidget(self.frame_5)


        self.verticalLayout.addLayout(self.verticalLayout_4)


        self.retranslateUi(MainWidget)

        QMetaObject.connectSlotsByName(MainWidget)
    # setupUi

    def retranslateUi(self, MainWidget):
        MainWidget.setWindowTitle(QCoreApplication.translate("MainWidget", u"Frame", None))
    # retranslateUi

