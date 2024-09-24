
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui.components import ShowmenuButton,Card_Item
from atklip.gui import FluentIcon as FIF
# from atklip.gui.draw_bar import *
from atklip.gui.qfluentwidgets.common import *
class BRUSHS(QFrame):
    def __init__(self,parent:QWidget=None,sig_draw_object_name=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.sig_draw_object_name = sig_draw_object_name
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)

        self.splitToolButton = ShowmenuButton(FIF.BRUSH,self.parent)

        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("BRUSHS")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)

        self.brush = Card_Item(FIF.BRUSH,"Brush", 'BRUSHS',self)
        self.highlighter = Card_Item(FIF.HIGHLIGHTER,"Highlighter", 'BRUSHS',self)

        # add item to card
        self.brush.resize(250, 40)
        
        self.menu.addWidget(self.brush)
        self.menu.addWidget(self.highlighter)
        # split tool button
        self.menu.addSeparator()

        chanel_header_wg = QWidget(self.menu)
        chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        chanel_headerLabel = TitleLabel("ARROWS")
        chanel_headerLabel.setFixedHeight(25)
        chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(chanel_headerLabel, 13, QFont.DemiBold)
        chanel_headerLayout.addWidget(chanel_headerLabel)
        chanel_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(chanel_header_wg)

        self.arrow_marker = Card_Item(FIF.ARROW_MAKER,"Arrow Marker", 'BRUSHS',self)
        self.arrow = Card_Item(FIF.ARROW,"Arrow", 'BRUSHS',self)
        self.arrow_mark_up = Card_Item(FIF.ARROW_MAKER_UP,"Arrow Mark Up", 'BRUSHS',self)
        self.arrow_mark_down = Card_Item(FIF.ARROW_MAKER_DOWN,"Arrow Mark Down", 'BRUSHS',self)
        # add item to card
        # split tool button
        self.menu.addWidget(self.arrow_marker)
        self.menu.addWidget(self.arrow)
        self.menu.addWidget(self.arrow_mark_up)
        self.menu.addWidget(self.arrow_mark_down)
        self.menu.addSeparator()

        pitchfork_header_wg = QWidget(self.menu)
        pitchfork_headerLayout = QHBoxLayout(pitchfork_header_wg)
        pitchfork_headerLabel = TitleLabel("SHAPES")
        pitchfork_headerLabel.setFixedHeight(25)
        pitchfork_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(pitchfork_headerLabel, 13, QFont.DemiBold)
        pitchfork_headerLayout.addWidget(pitchfork_headerLabel)
        pitchfork_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(pitchfork_header_wg)

        self.rectangle = Card_Item(FIF.RECTANGLE,"Rectangle", 'BRUSHS',self)
        self.rotated_rectangle = Card_Item(FIF.ROTATE_RECTANGLE,"Rotated Rectangle", 'BRUSHS',self)
        self.path = Card_Item(FIF.PATH,"Path", 'BRUSHS',self)
        self.circle = Card_Item(FIF.CIRCLE,"Circle", 'BRUSHS',self)
        self.elipse = Card_Item(FIF.ELIPSE,"Elipse", 'BRUSHS',self)
        self.polyline = Card_Item(FIF.POLIGON,"Polyline", 'BRUSHS',self)
        self.triangle = Card_Item(FIF.TRIANGLE,"Triangle", 'BRUSHS',self)
        self.arc = Card_Item(FIF.ARC,"Arc", 'BRUSHS',self)
        self.curve = Card_Item(FIF.CURVE,"Curve", 'BRUSHS',self)
        self.double_curve = Card_Item(FIF.DOUBLE_CURVE,"Double Curve", 'BRUSHS',self)
        

        self.menu.addWidget(self.rectangle)
        self.menu.addWidget(self.rotated_rectangle)
        self.menu.addWidget(self.path)
        self.menu.addWidget(self.circle)
        self.menu.addWidget(self.elipse)
        self.menu.addWidget(self.polyline)
        self.menu.addWidget(self.triangle)
        self.menu.addWidget(self.arc)
        self.menu.addWidget(self.curve)
        self.menu.addWidget(self.double_curve)


        
        self.splitToolButton.setFlyout(self.menu)
        
        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    
    def set_current_tool(self,tool_infor):
        tool,icon = tool_infor[0],tool_infor[1]
        self.current_tool = tool
        self.splitToolButton.change_item(icon)
        self.set_enable()
        self.sig_draw_object_name.emit((self.current_tool,self.is_enabled,"draw_trenlines"))
    def set_enable(self):
        if self.splitToolButton.button.isChecked():
            self.is_enabled = True
        else:
            self.is_enabled = False
    
    def enterEvent(self, event):
        #self.splitToolButton.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        #self.splitToolButton.dropButton.hide()
        super().leaveEvent(event)
