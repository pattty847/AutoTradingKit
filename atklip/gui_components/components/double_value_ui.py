# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'double_value.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout)

from atklip.gui_components.qfluentwidgets.components.widgets import (DoubleSpinBox, TitleLabel)

class Ui_double_value(object):
    def setupUi(self, double_value):
        if not double_value.objectName():
            double_value.setObjectName(u"double_value")
        double_value.resize(345, 35)
        self.horizontalLayout = QHBoxLayout(double_value)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 1, 10, 1)
        self.tittle = TitleLabel(double_value)
        self.tittle.setObjectName(u"tittle")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = DoubleSpinBox(double_value)
        self.value.setObjectName(u"value")

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(double_value)

        QMetaObject.connectSlotsByName(double_value)
    # setupUi

    def retranslateUi(self, double_value):
        double_value.setWindowTitle(QCoreApplication.translate("double_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("double_value", u"Title label", None))
    # retranslateUi

