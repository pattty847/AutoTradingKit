
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui_components.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui_components.components import ShowmenuButton,Card_Item
from atklip.gui_components import FluentIcon as FIF
# from atklip.gui_components.draw_bar import *
from atklip.gui_components.qfluentwidgets.common import *

class TEXTS(QFrame):
    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)

        self.splitToolButton = ShowmenuButton(FIF.TEXT,self.parent)

        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("TEXT & NOTES")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)

        self.text = Card_Item(FIF.TEXT,"Text", 'TEXT&NOTES',self)
        self.anchored_text = Card_Item(FIF.TEXT_ANCHORED,"Anchored Text", 'TEXT&NOTES',self)
        self.note = Card_Item(FIF.NOTE,"Note", 'TEXT&NOTES',self)
        self.anchored_note = Card_Item(FIF.NOTE_ANCHORED,"Anchored Note", 'TEXT&NOTES',self)
        self.callout = Card_Item(FIF.CALLOUT,"Callout", 'TEXT&NOTES',self)
        self.comment = Card_Item(FIF.COMMENT,"Comment", 'TEXT&NOTES',self)
        self.price_label = Card_Item(FIF.PRICE_LABEL,"Price Label", 'TEXT&NOTES',self)
        self.price_note = Card_Item(FIF.PRICE_NOTE,"Price Note", 'TEXT&NOTES',self)
        self.signpost = Card_Item(FIF.SIGNPOST,"Signpost", 'TEXT&NOTES',self)
        self.flag_mark = Card_Item(FIF.FLAG_MARK,"Flag Mark", 'TEXT&NOTES',self)
        # add item to card
        self.text.resize(250, 40)
        
        self.menu.addWidget(self.text)
        self.menu.addWidget(self.anchored_text)
        self.menu.addWidget(self.note)
        self.menu.addWidget(self.anchored_note)
        self.menu.addWidget(self.callout)
        self.menu.addWidget(self.comment)
        self.menu.addWidget(self.price_label)
        self.menu.addWidget(self.price_note)
        self.menu.addWidget(self.signpost)
        self.menu.addWidget(self.flag_mark)
        # split tool button
        self.menu.addSeparator()

        chanel_header_wg = QWidget(self.menu)
        chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        chanel_headerLabel = TitleLabel("CONTENT")
        chanel_headerLabel.setFixedHeight(25)
        chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(chanel_headerLabel, 13, QFont.DemiBold)
        chanel_headerLayout.addWidget(chanel_headerLabel)
        chanel_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(chanel_header_wg)

        self.image = Card_Item(FIF.IMAGE,"Image", 'TEXT&NOTES',self)
        self.idea = Card_Item(FIF.IDEA,"Idea", 'TEXT&NOTES',self)
        # add item to card
        # split tool button
        self.menu.addWidget(self.image)
        self.menu.addWidget(self.idea)

        
        self.splitToolButton.setFlyout(self.menu)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    def enterEvent(self, event):
        #self.splitToolButton.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        #self.splitToolButton.dropButton.hide()
        super().leaveEvent(event)
