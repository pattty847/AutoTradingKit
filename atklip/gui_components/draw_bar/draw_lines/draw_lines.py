
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui_components.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui_components.components import ShowmenuButton,Card_Item
from atklip.gui_components import FluentIcon as FIF
# from atklip.gui_components.draw_bar import *
from atklip.gui_components.qfluentwidgets.common import *

class LINES(QFrame):
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

        self.splitToolButton = ShowmenuButton(FIF.TRENDLINE,self.parent)

        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("LINES")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)
        self.trend_line = Card_Item(FIF.TRENDLINE,"Trend Line", 'LINE',self)
        self.ray = Card_Item(FIF.RAY,"Ray", 'LINE',self)
        self.infor_line = Card_Item(FIF.INFOR_LINE,"Infor Line", 'LINE',self)
        self.extended_line = Card_Item(FIF.EXTENTED_LINE,"Extended Line", 'LINE',self)
        self.trend_angle = Card_Item(FIF.TREND_ANGLE,"Trend Angle", 'LINE',self)
        self.horizon_line = Card_Item(FIF.HORIZONTAL_LINE, "Horizontal Line", 'LINE',self)
        self.horizon_ray = Card_Item(FIF.HORIZONTAL_RAY,"Horizontal Ray", 'LINE',self)
        self.vertical_line = Card_Item(FIF.VERTICAL_LINE,"Vertical Line", 'LINE',self)
        self.cross_line = Card_Item(FIF.CROSS_LINE,"Cross Line", 'LINE',self)
        # add item to card
        self.trend_line.resize(250, 40)
        
        self.menu.addWidget(self.trend_line)
        self.menu.addWidget(self.ray)
        self.menu.addWidget(self.infor_line)
        self.menu.addWidget(self.extended_line)
        self.menu.addWidget(self.trend_angle)
        self.menu.addWidget(self.horizon_line)
        self.menu.addWidget(self.horizon_ray)
        self.menu.addWidget(self.vertical_line)
        self.menu.addWidget(self.cross_line)
        # split tool button
        self.menu.addSeparator()

        chanel_header_wg = QWidget(self.menu)
        chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        chanel_headerLabel = TitleLabel("CHANELS")
        chanel_headerLabel.setFixedHeight(25)
        chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(chanel_headerLabel, 13, QFont.DemiBold)
        chanel_headerLayout.addWidget(chanel_headerLabel)
        chanel_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(chanel_header_wg)

        self.parallel_chanel = Card_Item(FIF.PARALLEL_CHANEL,"Parallel Chanel", 'LINE',self)
        self.regression_trend = Card_Item(FIF.REGRESSION_TREND,"Regression Trend", 'LINE',self)
        self.flat_top_bottom = Card_Item(FIF.FLAT_TOP_BOTTOM,"Flat Top/Bottom", 'LINE',self)
        self.disjoint_chanel = Card_Item(FIF.DISJOINT_CHANEL,"Disjoint Chanel", 'LINE',self)
        # add item to card
        # split tool button
        self.menu.addWidget(self.parallel_chanel)
        self.menu.addWidget(self.regression_trend)
        self.menu.addWidget(self.flat_top_bottom)
        self.menu.addWidget(self.disjoint_chanel)
        self.menu.addSeparator()

        pitchfork_header_wg = QWidget(self.menu)
        pitchfork_headerLayout = QHBoxLayout(pitchfork_header_wg)
        pitchfork_headerLabel = TitleLabel("PITCHFORKS")
        pitchfork_headerLabel.setFixedHeight(25)
        pitchfork_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(pitchfork_headerLabel, 13, QFont.DemiBold)
        pitchfork_headerLayout.addWidget(pitchfork_headerLabel)
        pitchfork_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(pitchfork_header_wg)

        self.pitchfork = Card_Item(FIF.PITCHFORK,"Pitchfork", 'LINE',self)
        self.schiff_pitchfork = Card_Item(FIF.SCHIFF_PITCHFORK,"Schiff Pitchfork", 'LINE',self)
        self.modify_schiff_pitchfork = Card_Item(FIF.MODIFY_SCHIFF_PITCHFORK,"Modified Schiff Pitchfork", 'LINE',self)
        self.inside_pitchfork = Card_Item(FIF.INSIDE_PITCHFORK,"Inside Pitchfork", 'LINE',self)

        self.menu.addWidget(self.pitchfork)
        self.menu.addWidget(self.schiff_pitchfork)
        self.menu.addWidget(self.modify_schiff_pitchfork)
        self.menu.addWidget(self.inside_pitchfork)

        
        self.splitToolButton.setFlyout(self.menu)
        
        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    def enterEvent(self, event):
        #self.splitToolButton.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        #self.splitToolButton.dropButton.hide()
        super().leaveEvent(event)
