import requests
import boto3
import os
import time
import csv
from datetime import datetime
import json
from binance_lib import variables
import pandas as pd
import numpy as np


# Function to send a message to telegram bot
def send_message_to_telegram(bot_message):
    bot_chat_id = variables.bot_chat_id
    bot_token = variables.bot_token
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + \
                '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


# Upload dictionary to S3 Storage as json
def upload_file_to_s3(dictionary="",
                      bucket=variables.s3_bucket,
                      object_name="bot-trading-operations/" + str(datetime.now().strftime("%Y-%m")) + \
                "/" + str(int(time.time())) +".json",
                      filename="/tmp/" + str(int(time.time()))+".json"):
    if dictionary == "":
        pass
    else:
        # Saving file locally
        s3_client = boto3.client('s3')
        with open(filename, "w") as of:
            json.dump(dictionary, of)
        try:
            # Uploading file to S3
            response = s3_client.upload_file(filename,
                                                   bucket,
                                                   object_name
                                                   )
        except Exception as e:
            print("error while uploading the file to S3: ", e)
            return False
        # Removing file locally
        os.remove(filename)

def upload_pred_input_to_s3(dictionary="",
                      bucket=variables.s3_bucket,
                      object_name="",
                      filename=""):
    if dictionary == "":
        pass
    else:
        # Saving file locally
        s3_client = boto3.client('s3')
        with open(filename, "w") as of:
            json.dump(dictionary, of)
        try:
            # Uploading file to S3
            response = s3_client.upload_file(filename,
                                                   bucket,
                                                   object_name
                                                   )
        except Exception as e:
            print("error while uploading the file to S3: ", e)
            return False
        # Removing file locally
        os.remove(filename)

def pred_to_dynamo(symbol, prediction):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(variables.dinamodb_table)
    response = table.put_item(
        Item={
            "symbol": symbol + "_pred",
            "value": str(prediction),
            "datetime": str(datetime.now())
        }
    )

def sellprice_to_dynamo(symbol, sellprice):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(variables.dinamodb_table)
    response = table.put_item(
        Item={
            "symbol": symbol + "_sell",
            "value": str(sellprice),
            "datetime": str(datetime.now())
        }
    )

def sellprice_from_dynamo(symbol):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(variables.dinamodb_table)
    response = table.get_item(Key={"symbol": symbol + "_sell"})
    return response

def get_last_pred(symbol):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(variables.dinamodb_table)
    response = table.get_item(Key={"symbol": symbol + "_pred"})
    return response

s3 = boto3.resource('s3') # assumes credentials & configuration are handled outside python in .aws directory or environment variables

def download_s3_folder(s3_folder, local_dir) -> object:
    """
    Download the contents of a folder directory
    Args:
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    bucket = s3.Bucket(variables.s3_bucket)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

def save_dict_to_csv(dictionary, output_file="backtest.csv"):
    file_exist = os.path.isfile(output_file)
    with open(output_file, "a+") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=dictionary.keys())
        if file_exist:
            pass
        else:
            writer.writeheader()
        writer.writerow(dictionary)
"""
with open("binance_lib/buy_response.json") as f:
    response = json.load(f)
"""

def convert_response_for_dynamodb(response):
    dynamo_transactions_dict = {}
    dynamo_transactions_dict["transactTime"] = response["transactTime"]
    dynamo_transactions_dict["transactTimeDt"] = datetime.fromtimestamp(response["transactTime"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
    dynamo_transactions_dict["symbol"] = response["symbol"]
    dynamo_transactions_dict["side"] = response["side"]
    dynamo_transactions_dict["orderId"] = response["orderId"]
    dynamo_transactions_dict["clientOrderId"] = response["clientOrderId"]
    dynamo_transactions_dict["status"] = response["status"]
    dynamo_transactions_dict["price"] = response["fills"][0]["price"]
    dynamo_transactions_dict["qty"] = response["fills"][0]["qty"]
    dynamo_transactions_dict["commission"] = response["fills"][0]["commission"]
    return dynamo_transactions_dict

def matrix_manupilation(allocation_matrix, allocation, mom_threshold):
    allocation_matrix = allocation_matrix.T
    allocation_matrix.index = pd.Series(allocation_matrix.index).apply(lambda a: a[:-4])
    temp = allocation.df_portfo
    temp.index = allocation.df_portfo.asset
    temp = temp.drop(columns='asset')
    alloc = pd.merge(temp, allocation_matrix, how="outer", left_index=True, right_index=True)

    alloc = alloc.sort_values(by=['mom'], ascending= False)
    free_money = sum(alloc[alloc.mom < mom_threshold].USDT) + float(alloc["USDT"].iloc[np.where(alloc.index=="USDT")])

    sell_list = alloc[alloc.mom < mom_threshold]
    alloc = alloc[alloc.mom > mom_threshold]
    alloc = alloc.sort_values(by=['vola_std'], ascending=False)
    alloc["purchase_amount"] = alloc.vola_score/sum(alloc.vola_score) * free_money
    return sell_list, alloc

