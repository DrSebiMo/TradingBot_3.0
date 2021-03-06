import requests
import time
import json
import hmac
import hashlib
import os
import pandas as pd


class Binance_all():
    """
    Binance Class will have all static parameters (that do not need to be initialized)
    """
    def __init__(self):
        self.api_key = os.environ['binance_key_new']
        self.api_secret = os.environ['binance_secret_new']
        self.base_api_url = 'https://api.binance.com'
        self.not_invested_usdt = 0
        self.endpoints = {
            "order": self.base_api_url + '/api/v3/order',
            "price_ticker": self.base_api_url + "/api/v3/ticker/price",
            "oco_order": self.base_api_url + "/api/v3/order/oco",
            "base_order_book": self.base_api_url + "/api/v3/depth",
            "testOrder": self.base_api_url + '/api/v3/order/test',
            "allOrders": self.base_api_url + '/api/v1/allOrders',
            "klines": self.base_api_url + '/api/v1/klines',
            "exchangeInfo": self.base_api_url + '/api/v1/exchangeInfo',
            "statistics": self.base_api_url + '/api/v1/ticker/24hr',
            "account": self.base_api_url + '/api/v3/account',
            "symbol_ticker": self.base_api_url + "/api/v3/ticker/price",
            "user_stream": self.base_api_url + "/api/v3/userDataStream",
            "trade_list": self.base_api_url + "/api/v3/myTrades"
        }
        self.headers = {"X-MBX-APIKEY": self.api_key}

        self.params = {
            "recvWindow": 6000 + 1000,
            "timestamp": int(round(time.time() * 1000)) -1000
        }
        self.add_signature_to_params(self.params)

        # self.symbols_list = self.getTradingSymbols()
        # self.df_last24h = self.getStatisticSymbols()
        # self.top_10_symbols = self.df_last24h.sort_values("volume", ascending=False).symbol.to_list()[:10]
        # To get the step sizes - done manually at the moment
        # self.exchange_info = self.get_exchange_info()
        # self.df_last24h_columns = self.df_last24h.columns

    def get_exchange_info(self):
        url = self.endpoints["exchangeInfo"]
        response = requests.get(url)
        data = json.loads(response.content)["symbols"]
        df = pd.DataFrame(data)
        return df

    def getTradingSymbols(self) -> list:
        url = self.endpoints["exchangeInfo"]
        try:
            response = requests.get(url)
            data = json.loads(response.text)
        except Exception as e:
            print(" Exception occured when trying to access " + url)
            print(e)
        symbols_list = []
        for pair in data['symbols']:
            if pair['status'] == 'TRADING':
                if "USDT" in pair['symbol']:
                    symbols_list.append(pair['symbol'])
        return symbols_list

    def getStatisticSymbols(self) -> pd.DataFrame:
        ''' Gets last day statistics for all symbol and filtering based on USDT symbols'''
        url = self.endpoints["statistics"]
        try:
            response = requests.get(url)
            symbolsStatistic = json.loads(response.text)
        except Exception as e:
            print(" Exception occured when trying to access " + url)
            print(e)
        df = pd.DataFrame.from_dict(symbolsStatistic)
        df = df[df["symbol"].isin(self.symbols_list)]
        return df

    def get_trade_list(self, symbol="ADAUSDT"):
        params = {
            "symbol": symbol,
            "timestamp": int(round(time.time() * 1000))
        }
        self.add_signature_to_params(params)
        response = requests.get(self.endpoints["trade_list"], params=params, headers=self.headers)
        data = json.loads(response.text)
        df = pd.DataFrame(data)
        return df

    def select_crypto_by(self, column="quoteVolume", ascending=False):
        """input column to consider to filter cryptos and order"""
        self.df_last24h = self.df_last24h.sort_values(by=[column], ascending=ascending)
        list_cryptos = self.df_last24h.head(50)["symbol"].values
        list_cryptos_usdt = [i for i in list_cryptos if "USDT" in i]
        return list_cryptos_usdt

    def add_signature_to_params(self, params):
        """
        Adding Signature to params (query string) using HMAC SHA256.
        """
        query_string = "&".join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(self.api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256)
        params["signature"] = signature.hexdigest()
        return params

    def get_ticker_symbol(self, symbol_name):
        response = requests.get(self.endpoints["symbol_ticker"] + "?&symbol=" + symbol_name)
        data = json.loads(response.text)
        return float(data["price"])

