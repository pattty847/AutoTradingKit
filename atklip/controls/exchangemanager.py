import asyncio
from typing import Any, Dict
from ccxt import RequestTimeout
from .models import *
from .ta_indicators import *
from .ta_indicators import CryptoExchange,CryptoExchange_WS
from qasync import asyncSlot
from atklip.app_utils.syncer import sync

class ExchangeManager:
    def __init__(self) -> None:
        self.map_chart_exchange:Dict[str:dict] = {}

    def add_exchange(self,id_exchange,chart_id,apikey,secretkey):
        client = self.set_client_exchange(id_exchange,chart_id,apikey,secretkey)
        ws = self.set_ws_exchange(id_exchange,chart_id,apikey,secretkey)
        return client,ws
    
    def set_ws_exchange(self,id_exchange,chart_id,apikey,secretkey):
        ws = CryptoExchange_WS().setupEchange(apikey=apikey,secretkey=secretkey,exchange_name=id_exchange)
        chart = self.map_chart_exchange.get(chart_id)
        if chart == None:
            self.map_chart_exchange[chart_id] = {f"ws-{id_exchange}":ws}
        else:
            self.map_chart_exchange[chart_id].update({f"ws-{id_exchange}":ws})
        return ws

    def set_client_exchange(self,id_exchange,chart_id,apikey,secretkey):
        client = CryptoExchange().setupEchange(apikey=apikey,secretkey=secretkey,exchange_name=id_exchange)
        chart = self.map_chart_exchange.get(chart_id)
        if chart==None:
            self.map_chart_exchange[chart_id] = {f"client-{id_exchange}":client}
        else:
            self.map_chart_exchange[chart_id].update({f"client-{id_exchange}":client})
        return client
    
    def get_ws_exchange(self,id_exchange,chart_id):
        chart = self.map_chart_exchange.get(chart_id)
        if chart !=None:
            return chart.get(f"ws-{id_exchange}")
        return chart
        

    def get_client_exchange(self,id_exchange,chart_id):
        chart = self.map_chart_exchange.get(chart_id)
        if chart !=None:
            return chart.get(f"client-{id_exchange}")
        return chart
    
    async def reload_markets(self,id_exchange,chart_id):
        
        while True:
            try:
                client_socket = self.get_client_exchange(id_exchange,chart_id)
                ws_socket = self.get_ws_exchange(id_exchange,chart_id)
                
                if not client_socket or not ws_socket:
                    break
                await asyncio.sleep(60)
                ws_market = await ws_socket.load_markets(True)
                client_market = client_socket.load_markets(True)
                print(f'{client_socket} --- Markets reloaded')
            except Exception as e:
                print(type(e).__name__, str(e))
                break

    async def remove_exchange(self,id_exchange:str,chart_id):
        try:
            ws = self.get_ws_exchange(id_exchange,chart_id)
            if ws:
                try:
                    await ws.close()
                except: pass
            cl = self.get_client_exchange(id_exchange,chart_id)
            if ws:
                try:
                    cl.close()  
                except: pass
            self.map_chart_exchange[chart_id] == {}
        except:
            pass
        