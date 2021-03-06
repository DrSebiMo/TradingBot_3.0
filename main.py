from binance_lib.crypto import Crypto
from binance_lib.bot import Bot
import pandas as pd
from binance_lib import variables
from binance_lib.utils import sellprice_to_dynamo
from binance_lib.utils import download_s3_folder

df = pd.DataFrame(variables.step_sizes)
df = df.set_index("symbol")

if __name__ == '__main__':
    for crypto in variables.list_cryptocurrencies:
        #crypto = "ETHUSDT"
        print(f"Evaluating crypto {crypto}")
        #sellprice_to_dynamo(crypto, 45)
        try:
            step_size = df.loc[crypto]["stepsize"]
            cryptocurrency = Crypto(symbol=crypto, interval="15m", step_size=step_size, limit=500)
            print(f"Starting Bot for {crypto}")
            Bot(cryptocurrency).start_bot()
            if crypto == "SUSHIUSDT":
                cryptocurrency.last_crypto()
        except Exception as e:
            print(f"Error for {crypto}: {e}")







