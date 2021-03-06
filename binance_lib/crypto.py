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


class Crypto(Binance_all, Indicators, Portfolio):
    def __init__(self, symbol: str, interval: str, step_size: float, limit: int = 500,
                 get_data_locally=False):
        Binance_all.__init__(self)
        self.mom_window = 96
        self.symbol = symbol
        self.step_size = step_size
        self.limit = limit
        self.interval = interval
        self.trend = 0
        self.get_data_locally = get_data_locally
        self.order_book_api = self.endpoints["base_order_book"] + "?symbol=" + symbol
        if self.get_data_locally:
            self.df = pd.read_parquet(f"data/test_strategy/{self.symbol}.parquet")
        else:
            self.df = self.getSymbolData()

        self.order_book = json.loads(requests.get(self.order_book_api).text)["bids"]
        Indicators.__init__(self)
        Portfolio.__init__(self)
        self.df = self.df.drop(columns=["hour"])
        #del self.df['hour']
        #self.prediction = self.get_prediction()
        self.last_price = self.df["close"].iloc[-1]
        try:
            self.hold = (self.df_portfo.loc[self.df_portfo.asset.str.contains(symbol[:3])]["EUR"] > 10).values[0]
        except:
            print(f"Not possible to find hold for stock {symbol}. Setting it to False")
            self.hold = False
        locator = [True if self.symbol[:3] in x else False for x in self.df_portfo["asset"].values]
        self.owned_stock_quantity = self.df_portfo.loc[locator]["free"].sum()
        self.quantity_to_sell = self.format_value(self.owned_stock_quantity - self.step_size/2, self.step_size)
        self.orderID = None

    def get_prediction(self):
        try:
            array_prediction = self.df.iloc[-50:, 1:]
            array_prediction_list = array_prediction.values.tolist()
            dict_for_pred = {'array': str(array_prediction_list), "symbol": self.symbol}
            #np.save('test_dict.npy', dict_for_pred)
            response = upload_pred_input_to_s3(dictionary= dict_for_pred,
                                               object_name= "pred_inp/" + "pred_inp_" + str(self.symbol) + ".json",
                                               filename= "/tmp/" + "pred_inp_" + str(self.symbol) +".json")
            res = requests.post(variables.url_prediction, data=dict_for_pred, timeout=3)
            prediction = float(res.content)
            print(f"prediction for {self.symbol} is {prediction}")
        except:
            prediction = None
            print("It was not possible to get the prediction from the API")
        return prediction

    def step_size_to_precision(self, ss):
        return format(ss, ".10f").find('1') - 1

    def format_value(self, val, step_size_str):
        precision = self.step_size_to_precision(step_size_str)
        return "{:0.0{}f}".format(val, precision)

    def get_ticker(self) -> float:
        """
        return: last price for the symbol
        """
        response = requests.get(self.endpoints["symbol_ticker"] + "?&symbol=" + self.symbol)
        data = json.loads(response.text)
        return float(data["price"])

    def save_df_locally(self, path=""):
        if path == "":
            path = f"data/test_strategy/{self.symbol}.parquet"
        self.df.to_parquet(path)

    def make_order_buy(self, quoteOrderQty: float):
        """
        We buy in quoteOrderQty: USDT
        """
        self.params = {
            "symbol": self.symbol,
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": quoteOrderQty,
            "timestamp": int(round(time.time() * 1000)) - 1000
        }
        self.add_signature_to_params(self.params)
        response = requests.post(self.endpoints["order"], params=self.params, headers=self.headers)
        return response


    def make_order_sell(self, quantity: float):
        """
        We sell in symbol quantity: symbol (all the quantity)
        """
        self.params = {
            "symbol": self.symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": int(round(time.time() * 1000)) - 1000
        }
        self.add_signature_to_params(self.params)

        response = requests.post(self.endpoints["order"], params=self.params, headers=self.headers)
        return response


    def getSymbolData(self,):
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
        #self.df['mean_price'] = (self.df['close'] + self.df['open'])/2

        return self.df




