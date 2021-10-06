import ccxt 
import datetime
import time
import pandas as pd
from pandas.core.frame import DataFrame
import pprint
import sys

SYMBOL         = "ETH/USDT"
SYMBOLPOSITION = "ETHUSDT"
TIMEFRAME      = '15m'
SINCE          = None
LIMIT          = 200
AMOUNT         = 0.040
LEVERAGE       = 4

binance = ccxt.binance(config={
    'apiKey': '7QuvskcNR5pG1jkGopiSxNlaPGeMMp68kVhpjt5fOjsHdsLa178SPv5a3crqSnCK',
    'secret': '7Vhfs9EVEvu85C4gPQVoXzNyAl63cr5TFBSYpJCYUO9tWf8QGkM0xCsNX439GJp2',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})






f = open('testtxt.txt','a')
while(True):
    try:
        
        btc = binance.fetch_ohlcv(
            symbol   =SYMBOL, 
            timeframe=TIMEFRAME, 
            since    =SINCE, 
            limit    =LIMIT)    
        print(btc,file=f)
        time.sleep(1)

    except : 
        pass
f.close()