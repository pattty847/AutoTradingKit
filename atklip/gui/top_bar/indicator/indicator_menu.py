
from typing import List
from atklip.gui.qfluentwidgets.components import SearchLineEdit
from atklip.gui.qfluentwidgets.components.container import VWIDGET,HWIDGET
from atklip.gui.qfluentwidgets import FluentIcon as FIF
from atklip.gui.components import ScrollInterface,ICON_TEXT_BUTTON,Indicator_Item,MovingWidget
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from atklip.appmanager.setting import AppConfig
from atklip.controls import IndicatorType

from PySide6.QtWidgets import QStackedWidget,QWidget
from PySide6.QtCore import Signal,Qt

class RightMenu(VWIDGET):
    def __init__(self,parent:QWidget=None):
        super(RightMenu, self).__init__(parent,"Right Menu")
        self._parent:MainMenu = parent
        self.favorites = ICON_TEXT_BUTTON(self._parent,"Favorites",FIF.FAVORITE)
        self.favorites.exchange_icon.setFixedSize(20,20)
        self.basics = ICON_TEXT_BUTTON(self._parent,"Basic Indicators",FIF.INDICATOR)
        self.subs = ICON_TEXT_BUTTON(self._parent,"Sub Indicators",FIF.INDICATOR)
        #self.profiles = ICON_TEXT_BUTTON(self._parent,"Profiles",FIF.BAR_PATTERN)
        self.patterns = ICON_TEXT_BUTTON(self._parent,"Paterns",FIF.CANDLE)
        self.candles = ICON_TEXT_BUTTON(self._parent,"Candle Idicators",FIF.CANDLE)
        self.subview = ICON_TEXT_BUTTON(self._parent,"Sub View Idicators",FIF.CANDLE)
        self.advands = ICON_TEXT_BUTTON(self._parent,"Advand Idicators",FIF.ANHCHORED_VOLUME)
        self.strategy = ICON_TEXT_BUTTON(self._parent,"Strategies",FIF.STRATEGY)
        self.addWidget(self.favorites)
        self.addWidget(self.basics)
        self.addWidget(self.subs)
        #self.addWidget(self.profiles)
        self.addWidget(self.patterns)
        self.addWidget(self.candles)
        self.addWidget(self.subview)
        self.addWidget(self.advands)
        self.addWidget(self.strategy)
        self.addSpacer()
    def get_indicator_menu(self,name):
        menu = self.findChild(ICON_TEXT_BUTTON,name)
        return menu


class BasicMenu(ScrollInterface):
    sig_add_indicator = Signal(tuple)
    sig_remove_indicator = Signal(object)
    
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(BasicMenu,self).__init__(parent)
        
        self._parent = parent
        self.sig_add_indicator_to_chart = sig_add_indicator_to_chart
        self.sig_add_remove_favorite=sig_add_remove_favorite
        self._type_indicator = "type_indicator"
        self.setObjectName(self._type_indicator)
        self.list_indicators = []
        self.dict_favorites = None
        
        self.setObjectName(self._type_indicator)
        self.sig_add_indicator.connect(self.add_Widget, Qt.ConnectionType.AutoConnection)
        self.sig_remove_indicator.connect(self.remove_Widget,Qt.ConnectionType.AutoConnection)
        self.setFixedHeight(410)
        
    def add_to_favorite_from_load(self):
        "need overwrite"
        pass

    def load_indicators(self):
        self._load_indicator()
        self.add_spacer()

    def add_spacer(self):
        self.addSpacer("VERTICAL")
    
    def _load_indicator(self):
        if self._type_indicator == "Favorites Indicator":
            self.add_to_favorite_from_load()
            return
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")

        if self.dict_favorites == None:
            AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite",{}))
            self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
        
        _list_pre_favorites = []
        if self._type_indicator in list(self.dict_favorites.keys()):
            _list_pre_favorites = self.dict_favorites[self._type_indicator]
        else:
            AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite.{self._type_indicator}",[]))
            _list_pre_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite.{self._type_indicator}")

        if self.list_indicators != []:
            for indicator in self.list_indicators:
                indicator_data = (indicator,_list_pre_favorites)
                self.sig_add_indicator.emit(indicator_data)
                # QApplication.processEvents()

    def find_item(self,name):
        item = self.findChild(Indicator_Item,name)
        return item
    
    def add_Widget(self,data):
        indicator,_list_pre_favorites = data[0], data[1]
        widget = Indicator_Item(self.sig_add_remove_favorite,self.sig_add_indicator_to_chart,self._type_indicator,indicator,self)
        if _list_pre_favorites!= []:
            if indicator.name in _list_pre_favorites:
                widget.btn_fovarite.added_to_favorite()
        self.addWidget(widget,stretch=0, alignment=Qt.AlignmentFlag.AlignTop)

    def remove_Widget(self,widget):
        self.removeWidget(widget)
    

class FavoritesIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(FavoritesIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)

        self._type_indicator = "Favorites Indicator"
        self.setObjectName(self._type_indicator)
        
        self.list_indicators = []

        self.load_indicators()
        
        #self.addSpacer("VERTICAL")
    
    def add_to_favorite_from_load(self):
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
        if self.dict_favorites == None:
            AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite",{}))
            self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
            return
        if self.dict_favorites != {}:
            for _type_indicator in list(self.dict_favorites.keys()):
                list_indicators = self.dict_favorites[_type_indicator]
                if list_indicators != []:
                    self.list_indicators += list_indicators
                for indicator in list_indicators:
                    _indicator =  IndicatorType.__getitem__(indicator)
                    indicator_data = (_type_indicator,_indicator)
                    self.sig_add_indicator.emit(indicator_data)
                    # item = Indicator_Item(self.sig_add_remove_favorite,self.sig_add_indicator_to_chart,_type_indicator,_indicator,self)
                    # item.btn_fovarite.added_to_favorite()
                    # self.sig_add_indicator.emit(item)
                    # QApplication.processEvents()
    def add_Widget(self,data):
        _type_indicator,_indicator = data[0], data[1]
        widget = Indicator_Item(self.sig_add_remove_favorite,self.sig_add_indicator_to_chart,_type_indicator,_indicator,self)
        widget.btn_fovarite.added_to_favorite()
        self.insertWidget(0,widget,stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
        # self.ins(widget,stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
class BasicIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(BasicIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)

        self._type_indicator = "Basic Indicator"
        self.setObjectName(self._type_indicator)
        
        self.list_indicators = [IndicatorType.FWMA ,
                                # IndicatorType.ALMA ,
                                IndicatorType.DEMA ,
                                IndicatorType.EMA ,
                                IndicatorType.HMA ,
                                IndicatorType.LINREG ,
                                IndicatorType.MIDPOINT,
                                IndicatorType.PWMA,
                                IndicatorType.RMA ,
                                IndicatorType.SINWMA ,
                                IndicatorType.SMA ,
                                IndicatorType.SMMA ,
                                IndicatorType.SWMA ,
                                IndicatorType.T3 ,
                                IndicatorType.TEMA ,
                                IndicatorType.TRIMA ,
                                IndicatorType.VIDYA ,
                                IndicatorType.WMA ,
                                IndicatorType.SSF ,
                                IndicatorType.ZLMA,
                                ]
        
        self.load_indicators()
        #self.addSpacer("VERTICAL")

class SubIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(SubIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)

        self._type_indicator = "Sub Indicator"
        self.setObjectName(self._type_indicator)

        self.list_indicators = [IndicatorType.VOLUME,IndicatorType.MACD,
                                IndicatorType.RSI,IndicatorType.ROC,IndicatorType.SQEEZE,
                                IndicatorType.TTM,IndicatorType.TSI, IndicatorType.VOLUMEWITHMA,
                                IndicatorType.VTX,IndicatorType.UO,
                                IndicatorType.StochRSI,IndicatorType.TRIX,
                                IndicatorType.STC,IndicatorType.Stoch,
                                IndicatorType.SOBV,IndicatorType.SFX,
                                IndicatorType.IBS,IndicatorType.MassIndex,
                                IndicatorType.OBV,IndicatorType.MeanDev,
                                IndicatorType.KVO,IndicatorType.KST,
                                IndicatorType.Ichimoku,IndicatorType.ForceIndex,
                                IndicatorType.EMV,IndicatorType.DPO,
                                IndicatorType.CoppockCurve,IndicatorType.CHOP,
                                IndicatorType.ChaikinOsc,IndicatorType.CCI,
                                IndicatorType.BOP,IndicatorType.ATR,
                                IndicatorType.Aroon,IndicatorType.AO,
                                IndicatorType.ADX,IndicatorType.AccuDist,
                                ]
        self.load_indicators()
        #self.addSpacer("VERTICAL")
class ProfilesIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(ProfilesIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)

        self._type_indicator = "Profiles Indicator"
        self.setObjectName(self._type_indicator)
        self.list_indicators = [IndicatorType.VWAP
                              ]
        self.load_indicators()
        #self.addSpacer("VERTICAL")

class ParttensIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(ParttensIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)
        self._type_indicator = "Parttens Indicator"
        self.setObjectName(self._type_indicator)
        self.list_indicators = [IndicatorType.CANDLE_PATTERN,
                                IndicatorType.CUSTOM_CANDLE_PATTERN,
                                IndicatorType.CHART_PATTERN]
        self.load_indicators()
        #self.addSpacer("VERTICAL")

class AdvanceIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(AdvanceIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)
        self._type_indicator = "Advance Indicator"
        self.setObjectName(self._type_indicator)
        self.list_indicators = [IndicatorType.ATKPRO,
                                IndicatorType.UTBOT,
                                IndicatorType.UTBOT_WITH_BBAND,
                                IndicatorType.TRENDWITHSL,
                                IndicatorType.SuperTrend,
                                IndicatorType.ATRSuperTrend,
                                
                                IndicatorType.ZIGZAG,
                                IndicatorType.BB,
                                IndicatorType.KeltnerChannels,
                                IndicatorType.DonchianChannels,
                                
                                IndicatorType.StdDev,
                                IndicatorType.ParabolicSAR,
                                IndicatorType.PivotsHL,
                                IndicatorType.McGinleyDynamic,
                                IndicatorType.KAMA,
                                
                                IndicatorType.ChandeKrollStop,
                                IndicatorType.VWAP,IndicatorType.VWMA,
                                IndicatorType.T3,
                              ]
        self.load_indicators()
        #self.addSpacer("VERTICAL")

class CandleIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(CandleIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)
        self._type_indicator = "Candle Indicator"
        self.setObjectName(self._type_indicator)

        self.list_indicators = [IndicatorType.JAPAN_CANDLE, IndicatorType.HEIKINASHI_CANDLE
                                , IndicatorType.SMOOTH_JAPAN_CANDLE, IndicatorType.SMOOTH_HEIKINASHI_CANDLE
                                , IndicatorType.N_SMOOTH_HEIKIN, IndicatorType.N_SMOOTH_JP]
        self.load_indicators()
        #self.addSpacer("VERTICAL")
        
class StrategyIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(StrategyIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)
        self._type_indicator = "Strategies"
        self.setObjectName(self._type_indicator)

        self.list_indicators = [IndicatorType.ATKBOT_SUPERTREND_SSCANDLE, IndicatorType.ATKBOT_SUPERTREND
                                , IndicatorType.ATKBOT_CCI]
        self.load_indicators()
        #self.addSpacer("VERTICAL")     
          
        
class SubViewIndicator(BasicMenu):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None,sig_add_remove_favorite=None):
        super(SubViewIndicator,self).__init__(parent,sig_add_indicator_to_chart,sig_add_remove_favorite)
        self._type_indicator = "Sub Candle Indicator"
        self.setObjectName(self._type_indicator)
        self.list_indicators = [IndicatorType.SUB_CHART]
        self.load_indicators()

