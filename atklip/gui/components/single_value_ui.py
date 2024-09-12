# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'single_value.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout)

from atklip.gui.qfluentwidgets.components.widgets import (SpinBox, TitleLabel)

class Ui_single_value(object):
    def setupUi(self, single_value):
        if not single_value.objectName():
            single_value.setObjectName(u"single_value")
        single_value.resize(358, 35)
        single_value.setFixedHeight(35)
        self.horizontalLayout = QHBoxLayout(single_value)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 1, 10, 1)
        self.tittle = TitleLabel(single_value)
        self.tittle.setObjectName(u"tittle")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = SpinBox(single_value)
        self.value.setObjectName(u"value")

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(single_value)

        QMetaObject.connectSlotsByName(single_value)
    # setupUi

    def retranslateUi(self, single_value):
        single_value.setWindowTitle(QCoreApplication.translate("single_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("single_value", u"Title label", None))
    # retranslateUi

