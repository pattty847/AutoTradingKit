import time
from typing import Tuple, List, TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import GraphicsObject
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.graphics.chart_component.base_items import PriceLine
from PySide6.QtCore import Signal, QObject, Qt, QRectF
from PySide6.QtGui import QColor, QPicture, QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import IndicatorType, AO
from atklip.controls.models import AOModel

from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel


class BasicAO(GraphicsObject):
    """AO"""
    on_click = Signal(object)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()

    sig_change_indicator_name = Signal(str)

    def __init__(self, get_last_pos_worker, chart, panel) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption, True)
        self.chart: Chart = chart
        self._panel: ViewSubPanel = panel

        self._precision = self.chart._precision

        self.has: dict = {
            "name": f"AO 5 34",
            "y_axis_show": True,
            "inputs": {
                "source": self.chart.jp_candle,
                "source_name": self.chart.jp_candle.source_name,
                "indicator_type": IndicatorType.AO,
                "fast": 5,
                "slow": 34,
                "price_high": 100,
                "price_low": -100,
                "show": True
            },

            "styles": {
                'pen': "yellow",
                'width': 1,
                'style': Qt.PenStyle.SolidLine,
            }
        }
        self.id = self.chart.objmanager.add(self)
        self.first_setup = False

        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)

        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        self.destroyed.connect(self.price_line.deleteLater)
        self.last_pos.connect(self.price_line.update_price_line_indicator, Qt.ConnectionType.AutoConnection)

        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)

        self.INDICATOR = AO(self.has["inputs"]["source"], self.model.__dict__)

        self.chart.sig_update_source.connect(self.change_source, Qt.ConnectionType.AutoConnection)
        self.signal_delete.connect(self.delete)

    @property
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update
        return is_updated

    @property
    def id(self):
        return self.chart_id

    @id.setter
    def id(self, _chart_id):
        self.chart_id = _chart_id

    @property
    def model(self):
        return AOModel(self.id, "AO", self.chart.jp_candle.source_name,
                       self.has["inputs"]["fast"],
                       self.has["inputs"]["slow"]
                       )

    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_indicator)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.add_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
            pass

    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_indicator, Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker, Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.add_worker, Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_historic.connect(self.add_historic_worker, Qt.ConnectionType.AutoConnection)
        self.INDICATOR.signal_delete.connect(self.replace_source, Qt.ConnectionType.AutoConnection)

    def first_gen_data(self):
        self.connect_signals()
        self.INDICATOR.started_worker()

    def delete(self):
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)

    def reset_indicator(self):
        self.first_setup = False
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data, Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self, setdata):
        xdata, y_data = self.INDICATOR.get_data()
        setdata.emit((xdata, y_data))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"""AO {self.has["inputs"]["fast"]} {self.has["inputs"]["slow"]}"""
        self.sig_change_indicator_name.emit(self.has["name"])

    def replace_source(self):
        self.update_inputs("source", self.chart.jp_candle.source_name)

    def reset_threadpool_asyncworker(self):
        self.reset_indicator()

    def change_source(self, source):
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source", source.source_name)

    def get_inputs(self):
        inputs = {"source": self.has["inputs"]["source"],
                  "fast": self.has["inputs"]["fast"],
                  "slow": self.has["inputs"]["slow"]}
        return inputs

    def get_styles(self):
        styles = {"pen": self.has["styles"]["pen"],
                  "width": self.has["styles"]["width"],
                  "style": self.has["styles"]["style"], }
        return styles

    def update_inputs(self, _input, _source):
        """Update inputs"""
        update = False

        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
            self.has["inputs"][_input] = _source
            update = True

        if update:
            self.has["name"] = f"""AO {self.has["inputs"]["fast"]} {self.has["inputs"]["slow"]}"""
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)

    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"], style=self.has["styles"]["style"])

    def get_xaxis_param(self):
        return None, "#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def set_Data(self, data):
        xData = data[0]
        yData = data[1]
        self.setData(xData, yData)
        if not self.first_setup:
            self.first_setup = True
            self.sig_change_yaxis_range.emit()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.INDICATOR.is_current_update = True

    def add_historic_Data(self, data):
        xData = data[0]
        yData = data[1]
        self.addHistoricData(xData, yData)
        self.INDICATOR.is_current_update = True

    def update_Data(self, data):
        xData = data[0]
        yData = data[1]
        self.updateData(xData, yData)
        self.INDICATOR.is_current_update = True

    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.update_Data, Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def add_historic_worker(self, _len):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data, _len)
        self.worker.signals.setdata.connect(self.add_historic_Data, Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.add_Data, Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def load_historic_data(self, _len, setdata):
        xdata, y_data = self.INDICATOR.get_data(stop=_len)
        setdata.emit((xdata, y_data))

    def update_data(self, setdata):
        xdata, y_data = self.INDICATOR.get_data(start=-2)
        setdata.emit((xdata, y_data))
        self.last_pos.emit((self.has["inputs"]["indicator_type"], y_data[-1]))
        self._panel.sig_update_y_axis.emit()

    def boundingRect(self) -> QRectF:
        return self.childrenBoundingRect()

    def paint(self, p: QPainter, *args):
        self.picture.play(p)

    def get_yaxis_param(self):
        _value = None
        try:
            _time, _value = self.get_last_point()
        except:
            pass
        if _value is not None:
            if self._precision is not None:
                _value = round(_value, self._precision)
            else:
                _value = round(_value, 3)
        return _value, "#363a45"

    def get_last_point(self):
        df = self.INDICATOR.get_df(2)
        _time = df["index"].iloc[-1]
        _value = df["AO_data"].iloc[-1]
        return _time, _value

    def get_min_max(self):
        _min = None
        _max = None
        try:
            if len(self.yData) > 0:
                _min, _max = np.nanmin(self.yData), np.nanmax(self.yData)
                return _min, _max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min, _max

    def on_click_event(self):
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name