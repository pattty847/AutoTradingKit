# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'color_value.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout)

from atklip.gui_components.components._pushbutton import Color_Picker_Button
from atklip.gui_components.qfluentwidgets.components.widgets import (TitleLabel)

class Ui_color_value(object):
    def setupUi(self, color_value):
        if not color_value.objectName():
            color_value.setObjectName(u"color_value")
        color_value.resize(343, 35)
        self.horizontalLayout = QHBoxLayout(color_value)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 1, 10, 1)
        self.tittle = TitleLabel(color_value)
        self.tittle.setObjectName(u"tittle")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = Color_Picker_Button(parent=color_value,enableAlpha = True)
        self.value.setObjectName(u"value")

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(color_value)

        QMetaObject.connectSlotsByName(color_value)
    # setupUi

    def retranslateUi(self, color_value):
        color_value.setWindowTitle(QCoreApplication.translate("color_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("color_value", u"Title label", None))
        self.value.setText("")
    # retranslateUi

