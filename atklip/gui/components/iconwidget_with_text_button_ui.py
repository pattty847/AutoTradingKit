# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'iconwidget_with_text_button.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout)

from atklip.gui.qfluentwidgets.components.widgets import (IconWidget, TitleLabel)
import resource
class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(213, 40)
        Form.setMinimumSize(QSize(200, 40))
        Form.setMaximumSize(QSize(16777215, 45))
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 1, 9, 1)
        self.exchange_icon = IconWidget(Form)
        self.exchange_icon.setObjectName(u"exchange_icon")
        self.exchange_icon.setMinimumSize(QSize(30, 30))
        self.exchange_icon.setMaximumSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.exchange_icon)

        self.TitleLabel = TitleLabel(Form)
        self.TitleLabel.setObjectName(u"TitleLabel")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.TitleLabel.setFont(font)

        self.horizontalLayout.addWidget(self.TitleLabel)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.TitleLabel.setText(QCoreApplication.translate("Form", u"Title label", None))
    # retranslateUi

