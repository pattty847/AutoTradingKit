import traceback,asyncio,time
from typing import Dict
from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal, QCoreApplication, QKeyCombination, QThreadPool,QObject
from PySide6.QtGui import QKeyEvent

from atklip.graph_objects.chart_component.base_items import CandleStick
from atklip.graph_objects.chart_component.indicators import BasicMA,BasicBB,BasicDonchianChannels
from atklip.graph_objects.chart_component import ViewPlotWidget
from atklip.exchanges import CryptoExchange
from ccxt.base.errors import *
# from ccxt.base.errors import BadSymbol
from atklip.indicators import IndicatorType,OHLCV
from atklip.indicators.candle import HEIKINASHI, SMOOTH_CANDLE,JAPAN_CANDLE, N_SMOOTH_CANDLE

from .proxy_signal import Signal_Proxy

from atklip.app_utils import *

from atklip.appmanager import FastStartThread,AppLogger,ThreadPoolExecutor_global

from atklip.graph_objects.chart_component.proxy_signal import Signal_Proxy

from atklip.graph_objects.chart_component.indicator_panel import IndicatorPanel

class Chart(ViewPlotWidget):
    def __init__(self, parent=None,apikey:str="", secretkey:str="",exchange_name:str="binanceusdm",
                 symbol:str="BTCUSDT",interval:str="1m"):
        super(Chart,self).__init__(parent=parent)
        self._parent = parent
        self.sig_reload_indicator_panel.connect(self._parent.reload_pre_indicator,Qt.ConnectionType.AutoConnection)
        self.apikey = apikey
        self.secretkey = secretkey

        self.exchange_name,self.symbol, self.interval =exchange_name, symbol,interval
        
        self.sig_reset_exchange = False
        self.is_reseting =  False
        self.worker = None
        
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(4)

        self.vb.symbol, self.vb.interval = self.symbol, self.interval
        
        self.sources: Dict[str:QObject] = {}
        self.exchanges = {}

        self.sig_add_indicator_panel.connect(self.setup_indicator,Qt.ConnectionType.AutoConnection)

        self.first_run.connect(self.set_data_dataconnect,Qt.ConnectionType.AutoConnection)
        self.fast_reset_worker(apikey=self.apikey,secretkey=self.secretkey,exchange_name=self.exchange_name,symbol=self.symbol,interval=self.interval)
        

    def add_to_exchanges(self,new_echange):
        """new_echange = {"id":"symbol_interval","exchange":Exchange,}"""
        if self.exchanges != {}:
            _list_values = list(self.exchanges.items())
            for key,echange in _list_values:
                if key == new_echange["id"]:
                    self.exchanges[new_echange["id"]] = new_echange["exchange"]
                    return
        self.exchanges[new_echange["id"]] = new_echange["exchange"]
    
    async def remove_from_exchanges(self,_id,exchange):
        print(_id,exchange)
        del self.exchanges[_id]
        if exchange.exchange != None:
            await exchange.exchange.close()
        exchange.deleteLater()
        exchange = None
    
    def get_exchange(self):
        return f"{self.symbol}_{self.interval}",self.exchanges.get(f"{self.symbol}_{self.interval}")
    
    def update_sources(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        _key = f"{self.symbol} {self.interval}"
        while True:
            for key,value in list(self.sources.items()):
                if not key.__contains__(_key):
                    del self.sources[key] 
                if value == source:
                    if key in list(self.sources.keys()):
                        del self.sources[key]
            else:
                break
        self.sources[source.source_name] = source
    
    def remove_source(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        if source.source_name in list(self.sources.keys()):
            self.sig_remove_source.emit(source.source_name)
            del self.sources[source.source_name]
            # if not isinstance(source,JAPAN_CANDLE):
            #     source.deleteLater()
    
    def get_source(self,_source_name) ->HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE:
        return self.sources[_source_name]
    
    def generate_source(self,interval):
        "Tạo source cùng symbol khác interval để phục vụ logic nếu cần"
        self.generate_source_worker(exchange_name=self.exchange_name,symbol=self.symbol,interval=interval)
    def generate_source_worker(self,exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        pass

    def on_reset_exchange(self,args):
        self.sig_show_process.emit(True)
        self.sig_reset_exchange = True
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path)"""
        #print("viwchart",args)

        _id,exchange = self.get_exchange()
        if exchange != None:
            print(exchange)
            asyncio.run(self.remove_from_exchanges(_id,exchange)) 
        
        _type, symbol, exchange_name = args[0],args[1],args[2]
        if exchange_name == self.exchange_name:
            print("same exchange")
        self.symbol = symbol
        self.exchange_name = exchange_name
        self.is_reseting =  False
        self.sig_change_tab_infor.emit((self.symbol,self.interval))
        self.fast_reset_worker(exchange_name=exchange_name,symbol=symbol,interval=self.interval)
    
    def on_change_inteval(self,args):
        """
        ("change_interval",interval)
        """
        self.sig_show_process.emit(True)
        
        _id,exchange = self.get_exchange()
        if exchange != None:
            # print(exchange)
            asyncio.run(self.remove_from_exchanges(_id,exchange)) 
        
        self.sig_reset_exchange = True
        _type, interval = args[0],args[1]
        self.interval = interval
        self.is_reseting =  False

        self.sig_change_tab_infor.emit((self.symbol,self.interval))

        self.fast_reset_worker(exchange_name=self.exchange_name,symbol=self.symbol,interval=interval)
    
    
    def fast_reset_worker(self,apikey:str="",secretkey:str="",exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        crypto_ex = CryptoExchange(self)
        new_echange = {"id":f"{symbol}_{interval}","exchange":crypto_ex,}
        self.add_to_exchanges(new_echange)
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        self.worker = None
        self.worker = FastStartThread(crypto_ex,self.reset_exchange, apikey,secretkey,crypto_ex,exchange_name,symbol,interval)
        self.worker.start_thread()
        # self.threadpool.start(self.worker)

    async def reset_exchange(self,apikey:str="",secretkey:str="",crypto_ex: CryptoExchange=None,exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        if apikey != "":
            self.apikey = apikey
        if secretkey != "":
            self.secretkey = secretkey
        
        exchange = crypto_ex.setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=exchange_name)
        # exchange.streaming['keepAlive'] = 10000 
        # exchange.streaming['maxPingPongMisses'] = 1
        
        data = []
        if exchange != None:
            data = await exchange.fetch_ohlcv(symbol,interval,limit=1500) 
        else:
             raise BadSymbol(f"{self.exchange_name} {symbol}/{interval} does not support fetch_ohlcv")
        if len(data) == 0:
            raise BadSymbol(f"{self.exchange_name} data not received")
        self.set_market_by_symbol(exchange)
        self.jp_candle.fisrt_gen_data(data,self._precision)
        self.jp_candle.source_name = f"jp {self.symbol} {self.interval}"
        self.update_sources(self.jp_candle)
        
        self.heikinashi.source_name = f"heikin {self.symbol} {self.interval}"
        self.update_sources(self.heikinashi)
        
        self.heikinashi.fisrt_gen_data()
        
        await self.loop_watch_ohlcv(crypto_ex,exchange,symbol,interval)
        
    async def loop_watch_ohlcv(self,crypto_ex,exchange,symbol,interval):
        firt_run = False
        _ohlcv = []
        while crypto_ex in list(self.exchanges.values()):
            if not (self.symbol == symbol and self.interval == interval and exchange.id == self.exchange_name):
                AppLogger.writer("INFO",f"{__name__} - {exchange.id}-{symbol}-{interval} have changed to {self.exchange_name}-{self.symbol}-{self.interval}")
                break
            if exchange != None:
                if (self.symbol == symbol and self.interval == interval and exchange.id == self.exchange_name):
                    try:
                        if "watchOHLCV" in list(exchange.has.keys()):
                            if _ohlcv == []:
                                _ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)
                                # _ohlcv[-1] = ohlcv[-1]
                            else:
                                ohlcv = await exchange.watch_ohlcv(symbol,interval,limit=2)
                                if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                    _ohlcv[-1] = ohlcv[-1]
                                else:
                                    _ohlcv.append(ohlcv[-1])
                                    _ohlcv = _ohlcv[-2:]
                                    #_ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)    
                        elif "fetchOHLCV" in list(exchange.has.keys()):
                            _ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)
                        else:
                            await asyncio.sleep(0.3)
                            continue
                    except Exception as ex:
                        await asyncio.sleep(0.3)
                        continue
                    # print(_ohlcv)
                    if len(_ohlcv) >= 2 and (self.symbol == symbol and self.interval == interval and exchange.id == self.exchange_name):
                        #print("update candle")
                        pre_ohlcv = OHLCV(_ohlcv[-2][1],_ohlcv[-2][2],_ohlcv[-2][3],_ohlcv[-2][4], round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,self._precision) , round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,self._precision), round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,self._precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                        last_ohlcv = OHLCV(_ohlcv[-1][1],_ohlcv[-1][2],_ohlcv[-1][3],_ohlcv[-1][4], round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,self._precision) , round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,self._precision), round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,self._precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                        _is_add_candle = self.jp_candle.update([pre_ohlcv,last_ohlcv])
                        
                        self.heikinashi.update( self.jp_candle.candles[-2:],_is_add_candle)
      
                        if firt_run == False:
                            self.first_run.emit()
                            #QCoreApplication.processEvents()
                            firt_run = True
                else:
                    if exchange != None:
                        AppLogger.writer("warning",f"{__name__} - {exchange.id}-{symbol}-{interval} have changed to {self.exchange_name}-{self.symbol}-{self.interval}")
                    break
            else:
                break
            try:
                await asyncio.sleep(0.3)
            except:
                pass
        if exchange != None:
            AppLogger.writer("INFO",f"{__name__} - {symbol}-{interval} have closed")
        try:
            await exchange.close()
            AppLogger.writer("INFO",f"{__name__} - {exchange.id}-{symbol}-{interval} have closed")
        except Exception as e:
            pass
        print("turn-off")
 
    async def close(self):
        while list(self.exchanges.keys()) != []:
            for key,value in list(self.exchanges.items()):
                print(key,value)
                del self.exchanges[key]
                if value.exchange != None:
                    await value.exchange.close()
                value.exchange = None
                value.deleteLater()
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        ThreadPoolExecutor_global.shutdown(cancel_futures=True)

    def set_market_by_symbol(self,exchange):
        """
        - Binance
        {'id': 'BTCUSDT', 'lowercaseId': 'btcusdt', 'symbol': 'BTC/USDT:USDT', 'base': 'BTC', 'quote': 'USDT', 
        'settle': 'USDT', 'baseId': 'BTC', 'quoteId': 'USDT', 'settleId': 'USDT', 'type': 'swap', 'spot': False, 
        'margin': False, 'swap': True, 'future': False, 'option': False, 'active': True, 'contract': True, 
        'linear': True, 'inverse': False, 'taker': 0.0004, 'maker': 0.0002, 'contractSize': 1.0, 'expiry': None, 
        'expiryDatetime': None, 'strike': None, 'optionType': None, 'precision': {'amount': 3, 'price': 1, 'base': 8, 
        'quote': 8}, 'limits': {'leverage': {'min': None, 'max': None}, 'amount': {'min': 0.001, 'max': 1000.0}, 
        'price': {'min': 556.8, 'max': 4529764.0}, 'cost': {'min': 100.0, 'max': None}, 
        'market': {'min': 0.001, 'max': 120.0}}, 'info': {'symbol': 'BTCUSDT', 'pair': 'BTCUSDT', 
        'contractType': 'PERPETUAL', 'deliveryDate': '4133404800000', 'onboardDate': '1569398400000', 
        'status': 'TRADING', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000', 'baseAsset': 'BTC', 
        'quoteAsset': 'USDT', 'marginAsset': 'USDT', 
        'pricePrecision': '2', 'quantityPrecision': '3', 'baseAssetPrecision': '8', 'quotePrecision': '8', 
        'underlyingType': 'COIN', 'underlyingSubType': ['PoW'], 'settlePlan': '0', 'triggerProtect': '0.0500', 
        'liquidationFee': '0.012500', 'marketTakeBound': '0.05', 'maxMoveOrderLimit': '10000', 
        'filters': [{'tickSize': '0.10', 'maxPrice': '4529764', 'filterType': 'PRICE_FILTER', 'minPrice': '556.80'}, 
        {'minQty': '0.001', 'stepSize': '0.001', 'filterType': 'LOT_SIZE', 'maxQty': '1000'}, 
        {'minQty': '0.001', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '120', 'stepSize': '0.001'}, 
        {'filterType': 'MAX_NUM_ORDERS', 'limit': '200'}, {'limit': '10', 'filterType': 'MAX_NUM_ALGO_ORDERS'}, 
        {'notional': '100', 'filterType': 'MIN_NOTIONAL'}, 
        {'multiplierDecimal': '4', 'multiplierUp': '1.0500', 'multiplierDown': '0.9500', 'filterType': 'PERCENT_PRICE'}], 
        'orderTypes': ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'], 
        'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX', 'GTD']}, 'created': 1569398400000}
        """
        market = exchange.market(self.symbol)
        #print(market)
        _precision = convert_precicion(market['precision']['price'])
        self.set_precision(_precision)
        #print("self._precision", self._precision)

    def get_candle(self,_type:str="japan"):
        candle = CandleStick(self,_type)
        return candle
    
    def setup_indicator(self,indicator_data):
        _group_indicator = indicator_data[0][0]
        _indicator_type = indicator_data[0][1]
        mainwindow = indicator_data[1]
        
        # print("view chart", _group_indicator,_indicator_type)
        
        if _group_indicator == "Basic Indicator":
            indicator = BasicMA(self,indicator_type=_indicator_type,period=13,_type="close",pen="#ffaa00")
            panel = IndicatorPanel(mainwindow,self, indicator)
            self.container_indicator_wg.add_indicator_panel(panel)
            self.add_item(indicator)
            indicator.threadpool_asyncworker()

        elif _group_indicator == "Candle Indicator":
            candle:CandleStick = self.get_candle(_indicator_type)
            panel = IndicatorPanel(mainwindow,self, candle)
            # self.container_indicator_wg.sig_add_panel.emit(panel)
            self.container_indicator_wg.add_indicator_panel(panel)
            #self.sig_add_item.emit(candle)
            self.add_item(candle)
            candle.first_setup_candle()
            self.auto_xrange()
            candle.source.sig_add_candle.emit(candle.source.candles[-2:])

        elif _group_indicator == "Advance Indicator":
            if _indicator_type==IndicatorType.BB:
                indicator = BasicBB(self)
                panel = IndicatorPanel(mainwindow,self, indicator)
                self.container_indicator_wg.add_indicator_panel(panel)
                self.add_item(indicator)
                indicator.threadpool_asyncworker()
            elif _indicator_type==IndicatorType.DonchianChannels:
                indicator = BasicDonchianChannels(self)
                panel = IndicatorPanel(mainwindow,self, indicator)
                self.container_indicator_wg.add_indicator_panel(panel)
                self.add_item(indicator)
                indicator.threadpool_asyncworker()
                

    def set_data_dataconnect(self):
        if self.list_candle_indicators == []:
            "load data when starting app"
            self.sig_reload_indicator_panel.emit()
        else:  
            "change interval/symbol data when starting app"
            self.jp_candle.sig_add_candle.emit(self.jp_candle.candles[-2:])
        self.sig_show_process.emit(False)
        self.is_reseting =  False
        self.sig_reset_exchange = False

    def mousePressEvent(self, ev):
        # #print(491, "press mapchart", self.fibo_reverse)
        if self.mouse_on_vb and ev.button() & Qt.MouseButton.LeftButton:
            self.mouse_clicked_signal.emit(ev)
            if self.draw_object ==  "draw_trenlines":
                self.draw_trenlines(ev)
            elif self.draw_object ==  "draw_horizontal_line":
                self.draw_horizontal_line(ev)
            elif self.draw_object ==  "draw_horizontal_ray":
                self.draw_horizontal_ray(ev)
            elif self.draw_object ==  "draw_fibo_retracement":
                self.draw_fibo(ev)
            elif self.draw_object ==  "draw_fibo_2":
                self.draw_fibo_2(ev)
            elif self.draw_object ==  "draw_rectangle":
                self.draw_rectangle(ev)
            elif self.draw_object ==  "draw_text":
                self.draw_text(ev)
            elif self.draw_object ==  "draw_path":
                self.draw_path(ev)
            elif self.draw_object == "draw_date_price_range":
                self.draw_date_price_range(ev)
            elif self.draw_object ==  "draw_verticallines":
                self.draw_verticallines(ev)
            else:
                if self.draw_object in ["drawed_trenlines", "drawed_fibo_retracement", "drawed_fibo_retracement_2", "drawed_rectangle", "drawed_date_price_range"]:
                    self.draw_object =None
                    self.drawing_object.finished = True
                    self.drawing_object.on_click.emit(self.drawing_object)
                    self.drawing_object = None
                
        super().mousePressEvent(ev)

    def roll_till_now(self,):
        vr = self.viewRect()
        height = vr.height()
        # close_price = datasrc.df.columns[2]
        y1 = self.last_close_price + height / 2
        y0 = y1 - height
        self.setYRange(y1, y0, padding=0.2)
        x1 = self.timedata[-1]
        x0 = x1 - 400*covert_time_to_sec(self.interval)
        ##print(752, "Rolling", x1, x0, self.timedata[-400])
        self.setXRange(x1, x0, padding=0.5)

    def keyPressEvent(self, ev: QKeyEvent):
        if ev.key() == Qt.Key.Key_Delete:
            pass

        elif ev.modifiers() == Qt.KeyboardModifier.AltModifier:
            #print("Enter Ctrl V",ev.keyCombination(), ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_V))
            if ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_T):
                self.draw_object = "draw_trenlines"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_H):
                self.draw_object =  "draw_horizontal_line"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_J):
                self.draw_object =  "draw_horizontal_ray"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_F):
                self.draw_object =  "draw_fibo_retracement"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_V):
                self.draw_object =  "draw_verticallines"
            # elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_J):
            #     self.draw_object ==  "draw_horizontal_ray"

        return super().keyPressEvent(ev)       
    

    