import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#from sklearn.linear_model import LinearRegression

from pyti.bollinger_bands import lower_bollinger_band as lbb
from pyti.bollinger_bands import upper_bollinger_band as ubb

class Indicators:
    def __init__(self, price_column: str = "close", df: pd.DataFrame = pd.DataFrame()):
        if df.shape[0] > 0:
            self.df = df
        #self.df['true_price'] = (self.df["high"] + self.df["close"] + self.df["low"]) / 3
        self.price_column = price_column
        self.create_indicators()

    def create_indicators(self):

            min_mom = self.mom_window
            self.df['ma_mom_win'] = self.df["close"].rolling(window=self.mom_window).mean()
            self.df['pct_change'] = self.df['close'].pct_change()
            self.df['norm_close'] = (self.df['close'] - min(self.df['close']))/max(self.df['close'] - min(self.df['close']))

            def linreg_np(x, y):
                coeffs = np.polyfit(x, y, 1)
                p = np.poly1d(coeffs)
                yhat = p(x)
                ybar = np.sum(y) / len(y)
                ssreg = np.sum((yhat - ybar) ** 2)
                sstot = np.sum((y - ybar) ** 2)
                r_sq = ssreg / sstot
                slope = coeffs[0]
                return slope, r_sq


            def mom_score(ts):
                x = np.arange(len(ts))
                y = np.log(ts)

                slope, r_sq =  linreg_np(x,y)
                scaler = 1 * 4 * 24
                scaled_slope = (np.power(np.exp(slope), scaler) - 1) * 100
                return scaled_slope * (r_sq ** 2)

            def mom_score_lin(ts):
                x = np.arange(len(ts))
                y=ts
                slope, r_sq = linreg_np(x, y)
                scaler = 1 * 4 * 24
                scaled_slope = np.multiply(slope, scaler) * 100
                #scaled_slope = (np.power(np.exp(slope), scaler) - 1) * 100

                """coeffs = np.polyfit(x, y, 1)
                p = np.poly1d(coeffs)
                plt.plot(x, y, 'yo', x, p(x), '--k')
                plt.title(self.symbol)

                plt.show()"""

                return scaled_slope * (r_sq ** 2)

            def vola_score(ts):
                x = np.arange(len(ts))
                #y = np.log(ts)
                y = (ts - min(ts))/max(ts - min(ts))
                _, r_sq = linreg_np(x, y)
                return r_sq

            self.df['mom'] = self.df['norm_close'].rolling(self.mom_window, min_periods=min_mom).apply(
                mom_score).reset_index(level=0, drop=True)

            self.df['mom_lin'] = self.df['norm_close'].rolling(self.mom_window, min_periods=min_mom).apply(
                mom_score_lin).reset_index(level=0, drop=True)

            """y = self.df.close[-96:]
            x = np.arange(len(y))

            a, b = linreg_np(x, y)
            a = 1 * 4 * 24 * a"""

            self.df['vola_score'] = self.df['norm_close'].rolling(self.mom_window, min_periods=min_mom).apply(
                vola_score).reset_index(level=0, drop=True)

            self.df['mom_diff'] = self.df['mom'].diff()

            self.df['vola_std'] = self.df['close'].pct_change().rolling(self.mom_window).std()

