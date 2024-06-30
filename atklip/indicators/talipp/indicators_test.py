import random

from atklip.indicators.talipp.indicators import AccuDist, ADX, ALMA, AO, Aroon, ATR, BB, BOP, CCI, ChaikinOsc, ChandeKrollStop, CHOP, \
    CoppockCurve, DEMA, DonchianChannels, DPO, EMA, EMV, ForceIndex, HMA, Ichimoku, KAMA, KeltnerChannels, KST, KVO, \
    MACD, MassIndex, MeanDev, OBV, PivotsHL, ROC, RSI, ParabolicSAR, SFX, SMA, SMMA, SOBV, STC, StdDev, Stoch, StochRSI, \
    SuperTrend, T3, TEMA, TRIX, TSI, TTM, UO, VTX, VWAP, VWMA, WMA, ZLEMA
from atklip.indicators.talipp.old_ohlcv import OHLCVFactory,OHLCV
import time


def generate_random_ohlcv_data(num_records):
    ohlcv_data = []
    current_price = 500  # Initial price
    n = True
    m = 0
    for _ in range(num_records):
        # Generate random OHLCV data for each record
        open_price = current_price
        high_price = open_price + random.uniform(0, 5)
        low_price = open_price - random.uniform(0, 5)
        close_price = random.uniform(low_price, high_price)
        volume = random.randint(1000, 10000)

        # Update current price for the next record
        
        if n:
            current_price = current_price + random.uniform(3, 10)
            m+=1
            if m == 10:
                n = False
                m = 0
        else:
            current_price = current_price - random.uniform(3, 10)
            m+=1
            if m == 10:
                n = True
                m = 0


        candle = OHLCV(open_price,high_price,low_price,close_price,volume,time.time())

        # Append OHLCV data to the list
        ohlcv_data.append(candle)

    return ohlcv_data


if __name__ == "__main__":

    ohlcv = generate_random_ohlcv_data(10000)
    ohlcv_update = generate_random_ohlcv_data(10000)
    spt = SuperTrend(10, 3, ohlcv)
    for i in range(1000):
        #print(spt.input_values[-1:])
        if isinstance(ohlcv_update[-i], OHLCV):
            spt.update(ohlcv_update[-i]) # example for update last candle as a sigle candle
            #spt.update([ohlcv[-i]]) # example for update last candle as a list of candles
            print(f'outputs: {len(spt.output_values)} {len(spt.output_values)} {spt.output_times[-1]} {spt.output_values[-1]}')
            time.sleep(0.1)
