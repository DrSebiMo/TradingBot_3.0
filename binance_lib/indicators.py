import pandas as pd
import numpy as np
#from sklearn.linear_model import LinearRegression

from pyti.bollinger_bands import lower_bollinger_band as lbb
from pyti.bollinger_bands import upper_bollinger_band as ubb

class Indicators:
    def __init__(self, price_column: str = "close", df: pd.DataFrame = pd.DataFrame()):
        if df.shape[0] > 0:
            self.df = df
        self.df['true_price'] = (self.df["high"] + self.df["close"] + self.df["low"]) / 3
        self.price_column = price_column
        self.create_moving_average_der([3, 5, 10])
        self.create_ema_der([3, 5, 10])
        self.create_MACD([[12, 26, 9], [8, 21, 5], [6, 27, 5], [12, 26, 3]])
        self.create_indicators()




    def create_moving_average_der(self, params: list = []):
        for param in params:
            self.df[f"ma{param}"] = self.df["close"].rolling(window=param).mean()
            self.df[f"diff_ma{param}"] = self.df[f"ma{param}"].diff()

    def create_ema_der(self, params:list = []):
        for param in params:
            self.df[f"ema{param}"] = pd.Series.ewm(self.df["close"], span=param).mean()
            self.df[f"diff_ema{param}"] = self.df[f"ema{param}"].diff()

    def create_MACD(self, params: list = []):
        for param in params:
            #param [12, 26, 9]
            ema_short = pd.Series.ewm(self.df[self.price_column], span=param[0]).mean()
            ema_long = pd.Series.ewm(self.df[self.price_column], span=param[1]).mean()
            self.df[f'macd{param[0]}_{param[1]}'] = ema_short - ema_long
            self.df[f'macdSignal{param[2]}'] = pd.Series.ewm(self.df[f'macd{param[0]}_{param[1]}'], span=param[2]).mean()
            self.df[f'diff_macd{param[0]}_{param[1]}'] = self.df[f'macd{param[0]}_{param[1]}'].diff()
            self.df[f'diff_macdSignal{param[2]}'] = self.df[f'macdSignal{param[2]}'].diff()

    def create_indicators(self):
            # Calculating the True Prices (used in bollinger bands)
            #self.df['true_price'] = (self.df["high"] + self.df["close"] + self.df["low"])/3
            #self.df["MA_TP"] = self.df['true_price'].rolling(20).mean()
            #self.df['mean_price'] = (self.df["high"] + self.df["low"])/2
            #self.df["is_green_candlestick"] = self.df["close"] - self.df["open"] > 0
            #self.df["MA_TP_diff"] = self.df['MA_TP'].diff(1)
            #self.df["MA_TP_diff_ma3"] = self.df["MA_TP_diff"].rolling(3).mean()
            #self.df["MA_TP_diff_ma5"] = self.df['MA_TP_diff'].rolling(5).mean()
            #self.df["MA_TP_diff_ma10"] = self.df['MA_TP_diff'].rolling(10).mean()
            #self.df["MA_TP_diff_ma20"] = self.df['MA_TP_diff'].rolling(20).mean()
            #self.df["speed"] = self.df["close"] - self.df["open"]
            #self.df["diff_close"] = self.df["close"].diff()
            #self.df["diff_close_hourly"] = self.df["diff_close"].rolling(4).sum()

            #self.df["diff_macd6_27"] = self.df["macd6_27"].diff()


            # Capture Anomalies in single candlestick
            #self.df['max_min'] = self.df['high'] - self.df['low']
            # Positive if going up (positive comparable with max_mim)
            #self.df['up_pct'] = self.df['close'] - self.df['low']
            # Positive if going down (positive comparable with max_mim)
            #self.df['down_pct'] = self.df['high'] - self.df['close']


            #self.df["positive_trend_last24"] = ((self.df["diff_ma20"] > 0).rolling(window=96).sum())/96



            # Percentage Changes
            #self.df['pct_change3'] = self.df['true_price'].pct_change(3)
            #self.df['pct_change5'] = self.df['true_price'].pct_change(5)

            # Calculating the RSI (usually over last 14 closing prices)
            # It is a momentum Oscillator
            # RS is the relative strength (AvgGain/AvgLoss)
            # RSI = 100 - 100/(1+RS)
            #window_length = 10
            #delta = self.df['close'].diff()


            # Make the positive gains (up) and negative gains (down) Series
            #up, down = delta.copy(), delta.copy()
            #up[up < 0] = 0
            #down[down > 0] = 0

            # Calculate the EWMA
            #roll_up1 = up.ewm(span=window_length).mean()
            #roll_down1 = down.abs().ewm(span=window_length).mean()

            # Calculate the RSI based on EWMA
            #RS1 = roll_up1 / roll_down1
            #RSI1 = 100.0 - (100.0 / (1.0 + RS1))
            #self.df["RSI_ewm"] = RSI1
            #self.df["RSI_ewm_ma3"] = self.df["RSI_ewm"].rolling(window=3).mean()
            #self.df["RSI_ewm_ma3_diff"] = self.df["RSI_ewm_ma3"].diff()

            # Calculate the SMA
            #roll_up2 = up.rolling(window_length).mean()
            #roll_down2 = down.abs().rolling(window_length).mean()

            # Calculate the RSI based on SMA
            #RS2 = roll_up2 / roll_down2
            #RSI2 = 100.0 - (100.0 / (1.0 + RS2))
            #self.df["RSI_sma"] = RSI2

            # Stochastic Oscillator
            # Most recent closing price
            """self.df["CP"] = self.df["close"].shift(1)
            self.df["L14"] = self.df["low"].rolling(14).min()
            self.df["H14"] = self.df["high"].rolling(14).max()
            self.df["fast_k"] = 100 * (self.df["CP"] - self.df["L14"]) / (self.df["H14"]-self.df["L14"])
            self.df["fast_D"] = self.df["fast_k"].rolling(3).mean()

            self.df["slow_k"] = self.df["fast_k"].rolling(3).mean()
            self.df["slow_D"] = self.df["slow_k"].rolling(3).mean()

            self.df["H3"] = self.df["high"].rolling(3).max()
            self.df["L3"] = self.df["low"].rolling(3).min()
            self.df["D_line_diff"] = self.df["fast_D"].diff()


            # Bollinger Bands
            self.df['lbb'] = lbb(self.df[self.price_column], 20)
            self.df['ubb'] = ubb(self.df[self.price_column], 20)

            # Bollinger Bands True Price
            self.df['lbb_tp'] = lbb(self.df["true_price"], 20)
            self.df['ubb_tp'] = ubb(self.df["true_price"], 20)


            # MACD 12 26 true price
            self.df['ema12_tp'] = pd.Series.ewm(self.df["true_price"], span=12).mean()
            self.df['ema26_tp'] = pd.Series.ewm(self.df["true_price"], span=26).mean()
            self.df['macd_tp_12'] = self.df['ema12_tp'] - self.df['ema26_tp']
            self.df['macdSignal_tp_12'] = pd.Series.ewm(self.df["macd_tp_12"], span=9).mean()

            # MACD 8 21 true price
            self.df['ema8_tp'] = pd.Series.ewm(self.df["true_price"], span=12).mean()
            self.df['ema21_tp'] = pd.Series.ewm(self.df["true_price"], span=26).mean()
            self.df['macd_tp_8'] = self.df['ema8_tp'] - self.df['ema21_tp']
            self.df['macdSignal_tp_8'] = pd.Series.ewm(self.df["macd_tp_8"], span=5).mean()
            """

            min_mom = self.mom_window

            def mom_score(ts):
                x = np.arange(len(ts))
                y = np.log(ts)

                slope = (len(x) * np.sum(x * y) - np.sum(x) * np.sum(y)) /(len(x) * np.sum(x * x) - np.sum(x) ** 2)
                r_sq = (np.sum(y) - slope * np.sum(x)) / len(x)
                coeff = 1 * 4 * 24
                scaled_slope = (np.power(np.exp(slope), coeff) - 1) * 100
                return scaled_slope * (r_sq ** 2)

            self.df['mom'] = self.df['close'].rolling(self.mom_window, min_periods=min_mom).apply(
                mom_score).reset_index(level=0,
                                       drop=True)

            self.df['mom_diff'] = self.df['mom'].diff()

