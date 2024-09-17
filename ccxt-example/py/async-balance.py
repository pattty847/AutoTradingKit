# -*- coding: utf-8 -*-

import asyncio
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt.async_support as ccxt  # noqa: E402


async def test():
    bittrex = ccxt.binanceusdm({
        'apiKey': "zhBF9X2mhD7rY6fpFU243biBtE4ySGpXTBPdYYOExyx27G5CrU6cCEditBhO7ek4",
        'secret': "6rIYDN1xBaxxGyuLslYGMxlHFtjgzhVh6nV4zO8IKaspdF1H3tC5MKXMgxA1rHDA",
        'verbose': False,  # switch it to False if you don't want the HTTP log
    })
    print(await bittrex.fetch_balance())
    await bittrex.close()


asyncio.run(test())
