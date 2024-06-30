# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'combobox_value.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout)

from atklip.gui_components.qfluentwidgets.components.widgets import (ComboBox, TitleLabel)

class Ui_combobox_value(object):
    def setupUi(self, combobox_value):
        if not combobox_value.objectName():
            combobox_value.setObjectName(u"combobox_value")
        combobox_value.resize(358, 35)
        self.horizontalLayout = QHBoxLayout(combobox_value)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 1, 10, 1)
        self.tittle = TitleLabel(combobox_value)
        self.tittle.setObjectName(u"tittle")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = ComboBox(combobox_value)
        self.value.setObjectName(u"value")

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(combobox_value)

        QMetaObject.connectSlotsByName(combobox_value)
    # setupUi

    def retranslateUi(self, combobox_value):
        combobox_value.setWindowTitle(QCoreApplication.translate("combobox_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("combobox_value", u"Title label", None))
    # retranslateUi

