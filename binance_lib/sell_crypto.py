from binance_lib.utils import send_message_to_telegram, upload_file_to_s3, pred_to_dynamo, get_last_pred, sellprice_to_dynamo, sellprice_from_dynamo
from binance_lib.portfolio import Portfolio
from binance_lib import variables
import boto3
from botocore.exceptions import ClientError
import datetime
import json

class SellCrypto(Portfolio):
    def __init__(self, crypto, list_sell):
        """Instantiating all the parameters"""
        self.list_sell = list_sell
        self.crypto = crypto
        self.step_size = crypto.step_size
        self.df = crypto.df
        self.symbol = crypto.symbol
        self.owned_stock_quantity = crypto.owned_stock_quantity // self.step_size / 10
        self.quantity_to_sell = crypto.quantity_to_sell
        Portfolio.__init__(self)
        self.hold = True if len(self.df_portfo[(self.df_portfo["EUR"] > 5) & (self.df_portfo["asset"].str.contains(self.symbol[:3]))]) >= 1 else False
        self.client = boto3.client('dynamodb')
        self.start_bot()

    def start_bot(self, row_number=-1):
        """test strategy for a single row"""
        if not float(self.quantity_to_sell) == 0:
            res = self.monitor_stock_4sell(row_number)
            print("Sell Check", res)


    def monitor_stock_4sell(self, row_number) -> bool:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(variables.dinamodb_table)
        try:
            response = table.get_item(Key={"symbol": self.symbol})
        except ClientError as e:
            print(e.response['Error']['Message'])
        self.buying_price = float(response["Item"]["value"])
        self.buying_time = response["Item"]["datetime"].split(".")[0]

        print(f"owned stock for symbol {self.symbol} is {self.owned_stock_quantity}")
        response = self.crypto.make_order_sell(quantity=self.quantity_to_sell)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            self.selling_price = float(json_data["fills"][0]["price"])
            self.selling_time = self.df.iloc[row_number]["time"]
            dict_selling = {
                "symbol": self.symbol,
                "buying_price": self.buying_price,
                "selling_price": self.selling_price,
                "buying_time": self.buying_time,
                "selling_time": str(self.selling_time),
                "return_perc": ((self.selling_price - self.buying_price) / self.buying_price) * 100
            }
            send_message_to_telegram(
                f"{self.symbol} SOLD, bought at price {self.buying_price}, sold at price of: {self.selling_price}, return of the investment: {round((self.selling_price - self.buying_price) / self.buying_price * 100, 2)}")
            upload_file_to_s3(dictionary=dict_selling)
        else:
            print(
                f"It was not possible to to make sell order for crypto {self.symbol}. Error: {response.content}")
        return True

