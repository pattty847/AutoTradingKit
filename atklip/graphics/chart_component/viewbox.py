
from typing import TYPE_CHECKING

import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from atklip.graphics.pyqtgraph import functions as fn, ViewBox, InfiniteLine, mkPen, Point, PolyLineROI

from atklip.graphics.chart_component.clone_tv_indicators import FinPolyLine
from atklip.graphics.chart_component.graph_items import InfLabel

from atklip.app_utils import *

if TYPE_CHECKING:
    from .plotwidget import ViewPlotWidget



class PlotViewBox(ViewBox):
    
    load_old_data = Signal()
    update_basement_feature_signal = Signal()
    
    def __init__(self, type_chart="trading",plotwidget=None, main=None,*args, **kwds):
        kwds['enableMenu'] = False
        ViewBox.__init__(self, *args, **kwds)
        # self.setFlag(self.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        # self.setFlag(self.GraphicsItemFlag.ItemClipsToShape, True)
        # self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        # self.setFlag(self.GraphicsItemFlag.ItemContainsChildrenInShape,True)
  
        self.symbol,self.interval = None,None
        
        self.plotwidget:ViewPlotWidget = plotwidget

        self.chart = main
        
        cursor = QtGui.QCursor(Qt.CrossCursor)
        self.setCursor(cursor)
        
        self.type_chart = type_chart
        self._isMouseLeftDrag = False
        self.drawing = False
        self.draw_line = None
        self.rois = []
        self.red_box = 'background-color: #363a45;color:#363a45; border:6px solid black; margin:0px 6px;'
        self.green_box = 'background-color: #22c55e;color:#22c55e; border:6px solid black; margin:0px 6px;'
        self.state.update({

            ## separating targetRange and viewRange allows the view to be resized
            ## while keeping all previously viewed contents visible
            'targetRange': [[0,1], [0,1]],   ## child coord. range visible [[xmin, xmax], [ymin, ymax]]
            'viewRange': [[0,1], [0,1]],     ## actual range viewed

            #'yInverted': False,
            #'xInverted': False,
            #'aspectLocked': False,    ## False if aspect is unlocked, otherwise float specifies the locked ratio.
            #'autoRange': [True, True],  ## False if auto range is disabled,
                                        ## otherwise float gives the fraction of data that is visible
            #'autoPan': [False, False],         ## whether to only pan (do not change scaling) when auto-range is enabled
            #'autoVisibleOnly': [False, False], ## whether to auto-range only to the visible portion of a plot
            #'linkedViews': [None, None],  ## may be None, "viewName", or weakref.ref(view)
                                          ## a name string indicates that the view *should* link to another, but no view with that name exists yet.
            #'defaultPadding': defaultPadding,

            'mouseEnabled': [True, True],
            'mouseMode': ViewBox.PanMode,#ViewBox.PanMode if getConfigOption('leftButtonPan') else ViewBox.RectMode,
            'enableMenu': True,
            'wheelScaleFactor': -1/70,

            'background': "#313335",
            
            #'logMode': [False, False],

            # Limits
            # maximum value of double float is 1.7E+308, but internal caluclations exceed this limit before the range reaches it.
            'limits': { 
                'xLimits': [-1E307, +1E307],   # Maximum and minimum visible X values
                'yLimits': [-1E307, +1E307],   # Maximum and minimum visible Y values
                'xRange': [None, None],   # Maximum and minimum X range
                'yRange': [None, None],   # Maximum and minimum Y range
                }
        })
        
        self.setLimits(minXRange=100, maxXRange=1440)
    def makepen(self,color, style=None, width=1):
        if style is None or style == '-':
            return mkPen(color=color, width=width)
        dash = []
        for ch in style:
            if ch == '-':
                dash += [4, 2]
            elif ch == '_':
                dash += [10, 2]
            elif ch == '.':
                dash += [1, 2]
            elif ch == ' ':
                if dash:
                    dash[-1] += 2
        return mkPen(color=color, style=Qt.PenStyle.CustomDashLine, dash=dash, width=width)
    def draw_line_postion(self, price, position="long"):
        color = "#ff0e0e" if position == "short" else "#11f227"
        back_ground = (14, 203, 129, 200) if position == "long" else (246, 70, 93, 200)
        line_l = InfiniteLine(angle=0, movable=False,
                                 pen=self.makepen(color, style='.'),
                                 label="P",
                                 labelOpts={'rotateAxis': [1, 0], 'fill': back_ground, 'movable': True, 'position': 0.1,
                                            'color': "#f6f6f7"})
        line_l.setPos(price)
        line_l.setName(position)
        line_l.setZValue(999)
        self.addItem(line_l, ignoreBounds=True)
        return line_l

    def draw_line_last_price(self, price):
        color = "#027df7"
        line_l = InfiniteLine(angle=0, movable=False, pen=self.makepen(color, style='.', width=2),)
        line_l.setPos(price)
        line_l.setName("last_price")
        line_l.setZValue(999)
        self.addItem(line_l, ignoreBounds=True)
        return line_l
    
    
    def draw_line_edges(self, points, precision=4, order="long", isOpen=False):   #  Real Mode\
        # print(2094, points)
        color = "#22c55e" if order == "long" else "#363a45"
        price = float(points[0].y())
        line_infinity = InfiniteLine(angle=0, movable=False,
                                 pen=mkPen(color),)
        line_infinity.setPos(points[0].y())
        line_infinity.setName(f"{price}")
        line_infinity.precision = precision
        line_infinity.price = price
        if isOpen:
            side = "O"
            line_infinity.setZValue(72)
        else:
            side = "C"
        self.addItem(line_infinity, ignoreBounds=False)
        text = self.addLabelToLine(line_infinity, price, precision, color, side)
        return line_infinity

    def addLabelToLine(self, line_infinity, price, precision, color, side="O"):
        html_status = f"<div><span style='{self.red_box}'> _ </span>_<span style='{self.green_box}'> _ </span>_<span style='{self.red_box}'> _ </span>_<span style='{self.green_box}'> _ </span>"
        html_openclose = f"<span style='background-color: {color};'>{side}"
        html_price =f"{round(price, precision)}</span></div>"
        html = html_status + "_" + html_openclose + " " + html_price
        text = InfLabel(line_infinity, movable=True, anchor=(0.5, -1.0), html=html, border={'color': color}, position= 0.96)
        text.line = line_infinity
        if hasattr(line_infinity, "accompany_items"):
            line_infinity.accompany_items["text_status"] = text
        else:
            line_infinity.accompany_items = {
                "text_status": text
            }
        text.price = round(price, precision)
        text.html_status = html_status
        text.html_openclose = html_openclose
        text.html_price = html_price
        font = QFont()
        font.setPixelSize(9)
        text.setFont(font)

        text.setParentItem(line_infinity)
        if side == "O":
            text.setAbove()
        else:
            text.setBelow()
        text.updatePosition()
        self.addItem(text)
        return text
    
    def wheelEvent(self, ev, axis=None):
        self.load_old_data.emit()
        y_range = (self.plotwidget.yAxis.range[1] + self.plotwidget.yAxis.range[0])/2
        x_range = self.plotwidget.xAxis.range[1]
        tr = self.targetRect()
        # if tr.right() - tr.left() >=1440 and ev.delta() < 0:
        #     "giới hạn 1440 candle trên viewchart"
        #     if axis == None or axis == 0:
        #         return True
        
        if axis is None:
                mask = [True, False]   # Zom theo trục x
        elif axis == 1:
                mask = [False, True]
        elif axis == 0:
                mask = [True, False]
        else:
            mask = [True, False]

        s = 1.02 ** (ev.delta() * self.state['wheelScaleFactor']) # actual scaling factor
        s = [(None if m is False else s) for m in mask]
        #center = Point(fn.invertQTransform(self.LiveViewBox.childGroup.transform()).map(ev.pos()))
        center = Point(x_range,y_range)
        self._resetTarget()
        self.scaleBy(s, center)
        self.sigRangeChangedManually.emit(mask)
        ev.accept()
    
    def mouseDragEvent(self, ev, axis=None):
        self.load_old_data.emit()
        
        pos = ev.pos()
        lastPos = ev.lastPos()
        dif = pos - lastPos
        dif = dif * -1

        ## Ignore axes if mouse is disabled
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float64)
        mask = mouseEnabled.copy()
        if axis is not None:
            mask[1-axis] = 0.0
        
        if ev.button() == Qt.MouseButton.LeftButton:    
            self.mouseLeftDrag(ev, axis, mouseEnabled, mask)
        elif ev.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddleDrag(ev, axis, dif, mask)
        elif ev.button() == Qt.MouseButton.RightButton:
            self.mouseRightDrag(ev, mouseEnabled, mask)
        else:
            super().mouseDragEvent(ev, axis)

        # ev.accept()  ## we accept all buttons
        ## if axis is specified, event will only affect that axis.

    def mouseMiddleDrag(self, ev, axis=None, dif=None, mask=None):
        return
        return super().mouseDragEvent(ev, axis)
        # if self.state['mouseMode'] == ViewBox.RectMode and axis is None:
        #     if ev.isFinish():  ## This is the final move in the drag; change the view scale now
        #         #print "finish"
        #         self.rbScaleBox.hide()
        #         ax = QRectF(Point(ev.buttonDownPos(ev.button())), Point(ev.pos()))
        #         ax = self.childGroup.mapRectFromParent(ax)
        #         self.showAxRect(ax)
        #         self.axHistoryPointer += 1
        #         self.axHistory = self.axHistory[:self.axHistoryPointer] + [ax]
        #     else:
        #         ## update shape of scale box
        #         self.updateScaleBox(ev.buttonDownPos(), ev.pos())
        # else:
        #     tr = self.childGroup.transform()
        #     tr = fn.invertQTransform(tr)
        #     tr = tr.map(dif*mask) - tr.map(Point(0,0))

        #     x = tr.x() if mask[0] == 1 else None
        #     y = tr.y() if mask[1] == 1 else None

        #     self._resetTarget()
        #     if x is not None or y is not None:
        #         self.translateBy(x=x, y=y)
        #     self.sigRangeChangedManually.emit(self.state['mouseEnabled'])

    def mouseRightDrag(self, ev, mouseEnabled, mask):
        #print "vb.rightDrag"
        if ev.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.state['aspectLocked'] is not False:
                mask[0] = 0
            dif = ev.screenPos() - ev.lastScreenPos()
            dif = np.array([dif.x(), dif.y()])
            # gioi han nen trong khung hinh
            tr = self.targetRect()
            x0 = tr.left()
            x1 = tr.right()
            # print(159, x1-x0)
            # if x1 - x0  >= 1440 and dif[0] < 0:
            #     "giới hạn 1440 candle trên viewchart"
            #     return True
                
            dif[0] *= -1
            s = ((mask * 0.02) + 1) ** dif

            tr = self.childGroup.transform()
            tr = fn.invertQTransform(tr)

            x = s[0] if mouseEnabled[0] == 1 else None
            y = s[1] if mouseEnabled[1] == 1 else None

            center = Point(tr.map(ev.buttonDownPos(Qt.MouseButton.RightButton)))
            self._resetTarget()
            self.scaleBy(x=x, y=y, center=center)
            self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        if ev.isFinish():
            self.drawing = False
        ev.accept()
    
    def mouseLeftDrag(self, ev, axis, mouseEnabled, mask):
        if axis in [0,1]:
            #print(axis)
            #print "vb.rightDrag"
            if self.state['aspectLocked'] is not False:
                mask[0] = 0

            dif = ev.screenPos() - ev.lastScreenPos()
            
            dif = np.array([dif.x()/4, dif.y()/4])
            dif[0] *= 1   # Điều chỉnh hệ số giản, -1 là chỉ số gốc, đã modified để giống binance khi kéo trục x
            s = ((mask * 0.02) + 1) ** dif  # tính toán hệ số zoom của trục x,y. <1 thì co vào, >1 thì giản ra, =1 không thay đổi

            tr = self.childGroup.transform()
            #print(tr)
            tr = fn.invertQTransform(tr)
            #print(tr)

            x = s[0] if mouseEnabled[0] == 1 else None
            y = s[1] if mouseEnabled[1] == 1 else None
            
            y_range = (self.plotwidget.getAxis('right').range[1] + self.plotwidget.getAxis('right').range[0])/2
        
            x_range = self.plotwidget.getAxis('bottom').range[1]

            #center = Point(tr.map(ev.buttonDownPos(QtCore.Qt.MouseButton.LeftButton)))
            
            center = Point(x_range, y_range)
            
            self._resetTarget()
            self.scaleBy(x=x, y=y, center=center)
            self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        '''Shift+LButton draw lines.'''
        if ev.modifiers() != Qt.KeyboardModifier.ShiftModifier:
            super().mouseDragEvent(ev, axis)
            if ev.isFinish():
                self._isMouseLeftDrag = False
            else:
                self._isMouseLeftDrag = True
            # if ev.isFinish() or self.drawing:
            #     self.refresh_all_y_zoom()

            if not self.drawing:
                return
     
        ev.accept() 

    def mouseClickEvent(self, ev):
        #print(460, "press vbox")
        
        if self.plotwidget.is_cutting_replay:
            mouse_point = self.mapSceneToView(ev.pos())
            nearest_idx = find_nearest_index(self.plotwidget.timedata, mouse_point.x())
            
            self.plotwidget.timedata = self.plotwidget.timedata[:nearest_idx]
            self.plotwidget.data = self.plotwidget.data[:nearest_idx]


            self.plotwidget.is_cutting_replay = False
            cursor = QtGui.QCursor(Qt.CrossCursor)
            self.setCursor(cursor)
            self.plotwidget.show_crosshair()
         
            
        if mouse_clicked(self, ev):
            ev.accept()
            return
        if ev.button() != Qt.MouseButton.LeftButton or ev.modifiers() != Qt.KeyboardModifier.ShiftModifier or not self.draw_line:
            return super().mouseClickEvent(ev)
        # add another segment to the currently drawn line
        p = self.mapClickToView(ev.pos())
        # p = _clamp_point(self.parent(), p)
        # print(858, self.parent(), p)

        self.append_draw_segment(p)
        self.drawing = False
        ev.accept()

    def mapClickToView(self, pos):
        '''mapToView() does not do grids properly in embedded widgets. Strangely, only affect clicks, not drags.'''
        if self.win.parent() is not None:
            ax = self.parent()
            if ax.getAxis('right').grid:
                pos.setX(pos.x() + self.width())
            elif ax.getAxis('bottom').grid:
                pos.setY(pos.y() + self.height())
        return super().mapToView(pos)

    def append_draw_segment(self, p):
        h0 = self.draw_line.handles[-1]['item']
        h1 = self.draw_line.addFreeHandle(p)
        self.draw_line.addSegment(h0, h1)
        self.drawing = True

    # chua dung den, dang dung ben mapchart roll_till_now
    # loi roll deen nam 1970
    def roll_x_to_last(self, datasrc_x, close_price):
        if datasrc_x is None:
            return
        vr = self.viewRect()
        height = vr.height()

        # close_price = datasrc.df.columns[2]
        y1 = close_price + height / 2
        y0 = y1 - height
        x0, x1 = xminmax(datasrc_x, x_indexed=True, init_steps=300, extra_margin=0)
        # self.set_range(x0, y0, x1, y1)
        print(482, "Rolling", x0, x1)

        self.setXRange(x0, x1, padding=0.5)
        self.setYRange(y0, y1, padding=0)

    def set_draw_line_color(self, color):
        if self.draw_line:
            pen = mkPen(color)
            for segment in self.draw_line.segments:
                segment.currentPen = segment.pen = pen
                segment.update()
