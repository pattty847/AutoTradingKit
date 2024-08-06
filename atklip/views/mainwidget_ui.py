# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLayout,
    QSizePolicy, QSplitter, QVBoxLayout)

from atklip.graph_objects.chart_component import GraphSplitter
from atklip.gui_components.draw_bar.draw_bar import DRAW_BAR
from atklip.gui_components.qfluentwidgets.components.container.vspliter import VSplitter
from atklip.gui_components.right_bar.right_bar import RIGHT_BAR
from atklip.gui_components.top_bar.top_bar import TopBar

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        if not MainWidget.objectName():
            MainWidget.setObjectName(u"MainWidget")
        MainWidget.setWindowModality(Qt.WindowModality.WindowModal)
        MainWidget.resize(1400, 800)
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
        self.frame_2 = QFrame(MainWidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 2))
        self.frame_2.setMaximumSize(QSize(16777215, 2))
        self.frame_2.setStyleSheet(u"background-color: #474747;")
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Plain)

        self.verticalLayout_4.addWidget(self.frame_2)

        self.topbar = TopBar(MainWidget)
        self.topbar.setObjectName(u"topbar")
        self.topbar.setMinimumSize(QSize(0, 45))
        self.topbar.setMaximumSize(QSize(16777215, 45))
        self.topbar.setFrameShape(QFrame.Shape.NoFrame)
        self.topbar.setFrameShadow(QFrame.Shadow.Plain)

        self.verticalLayout_4.addWidget(self.topbar)

        self.frame_3 = QFrame(MainWidget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 2))
        self.frame_3.setMaximumSize(QSize(16777215, 2))
        self.frame_3.setStyleSheet(u"background-color: #474747;")
        self.frame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Shadow.Plain)

        self.verticalLayout_4.addWidget(self.frame_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.drawbar = DRAW_BAR(MainWidget)
        self.drawbar.setObjectName(u"drawbar")
        sizePolicy.setHeightForWidth(self.drawbar.sizePolicy().hasHeightForWidth())
        self.drawbar.setSizePolicy(sizePolicy)
        self.drawbar.setMaximumSize(QSize(60, 16777215))
        self.drawbar.setFrameShape(QFrame.Shape.NoFrame)
        self.drawbar.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.drawbar)

        self.frame_4 = QFrame(MainWidget)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(2, 0))
        self.frame_4.setMaximumSize(QSize(2, 16777215))
        self.frame_4.setStyleSheet(u"background-color: #474747;")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.frame_4)

        self.chartview = QFrame(MainWidget)
        self.chartview.setObjectName(u"chartview")
        self.chartview.setStyleSheet(u"background-color: rgb(71, 71, 71);")
        self.chartview.setFrameShape(QFrame.Shape.NoFrame)
        self.chartview.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.chartview)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.splitter_2 = QSplitter(self.chartview)
        self.splitter_2.setObjectName(u"splitter_2")
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_2.setHandleWidth(2)
        self.splitter = VSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setFrameShape(QFrame.Shape.NoFrame)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(True)
        self.chartframe = QFrame(self.splitter)
        self.chartframe.setObjectName(u"chartframe")
        sizePolicy.setHeightForWidth(self.chartframe.sizePolicy().hasHeightForWidth())
        self.chartframe.setSizePolicy(sizePolicy)
        self.chartframe.setMinimumSize(QSize(0, 0))
        self.chartframe.setStyleSheet(u"background-color: rgb(22, 22, 22);")
        self.chartframe.setFrameShape(QFrame.Shape.StyledPanel)
        self.chartframe.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.chartframe)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.chartframe)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.chartbox_splitter = GraphSplitter(self.frame)
        self.chartbox_splitter.setObjectName(u"chartbox_splitter")
        sizePolicy.setHeightForWidth(self.chartbox_splitter.sizePolicy().hasHeightForWidth())
        self.chartbox_splitter.setSizePolicy(sizePolicy)
        self.chartbox_splitter.setMinimumSize(QSize(0, 0))
        self.chartbox_splitter.setOrientation(Qt.Orientation.Vertical)
        self.chartbox_splitter.setOpaqueResize(True)
        self.chartbox_splitter.setHandleWidth(1)

        self.verticalLayout_3.addWidget(self.chartbox_splitter)


        self.verticalLayout_6.addWidget(self.frame)

        self.splitter.addWidget(self.chartframe)
        self.tradebox = QFrame(self.splitter)
        self.tradebox.setObjectName(u"tradebox")
        sizePolicy.setHeightForWidth(self.tradebox.sizePolicy().hasHeightForWidth())
        self.tradebox.setSizePolicy(sizePolicy)
        self.tradebox.setMaximumSize(QSize(16777215, 0))
        self.tradebox.setStyleSheet(u"background-color: rgb(22, 22, 22);\n"
"background-color: rgb(72, 72, 72);")
        self.tradebox.setFrameShape(QFrame.Shape.NoFrame)
        self.tradebox.setFrameShadow(QFrame.Shadow.Raised)
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
        self.rightview.setFrameShape(QFrame.Shape.NoFrame)
        self.rightview.setFrameShadow(QFrame.Shadow.Raised)
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
        self.rightbar.setFrameShape(QFrame.Shape.NoFrame)
        self.rightbar.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout.addWidget(self.rightbar)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.verticalLayout_4)


        self.retranslateUi(MainWidget)

        QMetaObject.connectSlotsByName(MainWidget)
    # setupUi

    def retranslateUi(self, MainWidget):
        MainWidget.setWindowTitle(QCoreApplication.translate("MainWidget", u"Frame", None))
    # retranslateUi