class ListIndicatorMenu(QStackedWidget):
    sig_add_remove_favorite = Signal(tuple)
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None):
        super(ListIndicatorMenu,self).__init__(parent)
        self.sig_add_indicator_to_chart =sig_add_indicator_to_chart

        self.FavoritesMenu = FavoritesIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        self.BasicMenu = BasicIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        self.SubIndicatorMenu = SubIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)

        #self.ProfilesMenu = ProfilesIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        self.ParttensMenu = ParttensIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        self.AdvanceMenu = AdvanceIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)

        self.CandleMenu = CandleIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        
        self.Strategy = StrategyIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        
        self.SubView = SubViewIndicator(self,sig_add_indicator_to_chart,self.sig_add_remove_favorite)
        
        self._list_menu: List[MainMenu] = [self.FavoritesMenu,self.BasicMenu,self.SubIndicatorMenu,self.ParttensMenu,self.AdvanceMenu,self.CandleMenu,self.SubView]

        self.addWidget(self.FavoritesMenu)
        self.addWidget(self.BasicMenu)
        self.addWidget(self.SubIndicatorMenu)

        #self.addWidget(self.ProfilesMenu)
        self.addWidget(self.ParttensMenu)
        self.addWidget(self.CandleMenu)
        self.addWidget(self.SubView)
        self.addWidget(self.AdvanceMenu)
        self.addWidget(self.Strategy)
        
        #self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)

        self.sig_add_remove_favorite.connect(self.add_remove_favorite_item,Qt.ConnectionType.AutoConnection)
        
        # for menu in self._list_menu:
        #     menu.load_indicators()
    
    def add_remove_favorite_item(self,args):
        _is_add,__type_indicator,indicator = args[0],args[1],args[2]
        if _is_add:
            self.add_to_favorite(indicator,__type_indicator)
        else:
            self.remove_from_favorite(indicator,__type_indicator)

    def add_to_favorite(self,indicator,_type_indicator):
        "overwrite for favorite menu only"
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
        if _type_indicator not in list(self.dict_favorites.keys()):
            self.dict_favorites[_type_indicator] = [indicator.name]
            # item = Indicator_Item(self.sig_add_remove_favorite,self.sig_add_indicator_to_chart,_type_indicator,indicator,self)
            # item.btn_fovarite.added_to_favorite()
            self.FavoritesMenu.sig_add_indicator.emit((_type_indicator,indicator))
        else:
            if indicator.name not in self.dict_favorites[_type_indicator]:
                self.dict_favorites[_type_indicator].append(indicator.name)
                # item = Indicator_Item(self.sig_add_remove_favorite,self.sig_add_indicator_to_chart,_type_indicator,indicator,self)
                # item.btn_fovarite.added_to_favorite()
                self.FavoritesMenu.sig_add_indicator.emit((_type_indicator,indicator))
        AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite.{_type_indicator}",self.dict_favorites[_type_indicator]))
        
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")

    def remove_from_favorite(self,indicator,_type_indicator):
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
        if _type_indicator not in list(self.dict_favorites.keys()):
            return
        if indicator.name not in self.dict_favorites[_type_indicator]:
            return
        
        self.dict_favorites[_type_indicator].remove(indicator.name)
        menu = self.findChild(BasicMenu,_type_indicator)

        # print(menu)

        if isinstance(menu,BasicMenu):
            _item = menu.find_item(indicator.name)
            if isinstance(_item,Indicator_Item):
                _item.btn_fovarite.reject_from_favorite()
        _item = self.FavoritesMenu.find_item(indicator.name)
        if _item != None:
                self.FavoritesMenu.sig_remove_indicator.emit(_item)

        AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite.{_type_indicator}",self.dict_favorites[_type_indicator]))
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")

    def setCurrentWidget(self, widget):
        return super().setCurrentWidget(widget)

    def changePage(self,item_name):
        #print(item_name)
        if item_name == "Favorites":
            self.setCurrentWidget(self.FavoritesMenu)
        elif item_name == "Basic Indicators":
            self.setCurrentWidget(self.BasicMenu)
        elif item_name == "Sub Indicators":
            self.setCurrentWidget(self.SubIndicatorMenu)
        elif item_name == "Profiles":
            self.setCurrentWidget(self.ProfilesMenu)
        elif item_name == "Paterns":
            self.setCurrentWidget(self.ParttensMenu)
        elif item_name == "Advand Idicators":
            self.setCurrentWidget(self.AdvanceMenu)
        elif item_name == "Sub View Idicators":
            self.setCurrentWidget(self.SubView)
        elif item_name == "Candle Idicators":
            self.setCurrentWidget(self.CandleMenu)
        elif item_name == "Strategies":
            self.setCurrentWidget(self.Strategy)
        
    

class MainMenu(HWIDGET):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None):
        super(MainMenu,self).__init__(parent)
        self.ListIndicatorMenu = ListIndicatorMenu(self,sig_add_indicator_to_chart)
        self.rightmenu = RightMenu(self.ListIndicatorMenu)
        self.addWidget(self.rightmenu)
        self.addSeparator(_type = "VERTICAL",w=2,h=self.parent().height())
        self.addWidget(self.ListIndicatorMenu)
        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)

        

class IndicatorMenu(MovingWidget):
    def __init__(self,sig_remove_menu,sig_add_indicator_to_chart,parent:QWidget=None):
        super(IndicatorMenu, self).__init__(parent,"Indicators, Metrics & Strategies")
        self.title.btn_close.clicked.connect(sig_remove_menu,Qt.ConnectionType.AutoConnection)
        #self.setFixedWidth(700)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(700,500)
        #self.setSpacing(5)
        self.search_box = SearchLineEdit(self)
        self.search_box.setFixedHeight(35)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        self.addWidget(self.search_box)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        self.main_menu = MainMenu(self,sig_add_indicator_to_chart)
        self.addWidget(self.main_menu)
        FluentStyleSheet.INDICATORMENU.apply(self)



