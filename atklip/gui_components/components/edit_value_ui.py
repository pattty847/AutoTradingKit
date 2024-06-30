# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_value.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout, QSizePolicy)

from atklip.gui_components.qfluentwidgets.components.widgets import (LineEdit, TitleLabel)

class Ui_text_value(object):
    def setupUi(self, text_value):
        if not text_value.objectName():
            text_value.setObjectName(u"text_value")
        text_value.resize(343, 35)
        self.horizontalLayout = QHBoxLayout(text_value)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 1, 10, 1)
        self.tittle = TitleLabel(text_value)
        self.tittle.setObjectName(u"tittle")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = LineEdit(text_value)
        self.value.setObjectName(u"value")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.value.sizePolicy().hasHeightForWidth())
        self.value.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(text_value)

        QMetaObject.connectSlotsByName(text_value)
    # setupUi

    def retranslateUi(self, text_value):
        text_value.setWindowTitle(QCoreApplication.translate("text_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("text_value", u"Title label", None))
    # retranslateUi

