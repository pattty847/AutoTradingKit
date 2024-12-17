import numpy as np
import pandas as pd
import pandas_ta as ta

from atklip.app_utils.helpers import crossover

def utsignal(data,a,c):
    # ATR Calculation
    xATR = ta.atr(data["high"], data["low"], data["close"], length=c)
    nLoss = a * xATR
    src = data["close"]
    # ATR Trailing Stop
    xATRTrailingStop = np.zeros(len(data))
    for i in range(1, len(data)):
        if src[i] > xATRTrailingStop[i - 1] and src[i - 1] > xATRTrailingStop[i - 1]:
            xATRTrailingStop[i] = max(xATRTrailingStop[i - 1], src[i] - nLoss[i])
        elif src[i] < xATRTrailingStop[i - 1] and src[i - 1] < xATRTrailingStop[i - 1]:
            xATRTrailingStop[i] = min(xATRTrailingStop[i - 1], src[i] + nLoss[i])
        else:
            xATRTrailingStop[i] = src[i] - nLoss[i] if src[i] > xATRTrailingStop[i - 1] else src[i] + nLoss[i]
    # EMA for crossover logic
    ema = ta.ema(src, length=1)
    above = (ema > xATRTrailingStop).astype(int).diff() > 0
    below = (xATRTrailingStop > ema).astype(int).diff() > 0
    return xATR,xATRTrailingStop, above, below

# Bands Calculation
def calculate_bands(data, band_type, length, std_dev):
    if band_type == "Bollinger Bands":
        bb = ta.bbands(data["close"], length=length, std=std_dev)
        _props = f"_{length}_{std_dev}"
        lower_name = f"BBL{_props}"
        mid_name = f"BBM{_props}"
        upper_name = f"BBU{_props}"
        return bb[lower_name], bb[mid_name], bb[upper_name]
    elif band_type == "Keltner Channel":
        kc = ta.kc(data, length=length)
        return kc["KCL_20"], kc["KCM_20"], kc["KCU_20"]
    elif band_type == "Donchian Channel":
        dc_high = data["high"].rolling(window=length).max()
        dc_low = data["low"].rolling(window=length).min()
        return dc_low, (dc_high + dc_low) / 2, dc_high
    else:
        return None, None, None

# Trailing Stop Calculation
def calculate_trailing_stop(data, lower, upper, atr, mult, wicks):
    dir = np.ones(len(data))
    dir[0] = 1
    long_stop = lower - atr * mult
    short_stop = upper + atr * mult

    if wicks:
        longtarget = data["low"]
        shorttarget = data["high"]
    else:
        shorttarget = data["close"]
        longtarget = data["close"]
        
    for i in range(1, len(data)):
        if dir[i - 1] == 1 and longtarget[i] < long_stop[i - 1]:
            dir[i] = -1
        elif dir[i - 1] == -1 and shorttarget[i] > short_stop[i - 1]:
            dir[i] = 1
        else:
            dir[i] = dir[i - 1]

    return dir, long_stop, short_stop

def utbot_with_bb(data,a = 1,c=10, Mult = 1, wicks=False,BandType = "Bollinger Bands", ChannelLength = 20, StdDev = 1):
    """_summary_
    Args:
        data (_type_): _description_
        a (int, optional): Key Value, this changes sensitivity. Defaults to 1.
        c (int, optional): ATR Period. Defaults to 10.
        Mult (int, optional): ATR Multiplier. Defaults to 1.
        wicks (bool, optional): _description_. Defaults to False.
        BandType (str, optional): Channel Type. Defaults to "Bollinger Bands".
        ChannelLength (int, optional): _description_. Defaults to 20.
        StdDev (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    data = data.copy()
    src = data["close"]
    xATR,xATRTrailingStop, above, below = utsignal(data,a,c)
    lower_band, middle_band, upper_band = calculate_bands(data, BandType, ChannelLength, StdDev)
    barState, buyStop, sellStop = calculate_trailing_stop(data, lower_band, upper_band, xATR, Mult, wicks)
    # Trade Conditions
    print(barState)
    buy_condition = (src > xATRTrailingStop) & above & (barState == 1)
    sell_condition = (src < xATRTrailingStop) & below & (barState == -1)
    # Output Results
    data["BuySignal"] = buy_condition
    data["SellSignal"] = sell_condition
    
    return data[["BuySignal", "SellSignal"]]


# Sample OHLC Data (replace with real data)
data = pd.DataFrame({
    "open": np.random.random(100),
    "high": np.random.random(100),
    "low": np.random.random(100),
    "close": np.random.random(100)
})

# data = utbot_with_bb(data)
import numpy as np
import pandas as pd
import pandas_ta as ta

def get_trailing_stop(df:pd.DataFrame, channel_length=20, std_dev=1.0, pd_len=22, mult=1.0, use_wicks=False):
    """
    Calculate trailing stop values based on bands and ATR for a given DataFrame.
    
    Parameters:
    - df: pandas DataFrame containing columns ['high', 'low', 'close']
    - band_type: str, type of bands ('Bollinger Bands', 'Keltner Channel', etc.)
    - channel_length: int, length of the channel calculation
    - std_dev: float, standard deviation multiplier (used in Bollinger Bands)
    - pivot_len: int, pivot length for Donchian calculations
    - pd_len: int, ATR period
    - mult: float, multiplier for ATR-based stop levels
    - use_wicks: bool, whether to use wicks (high/low) or close price for calculations
    
    Returns:
    - A DataFrame with added columns for `dir`, `long_stop`, and `short_stop`
    """
    # ATR calculation
    
    df = df.copy()
    df = df.reset_index(drop=True)
    df['atr'] = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=pd_len)
    
  
    bb = ta.bbands(data["close"], length=channel_length, std=std_dev)
    _props = f"_{channel_length}_{std_dev}"
    lower_name = f"BBL{_props}"
    mid_name = f"BBM{_props}"
    upper_name = f"BBU{_props}"
    df['upper_band'] = bb[upper_name]
    df['lower_band'] = bb[lower_name]
    
    
    # Use high/low or close for calculations
    df['long_target'] = df['low'] if use_wicks else df['close']
    df['short_target'] = df['high'] if use_wicks else df['close']
    
    # Calculate long and short stops
    df['long_stop'] = df['lower_band'] - df['atr'] * mult
    df['long_stop_prev'] = df['long_stop'].shift(1)
    df['long_stop'] = np.where(df['long_stop_prev'].isna(), df['long_stop'], 
                               np.maximum(df['long_stop'], df['long_stop_prev']))
    
    df['short_stop'] = df['upper_band'] + df['atr'] * mult
    df['short_stop_prev'] = df['short_stop'].shift(1)
    df['short_stop'] = np.where(df['short_stop_prev'].isna(), df['short_stop'], 
                                np.minimum(df['short_stop'], df['short_stop_prev']))
    
    
    df = df.iloc[max([pd_len,channel_length])+1:]
    df = df.reset_index(drop=True)
    
    # Determine direction
    df['dir'] =  np.zeros(len(df)) 
    df['dir'].iloc[0] = 1
    df['dir'] = np.where(
        (df['dir'].shift(1) == -1) & (df['short_target'] >= df['short_stop_prev']), 1,
        np.where(
            (df['dir'].shift(1) == 1) & (df['long_target'] <= df['long_stop_prev']), -1,
            df['dir'].shift(1).fillna(1)
        )
    )
    
    # Return the DataFrame with trailing stop calculations
    return df[['dir', 'long_stop', 'short_stop']]


dataa = get_trailing_stop(data)

print(dataa)
