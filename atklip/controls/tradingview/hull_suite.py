import pandas as pd
import pandas_ta as ta
import numpy as np

class HullSuite:
    def __init__(self, df, mode='Hma', length=55, length_mult=1.0, use_htf=False, htf='240',
                 switch_color=True, candle_col=False, visual_switch=True, thickness=1, transparency=40):
        self.df = df
        self.src = df['close']
        self.mode = mode
        self.length = length
        self.length_mult = length_mult
        self.use_htf = use_htf
        self.htf = htf
        self.switch_color = switch_color
        self.candle_col = candle_col
        self.visual_switch = visual_switch
        self.thickness = thickness
        self.transparency = transparency

    def HMA(self, src, length):
        half_length = int(length / 2)
        sqrt_length = int(np.sqrt(length))
        wma1 = ta.wma(src, length)
        wma2 = ta.wma(src, half_length)
        return ta.wma(2 * wma2 - wma1, sqrt_length)

    def EHMA(self, src, length):
        half_length = int(length / 2)
        sqrt_length = int(np.sqrt(length))
        ema1 = ta.ema(src, length)
        ema2 = ta.ema(src, half_length)
        return ta.ema(2 * ema2 - ema1, sqrt_length)

    def THMA(self, src, length):
        third_length = int(length / 3)
        half_length = int(length / 2)
        wma1 = ta.wma(src, length)
        wma2 = ta.wma(src, third_length)
        wma3 = ta.wma(src, half_length)
        return ta.wma(wma2 * 3 - wma3 - wma1, length)
    
    def Mode(self, mode, src, length):
        if mode == 'Hma':
            return self.HMA(src, length)
        elif mode == 'Ehma':
            return self.EHMA(src, length)
        elif mode == 'Thma':
            return self.THMA(src, length // 2)
        else:
            return None

    def compute_hull(self):
        length_adjusted = int(self.length * self.length_mult)
        hull = self.Mode(self.mode, self.src, length_adjusted)
        return hull

    def apply(self):
        self.df['Hull'] = self.compute_hull()
        self.df['MHULL'] = self.df['Hull']
        self.df['SHULL'] = self.df['Hull'].shift(2)
        
        if self.switch_color:
            self.df['HullColor'] = np.where(self.df['Hull'] > self.df['Hull'].shift(2), '#00ff00', '#ff0000')
        else:
            self.df['HullColor'] = '#ff9800'
        
        if self.candle_col:
            self.df['BarColor'] = self.df['HullColor']
        else:
            self.df['BarColor'] = None

        return self.df

# Sample usage
if __name__ == "__main__":
    # Assuming you have a DataFrame `df` with a 'close' column
    df = pd.read_csv('path_to_your_data.csv')
    hull_suite = HullSuite(df)
    df_with_hull = hull_suite.apply()
    print(df_with_hull)