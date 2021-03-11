import requests
import time
import json
import pandas as pd
from binance_lib import variables
from binance_lib.indicators import Indicators
from binance_lib.binanceClient import Binance_all
from binance_lib.portfolio import Portfolio
import datetime
import numpy as np
from binance_lib.utils import upload_pred_input_to_s3


class PurchasingStrat(Binance_all, Indicators, Portfolio):
    def __init__(self, symbol: str, interval: str, step_size: float, limit: int,
                 get_data_locally=False):
        Binance_all.__init__(self)
        self.mom_window = 96
        self.symbol = symbol
        self.step_size = step_size
        self.limit = limit
        self.interval = interval
        self.get_data_locally = get_data_locally
        self.order_book_api = self.endpoints["base_order_book"] + "?symbol=" + symbol
        self.df = self.getSymbolData()
        self.order_book = json.loads(requests.get(self.order_book_api).text)["bids"]
        Indicators.__init__(self)
        if self.symbol == "SUSHIUSDT":
            Portfolio.__init__(self)

    def getSymbolData(self):
        """ Gets trading data for one symbol """

        params = '?&symbol=' + self.symbol + '&interval=' + self.interval + "&limit=" + str(self.limit)
        url = self.endpoints['klines'] + params

        # download data
        data = requests.get(url)
        dictionary = json.loads(data.text)

        # put in dataframe and clean-up
        self.df = pd.DataFrame.from_dict(dictionary)
        self.df = self.df.drop(range(5, 12), axis=1)
        temp = self.df[0].apply(lambda a: int(str(a)[:-3]))
        self.df["hour"] = temp.apply(lambda a: datetime.datetime.fromtimestamp(a).strftime('%H'))
        # rename columns
        col_names = ['time', 'open', 'high', 'low', 'close', "hour"]
        self.df.columns = col_names

        # transform values from strings to floats
        for col in col_names:
            self.df[col] = self.df[col].astype(float)

        self.df['time'] = pd.to_datetime(self.df['time'].astype('int'), unit='ms')
        # self.df['mean_price'] = (self.df['close'] + self.df['open'])/2

        return self.df
