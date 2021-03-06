url_prediction = "http://54.93.100.39:80/predict"

purchase_amount = 40

list_cryptocurrencies = ["XRPUSDT", "ETHUSDT", "BTCUSDT", "LTCUSDT",
                             "ADAUSDT", "LINKUSDT", "BNBUSDT", "XLMUSDT",
                             "EOSUSDT", "TRXUSDT", "XMRUSDT", "DASHUSDT",
                             "MKRUSDT", "KSMUSDT", "SUSHIUSDT"]

step_sizes = {"symbol":{"52":"ADAUSDT","83":"BNBUSDT","29":"BTCUSDT","138":"DASHUSDT","107":"EOSUSDT","23":"ETHUSDT","159":"KSMUSDT","62":"LINKUSDT","38":"LTCUSDT","148":"MKRUSDT","179":"SUSHIUSDT","114":"TRXUSDT","88":"XLMUSDT","122":"XMRUSDT","2":"XRPUSDT"},"stepsize":{"52":0.1,"83":0.001,"29":0.000001,"138":0.00001,"107":0.01,"23":0.00001,"159":0.001,"62":0.01,"38":0.00001,"148":0.00001,"179":0.001,"114":0.1,"88":0.1,"122":0.00001,"2":0.1}}

# Telegram
bot_chat_id = "-398376862"
bot_token = "1585005330:AAEr1Y_pXKYS3HV58Y7JTeU-PnMcF_3RTJM"

# S3 bucket name
s3_bucket = "cryptosebimo"

# Dinamo DB table
dinamodb_table = "BobbysLookup"
