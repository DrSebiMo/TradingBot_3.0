from binance_lib.utils import send_message_to_telegram, upload_file_to_s3, pred_to_dynamo, get_last_pred, sellprice_to_dynamo, sellprice_from_dynamo
from binance_lib.portfolio import Portfolio
from binance_lib import variables
import boto3
from binance_lib.crypto import Crypto
import json
import numpy as np
import datetime

class BuyCrypto(Crypto):
    def __init__(self, crypto, purchase_amount):
        """Instantiating all the parameters"""
        #self.buy_list = alloc
        self.purchase_amount = min(float(purchase_amount), 100)
        self.crypto = crypto
        #self.step_size = step_size
        self.df = crypto.df
        self.symbol = crypto.symbol
        #self.owned_stock_quantity = purchase_amount // self.step_size / 10
        #self.quantity_to_sell = crypto.quantity_to_sell
        Portfolio.__init__(self)
        self.hold = True if len(self.df_portfo[(self.df_portfo["EUR"] > 5) & (self.df_portfo["asset"].str.contains(self.symbol[:3]))]) >= 1 else False
        #self.client = boto3.client('dynamodb')
        self.start_bot()


    def start_bot(self, row_number=-1):
        """test strategy for a single row"""
        if not float(self.purchase_amount) == 0 and not self.hold:
            res = self.monitor_stock_4buy(row_number)
            print("Buy Check", res)

    def monitor_stock_4buy(self, row_number) -> bool:
        response = self.crypto.make_order_buy(quoteOrderQty=self.purchase_amount)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            self.buying_price = json_data["fills"][0]["price"]
            self.buying_time = self.df.iloc[row_number]["time"]
            """dict_buying = {
                "symbol": self.symbol,
                "buying_price": self.buying_price,
                "buying_time": str(self.buying_time),
                "operation": "buy"
            }"""
            self.hold = True
            send_message_to_telegram(f"Bought {self.symbol} at price of: {self.buying_price}")
            # Put the buy price for the symbol in dynamodb
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(variables.dinamodb_table)
            response = table.put_item(
                Item={
                    "symbol": self.symbol,
                    "value": str(self.buying_price),
                    "datetime": str(datetime.datetime.now())
                }
            )
            print("response put item dynamodb: ", response)
        else:
            print(f"It was not possible to to make buy order for crypto {self.symbol}. Error: {response.content}")
        return True
