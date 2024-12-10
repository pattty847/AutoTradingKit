import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.TextItem import TextItem
# from atklip.graphics.chart_component.graph_items.CustomTextItem import TextItem

from .fillbetweenitem import FillBetweenItem
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.graphics.pyqtgraph import GraphicsObject
from atklip.graphics.chart_component.draw_tools.TargetItem import TextBoxROI


from atklip.controls import PD_MAType,IndicatorType,BBANDS, AllCandlePattern
from atklip.controls.models import BBandsModel

from atklip.appmanager import FastWorker
from atklip.app_utils import *

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart


class CandlePattern(GraphicsObject):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        GraphicsObject.__init__(self)
        # super().__init__()
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has = {
            "name": f"BB 20 2",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "mamode":PD_MAType.SMA,
                    "length":20,
                    "std_dev_mult":2,
                    "indicator_type":IndicatorType.CANDLE_PATTERN,
                    "show":False},

            "styles":{
                    'pen_high_line': "green",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_center_line': "orange",
                    'width_center_line': 1,
                    'style_center_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "red",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    
                    "brush_color": mkBrush('#3f3964',width=0.7),
                    }
                    }
        self.id = self.chart.objmanager.add(self)
        self.lowline = PlotDataItem(pen=self.has["styles"]['pen_low_line'])  # for z value
        self.lowline.setParentItem(self)
        self.centerline = PlotDataItem(pen=self.has["styles"]['pen_center_line'])
        self.centerline.setParentItem(self)
        self.highline = PlotDataItem(pen=self.has["styles"]['pen_high_line'])
        self.highline.setParentItem(self)
        
        
        self.list_patterns:dict = {}
     
        self.picture: QPicture = QPicture()
                
        self.INDICATOR  = AllCandlePattern(self.has["inputs"]["source"])
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id
        
    @property
    def model(self) -> dict:
        return BBandsModel(self.id,"BBands",self.chart.jp_candle.source_name,self.has["inputs"]["mamode"].name.lower(),
                              self.has["inputs"]["type"],self.has["inputs"]["length"],
                              self.has["inputs"]["std_dev_mult"])
    
    
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.add_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR.signal_delete.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
    
    def fisrt_gen_data(self):
        self.connect_signals()
        self.INDICATOR.started_worker()
       
    def delete(self):
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        df= self.INDICATOR.get_data()
        setdata.emit(df)
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"ALL CDL PATTERNS"
        self.sig_change_indicator_name.emit(self.has["name"])
        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "length":self.has["inputs"]["length"],
                    "std_dev_mult":self.has["inputs"]["std_dev_mult"],
                    "mamode":self.has["inputs"]["mamode"],}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_high_line":self.has["styles"]["pen_high_line"],
                    "width_high_line":self.has["styles"]["width_high_line"],
                    "style_high_line":self.has["styles"]["style_high_line"],
                    
                    "pen_center_line":self.has["styles"]["pen_center_line"],
                    "width_center_line":self.has["styles"]["width_center_line"],
                    "style_center_line":self.has["styles"]["style_center_line"],
                    
                    "pen_low_line":self.has["styles"]["pen_low_line"],
                    "width_low_line":self.has["styles"]["width_low_line"],
                    "style_low_line":self.has["styles"]["style_low_line"],
                    
                    "brush_color":self.has["styles"]["brush_color"],
                    }
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        
        if is_update:
            self.has["name"] = f"BB {self.has["inputs"]["length"]} {self.has["inputs"]["std_dev_mult"]} {self.has["inputs"]["type"]} {self.has["inputs"]["mamode"].name}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_high_line" or _input == "width_high_line" or _input == "style_high_line":
            self.highline.setPen(color=self.has["styles"]["pen_high_line"], width=self.has["styles"]["width_high_line"],style=self.has["styles"]["style_high_line"])
        elif _input == "pen_center_line" or _input == "width_center_line" or _input == "style_center_line":
            self.centerline.setPen(color=self.has["styles"]["pen_center_line"], width=self.has["styles"]["width_center_line"],style=self.has["styles"]["style_center_line"])
            # self.setPen(color=self.has["styles"]["pen_center_line"], width=self.has["styles"]["width_center_line"],style=self.has["styles"]["style_center_line"])
        elif _input == "pen_low_line" or _input == "width_low_line" or _input == "style_low_line":
            self.lowline.setPen(color=self.has["styles"]["pen_low_line"], width=self.has["styles"]["width_low_line"],style=self.has["styles"]["style_low_line"])
        elif _input == "brush_color":
            self.bb_bank.setBrush(self.has["styles"]["brush_color"])
    
    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    
    def set_Data(self,df:pd.DataFrame):
        
        if self.list_patterns:
            for obj in self.list_patterns.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["cdl_pattern"])
                    # self.scene().removeItem(obj["entry"])
                    if hasattr(obj["cdl_pattern"], "deleteLater"):
                        obj["cdl_pattern"].deleteLater()
                    # if hasattr(obj["entry"], "deleteLater"):
                    #     obj["entry"].deleteLater()
                    # 
        self.list_patterns.clear()   
        "CDL_DOJISTAR  CDL_EVENINGDOJISTAR  CDL_ENGULFING  CDL_EVENINGSTAR  CDL_MORNINGDOJISTAR  CDL_MORNINGSTAR  CDL_SHOOTINGSTAR  CDL_HARAMI  CDL_HARAMICROSS  CDL_KICKING  CDL_KICKINGBYLENGTH"
        # print(df)
        sells = df.loc[(df['evening_star'] == True)|(df['shooting_star'] == True)|(df['bearish_harami'] == True)|(df['bearish_engulfing'] == True)|(df['bearish_kicker'] == True)] 
        buys = df.loc[(df['morning_star'] == True)|(df['bullish_harami'] == True)|(df['bullish_engulfing'] == True)|(df['bullish_kicker'] == True)] 
        
        for i in range(len(sells)):
            index, text = None,None
            row = sells.iloc[i]
            if row['evening_star'] == True:
                # print(row['index'],row['evening_star'])
                index = row['index']
                text = 'evening_star'
            elif row['shooting_star'] == True:
                # print(row['index'],row['shooting_star'])
                index = row['index']
                text = 'shooting_star'
            elif row['bearish_harami'] == True:
                # print(row['index'],row['bearish_harami'])
                index = row['index']
                text = 'bearish_harami'
            elif row['bearish_engulfing'] == True:
                # print(row['index'],row['bearish_engulfing'])
                index = row['index']
                text = 'bearish_engulfing'
            elif row['bearish_kicker'] == True:
                # print(row['index'],row['bearish_kicker'])
                index = row['index']
                text = 'bearish_kicker'
                
            if index and text:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)
                    obj.setAnchor((0.5,1))
                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    obj.setPos(Point(index, ohlc.high))
                    obj.hide()
                    self.list_patterns[index] = {"cdl_pattern":obj}
                
        for i in range(len(buys)):
            index, text = None,None
            row = buys.iloc[i]
            if row['morning_star'] == True:
                # print(row['index'],row['morning_star'])
                index = row['index']
                text = 'morning_star'
            elif row['bullish_harami'] == True:
                # print(row['index'],row['bullish_harami'])
                index = row['index']
                text = 'bullish_harami'
            elif row['bullish_engulfing'] == True:
                index = row['index']
                text = 'bullish_engulfing'
            elif row['bullish_kicker'] == True:
                # print(row['index'],row['bullish_kicker'])
                index = row['index']
                text = 'bullish_kicker'
            
            
            if index and text:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)

                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    
                    obj.setAnchor((0.5,0))
                    
                    r = obj.textItem.boundingRect()
                    tl = obj.textItem.mapToParent(r.topLeft())
                    br = obj.textItem.mapToParent(r.bottomRight())
                    offset = (br - tl) * obj.anchor

                    _y = ohlc.low-offset.y()/2

                    obj.setPos(Point(index,_y))
                    self.list_patterns[index] = {"cdl_pattern":obj}
                    
                    obj.hide()
                    

    def add_historic_Data(self,df):
        sells = df.loc[(df['evening_star'] == True)|(df['shooting_star'] == True)|(df['bearish_harami'] == True)|(df['bearish_engulfing'] == True)|(df['bearish_kicker'] == True)] 
        buys = df.loc[(df['morning_star'] == True)|(df['bullish_harami'] == True)|(df['bullish_engulfing'] == True)|(df['bullish_kicker'] == True)] 
        for i in range(len(sells)):
            index, text = None,None
            row = sells.iloc[i]
            index = row['index']
            
            if self.list_patterns.get(index):
                continue
            
            if row['evening_star'] == True:
                # print(row['index'],row['evening_star'])
                text = 'evening_star'
            elif row['shooting_star'] == True:
                # print(row['index'],row['shooting_star'])
                
                text = 'shooting_star'
            elif row['bearish_harami'] == True:
                # print(row['index'],row['bearish_harami'])
               
                text = 'bearish_harami'
            elif row['bearish_engulfing'] == True:
                # print(row['index'],row['bearish_engulfing'])
                
                text = 'bearish_engulfing'
            elif row['bearish_kicker'] == True:
                # print(row['index'],row['bearish_kicker'])
                
                text = 'bearish_kicker'
                
            if index and text:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)
                    obj.setAnchor((0.5,1))
                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    obj.setPos(Point(index, ohlc.high))
                    # obj.hide()
                    self.list_patterns[index] = {"cdl_pattern":obj}
                
        for i in range(len(buys)):
            index, text = None,None
            row = buys.iloc[i]
            index = row['index']
            if self.list_patterns.get(index):
                continue
            
            if row['morning_star'] == True:
                # print(row['index'],row['morning_star'])
                
                text = 'morning_star'
            elif row['bullish_harami'] == True:
                # print(row['index'],row['bullish_harami'])
                
                text = 'bullish_harami'
            elif row['bullish_engulfing'] == True:
                
                text = 'bullish_engulfing'
            elif row['bullish_kicker'] == True:
                # print(row['index'],row['bullish_kicker'])
                
                text = 'bullish_kicker'
            
            
            if index and text:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)
                    
                    
                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    
                    obj.setAnchor((0.5,0))
                    
                    r = obj.textItem.boundingRect()
                    tl = obj.textItem.mapToParent(r.topLeft())
                    br = obj.textItem.mapToParent(r.bottomRight())
                    offset = (br - tl) * obj.anchor

                    _y = ohlc.low-offset.y()/2

                    obj.setPos(Point(index,_y))
                    self.list_patterns[index] = {"cdl_pattern":obj}
                    
                    # obj.hide()

        
    def update_Data(self,df):
        # sells = df.loc[(df['evening_star'] == True)|(df['shooting_star'] == True)|(df['bearish_harami'] == True)|(df['bearish_engulfing'] == True)|(df['bearish_kicker'] == True)] 
        # buys = df.loc[(df['morning_star'] == True)|(df['bullish_harami'] == True)|(df['bullish_engulfing'] == True)|(df['bullish_kicker'] == True)] 
        # for i in range(len(sells)):
        index, text = None,None
        row = df.iloc[0]
        index = row['index']
        if self.list_patterns.get(index):
            return
        if row['evening_star'] == True:
            # print(row['index'],row['evening_star'])
            text = 'evening_star'
        elif row['shooting_star'] == True:
            # print(row['index'],row['shooting_star'])
            text = 'shooting_star'
        elif row['bearish_harami'] == True:
            # print(row['index'],row['bearish_harami'])
            text = 'bearish_harami'
        elif row['bearish_engulfing'] == True:
            # print(row['index'],row['bearish_engulfing'])
            text = 'bearish_engulfing'
        elif row['bearish_kicker'] == True:
            # print(row['index'],row['bearish_kicker'])
            text = 'bearish_kicker'
            
        if index and text:
            ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
            if ohlc:
                obj = TextItem("",color="green")
                obj.setParentItem(self)
                obj.setAnchor((0.5,1))
                txt = text.split("_")
                txt1,txt2 = txt[0],txt[1]
                html = f"""<div style="text-align: center">
            <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                obj.setHtml(html)
                obj.setPos(Point(index, ohlc.high))
                # obj.hide()
                self.list_patterns[index] = {"cdl_pattern":obj}
                
        # for i in range(len(buys)):
        _index, _text = None,None
        _row = df.iloc[0]
        _index = row['index']
        if self.list_patterns.get(_index):
            return
        
        if _row['morning_star'] == True:
            # print(row['index'],row['morning_star'])
            _text = 'morning_star'
        elif _row['bullish_harami'] == True:
            # print(row['index'],row['bullish_harami'])
            _text = 'bullish_harami'
        elif _row['bullish_engulfing'] == True:
            _text = 'bullish_engulfing'
        elif _row['bullish_kicker'] == True:
            # print(row['index'],row['bullish_kicker'])
            _text = 'bullish_kicker'
        
        
        if _index and _text:
            ohlc =  self.chart.jp_candle.map_index_ohlcv.get(_index)
            if ohlc:
                # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                obj = TextItem("",color="green")
                obj.setParentItem(self)
                
                
                txt = _text.split("_")
                txt1,txt2 = txt[0],txt[1]
                html = f"""<div style="text-align: center">
            <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                obj.setHtml(html)
                
                obj.setAnchor((0.5,0))
                
                r = obj.textItem.boundingRect()
                tl = obj.textItem.mapToParent(r.topLeft())
                br = obj.textItem.mapToParent(r.bottomRight())
                offset = (br - tl) * obj.anchor

                _y = ohlc.low-offset.y()/2

                obj.setPos(Point(index,_y))
                self.list_patterns[index] = {"cdl_pattern":obj}
                
                # obj.hide()
    
    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
        
    def add_historic_worker(self,_len):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data,_len)
        self.worker.signals.setdata.connect(self.add_historic_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start() 
    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
    
    def load_historic_data(self,_len,setdata):
        data = self.INDICATOR.get_data(stop=_len)
        setdata.emit(data)  
    def add_data(self,setdata):
        data = self.INDICATOR.get_data(start=-2)
        setdata.emit(data)   
    
    def update_data(self,setdata):
        data = self.INDICATOR.get_data(start=-2)
        setdata.emit(data)

       
    def boundingRect(self) -> QRectF:
        if self.list_patterns:
            x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
            for _x in list(self.list_patterns.keys()):
                obj = self.list_patterns.get(_x)
                if obj:
                    if x_left < _x < x_right:
                        obj["cdl_pattern"].show()
                    else:
                        obj["cdl_pattern"].hide()

        return self.picture.boundingRect()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
        # p.drawRect(self.boundingRect())
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self.has["styles"]['pen_center_line']
    
    
    def get_last_point(self):
        return None,None
    
    def get_min_max(self):
        try:
            return None,None
        except Exception as e:
            pass
        time.sleep(0.1)
        return None,None

    def on_click_event(self):
        #print("zooo day__________________")
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    
