from binance_lib.binanceClient import Binance_all
from binance_lib.utils import send_message_to_telegram
import pandas as pd
import time
import requests
import json


class Portfolio():
    def __init__(self):
        self.get_portfolio()
        self.params = None

    def get_portfolio(self):
        binance = Binance_all()
        """
        Get the actual portfolio where rows are valued more than 5 €
        """
        self.params = {
            "recvWindow": 6000 + 1000,
            "timestamp": int(round(time.time() * 1000)) - 2000
        }
        self.params = binance.add_signature_to_params(self.params)
        response = requests.get(binance.endpoints["account"],
                                params=self.params,
                                headers=binance.headers)
        if response.status_code != 200:
            print(f"From: {__name__}. Error while getting the data from account, error: {response.content}")
        data = json.loads(response.text)
        self.df_portfo = pd.DataFrame(data["balances"])
        # Filter assets based on value not Zero
        self.df_portfo["free"] = self.df_portfo["free"].astype("float")
        self.df_portfo["locked"] = self.df_portfo["locked"].astype("float")
        self.df_portfo = self.df_portfo[(self.df_portfo["free"]!=0) | (self.df_portfo["locked"]!=0)]
        self.df_portfo["USDT"] = 0

        eurusdt = binance.get_ticker_symbol(symbol_name="EURUSDT")
        for crypto in self.df_portfo.asset:
            if crypto == "USDT":
                self.df_portfo.loc[self.df_portfo.asset=="USDT", "USDT"] = \
                    self.df_portfo.loc[self.df_portfo.asset=="USDT"]["free"]
            elif crypto == "BCHA":
                pass
            else:
                self.df_portfo.loc[self.df_portfo.asset == crypto, "USDT"] = \
                    binance.get_ticker_symbol(crypto+"USDT") * \
                    (self.df_portfo.loc[self.df_portfo.asset == crypto]["free"] +\
                     self.df_portfo.loc[self.df_portfo.asset == crypto]["locked"])
        self.df_portfo["EUR"] = self.df_portfo["USDT"]/eurusdt
        self.message = f"The actual portfolio is of {round(self.df_portfo['EUR'].sum(),2)} €. \
                  We have invested {round(self.df_portfo.loc[self.df_portfo.asset!='USDT']['EUR'].sum(),2)} €"
        self.not_invested_usdt = round(self.df_portfo.loc[self.df_portfo.asset=='USDT']['EUR'].sum(),2)

    def last_crypto(self):
        send_message_to_telegram(self.message)
        # At the moment it is not used
        #cryptos_on_portfolio = self.df_portfo[self.df_portfo["EUR"] > 10]["asset"].to_list()



