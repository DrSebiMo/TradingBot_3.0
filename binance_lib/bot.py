from binance_lib.utils import send_message_to_telegram, upload_file_to_s3, pred_to_dynamo, get_last_pred, sellprice_to_dynamo, sellprice_from_dynamo
from binance_lib.portfolio import Portfolio
from binance_lib import variables
import boto3
from botocore.exceptions import ClientError
import datetime
import json
import numpy as np

class Bot(Portfolio):
    def __init__(self, crypto, purchase_amount):
        """Instantiating all the parameters"""
        self.crypto = crypto
        self.step_size = crypto.step_size
        self.df = crypto.df
        self.symbol = crypto.symbol
        self.owned_stock_quantity = crypto.owned_stock_quantity // self.step_size / 10
        self.quantity_to_sell = crypto.quantity_to_sell
        self.buying_time = None
        self.selling_time = None
        self.price_variation = self.df.close.values[1:] - self.df.close.values[:-1] #np.nanmedian(self.df.close.values[1:] - self.df.close.values[:-1]) #crypto.df["diff_close"].median()
        self.threshold = 40

        #self. = np.quantile(self.price_variation, 0.7)
        #self.thresholdPV_down = np.quantile(self.pricthresholdPV_upe_variation, 0.3)
        #self.prediction = crypto.prediction
        try:
            self.purchase_amount = purchase_amount
        except:
            self.purchase_amount = 40
            print("Could not download last sell-price from DynamoDB")

        #self.last_prediction = float(get_last_pred(self.symbol)["Item"]["value"])
        self.latest_price = crypto.last_price
        self.buying_price: float = 0
        self.selling_price: float = 0
        Portfolio.__init__(self)
        self.hold = True if len(self.df_portfo[(self.df_portfo["EUR"] > 5) & (self.df_portfo["asset"].str.contains(self.symbol[:3]))]) >= 1 else False
        self.client = boto3.client('dynamodb')

    def start_bot(self, row_number=-1):
        """test strategy for a single row"""
        print("The current momentum is ", self.df.iloc[-1]["mom"])
        if self.hold:
            res = self.monitor_stock_4sell(row_number)
            print("Sell Check", res)
        else:
            res = self.monitor_stock_4buy(row_number)
            print("Buy Check", res)
            """if self.not_invested_usdt < variables.purchase_amount:
                print(f"Not Checking for buying because we have {self.not_invested_usdt} € available")
            else:
                res = self.monitor_stock_4buy(row_number)
                print("Buy Check", res)"""

    def monitor_stock_4buy(self, row_number) -> bool:
        if (self.df.iloc[-1]["mom"] > self.threshold) and (self.df.iloc[-1]["ma_mom_win"] < self.df.iloc[-1]["close"]):# and (self.df.iloc[-1]["mom_diff"] > 0):
            response = self.crypto.make_order_buy(quoteOrderQty=variables.purchase_amount)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                self.buying_price = json_data["fills"][0]["price"]
                self.buying_time = self.df.iloc[row_number]["time"]
                dict_buying = {
                    "symbol": self.symbol,
                    "buying_price": self.selling_price,
                    "buying_time": str(self.selling_time),
                    "operation": "buy"
                }
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
        else:
            return False


    def monitor_stock_4sell(self, row_number) -> bool:
        # Getting Buying price for the symbol in dynamodb
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(variables.dinamodb_table)
        try:
            response = table.get_item(Key={"symbol": self.symbol})
        except ClientError as e:
            print(e.response['Error']['Message'])
        self.buying_price = float(response["Item"]["value"])
        self.buying_time = response["Item"]["datetime"].split(".")[0]


        #if (self.df.iloc[-1]["mom"] < self.threshold) or (self.df.iloc[-1]["mom_diff"] < 0) or (self.df.iloc[-1]["close"] < 0.98 * self.buying_price):
        if (self.df.iloc[-1]["mom"] < self.threshold):
            print(f"owned stock for symbol {self.symbol} is {self.owned_stock_quantity}")
            response = self.crypto.make_order_sell(quantity=self.quantity_to_sell)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                self.selling_price = float(json_data["fills"][0]["price"])
                return_perc = (self.selling_price - self.buying_price) / self.buying_price

                sellprice_to_dynamo(self.symbol, self.purchase_amount * (1 + return_perc))
                self.selling_time = self.df.iloc[row_number]["time"]
                dict_selling = {
                    "symbol": self.symbol,
                    "buying_price": self.buying_price,
                    "selling_price": self.selling_price,
                    "buying_time": self.buying_time,
                    "selling_time": str(self.selling_time),
                    "return_perc": return_perc * 100
                }
                send_message_to_telegram(f"{self.symbol} SOLD, bought at price {self.buying_price}, sold at price of: {self.selling_price}, return of the investment: {round((self.selling_price - self.buying_price) / self.buying_price * 100, 2)}")
                upload_file_to_s3(dictionary=dict_selling)
            else:
                print(f"It was not possible to to make sell order for crypto {self.symbol}. Error: {response.content}")
            return True
        else:
            return False

