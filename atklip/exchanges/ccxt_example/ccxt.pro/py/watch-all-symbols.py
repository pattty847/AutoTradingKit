# -*- coding: utf-8 -*-

import asyncio
import re
import ccxt.pro


async def loop(exchange, symbol, n):
    i = 0
    while True:
        try:
            orderbook = await exchange.fetch_ohlcv(symbol)
            # print every 100th bidask to avoid wasting CPU cycles on printing
            print(orderbook)
            # if not i % 100:
            #     # i = how many updates there were in total
            #     # n = the number of the pair to count subscriptions
            #     now = exchange.milliseconds()
            #     #print(exchange.iso8601(now), n, symbol, i, orderbook['asks'][0], orderbook['bids'][0])
            # i += 1
        except Exception as e:
            print(str(e), symbol)
            break
            # raise e  # uncomment to break all loops in case of an error in any one of them
            # break  # you can also break just this one loop if it fails

async def main():
    exchange = ccxt.pro.binance()
    await exchange.load_markets()
    markets = exchange.symbols
    #symbols = [market['symbol'] for market in markets if not market['darkpool']]
    #first_symbol = re.findall(r'(.*?)/', market['symbol'])
    #symbols = [market['symbol'] for market in markets if re.findall(r'(.*?):', market['symbol']) == []]
    symbols = [re.findall(r'(.*?):', market)[0] for market in markets if re.findall(r'(.*?):', market) != []]
    #symbols = [market for market in markets if re.findall(r'(.*?):', market) == []]
    #[print(maket) for maket in markets if "BTC" in maket['symbol']]
    print(symbols)
    #await asyncio.gather(*[loop(exchange, symbol, n) for n, symbol in enumerate(symbols)])
    await exchange.close()

asyncio.run(main())
