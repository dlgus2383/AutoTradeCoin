import ccxt 
import datetime
import time
import pandas as pd
from pandas.core.frame import DataFrame
import pprint
# EMA 길이 
Length = 14

# COIN NAME , TIMEFRAME , SINCE , CANDLE NUMBER , ENTRY AMOUNT ,LEVERAGE
SYMBOL         = "ETH/USDT"
SYMBOLPOSITION = "ETHUSDT"
TIMEFRAME      = '15m'
SINCE          = None
LIMIT          = 200
AMOUNT         = 0.040
LEVERAGE       = 4

# up = True , down = False , start = None
last_signal = None



# create key.txt in same folder , first line api_key , second secret_key  
with open("./key.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()


# Login
binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})


# Set Leverage
markets = binance.load_markets()
market = binance.market(SYMBOL)

resp = binance.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': LEVERAGE
})


def trendstate(df,SPAN):
    global last_signal

    # Candle ---> Heikin Ashi Candle
    # heihigh == high , heilow == low 
    heiopen  = []
    heiclose = []
    
    # first heikin Ashi candle 
    column = df.iloc[0]
    open_save = (column['open']+column['close'])/2
    close_save= (column['open']+column['close']+column['low']+column['high'])/4
    heiopen.append(open_save)
    heiclose.append(close_save)

    # anothers heikin Ashi candle
    for i in range(1,LIMIT):
        column = df.iloc[i]
        open_save  = (open_save+close_save)/2
        heiopen.append(open_save)
        close_save = (column['open']+column['high']+column['low']+column['close'])/4
        heiclose.append(close_save)
    
    # df insert heiopen and heiclose
    df['heiopen']  = heiopen
    df['heiclose'] = heiclose

    # trend 
    df['ohlc']  = (df['heiopen']+df['high']+df['low']+df['heiclose'])/4
    lis = [df['ohlc'][0]]
    temp=df['ohlc'][0]
    for i in range(1,LIMIT):
        a = (df['ohlc'][i] + temp)/2
        lis.append(a)
        temp = a
    df['haOpen'] = lis

    lis = []
    for i in range(LIMIT):
        lis.append((df['ohlc'][i]+
                    df['haOpen'][i]+
                    max(df['high'][i],df['haOpen'][i])+
                    min(df['low'][i],df['haOpen'][i]))/4)
        
                    
    df['haC'] = lis
    df['hlc3']  = (df['high']+df['low']+df['heiclose'])/3
    df['ema1']  = df['haC'].ewm(span=SPAN).mean()
    df['ema2']  = df['ema1'].ewm(span=SPAN).mean()
    df['ema3']  = df['ema2'].ewm(span=SPAN).mean()
    df['tma1']  = df['ema1']*3 - df['ema2']*3 + df['ema3']
    df['ema4']  = df['tma1'].ewm(span=SPAN).mean()
    df['ema5']  = df['ema4'].ewm(span=SPAN).mean()
    df['ema6']  = df['ema5'].ewm(span=SPAN).mean()
    df['tma2']  = df['ema4']*3 - df['ema5']*3 + df['ema6']
    df['IPEK']  = df['tma1'] - df['tma2']
    df['YASIN'] = df['tma1'] + df['IPEK']
    df['ema7']  = df['hlc3'].ewm(span=SPAN).mean()
    df['ema8']  = df['ema7'].ewm(span=SPAN).mean()
    df['ema9']  = df['ema8'].ewm(span=SPAN).mean()
    df['tma3']  = df['ema7']*3 - df['ema8']*3 + df['ema9']
    df['ema10'] = df['tma3'].ewm(span=SPAN).mean()
    df['ema11'] = df['ema10'].ewm(span=SPAN).mean()
    df['ema12'] = df['ema11'].ewm(span=SPAN).mean()
    df['tma4']  = df['ema10']*3 - df['ema11']*3 + df['ema12']
    df['IPEK1']  = df['tma3'] - df['tma4']
    df['YASIN1'] = df['tma3'] + df['IPEK1']
    df['mavi'] = df['YASIN1']
    df['kirmizi'] = df['YASIN']

    # current long or short trend 
    if(df['mavi'][-1] > df['kirmizi'][-1] and df['mavi'][-2] <= df['kirmizi'][-2]):
        currentlongCond = True
    else:
        currentlongCond = False

    if(df['mavi'][-1] < df['kirmizi'][-1] and df['mavi'][-2] >= df['kirmizi'][-2]):
        currentshortcond = True   
    else:
        currentshortcond = False
    
    # 현재는 상승 전봉은 하락 
    if(last_signal != True and currentlongCond):
        last_signal = True
        return True 
    # 현재는 하락 전봉은 상승 
    elif(last_signal != False and currentshortcond):
        last_signal = False
        return False 
    else:
        return None 
    
posi        = None
stoploss    = 0
# tradelist = []

while(True):
    # Get past data 
    btc = binance.fetch_ohlcv(
        symbol=SYMBOL, 
        timeframe=TIMEFRAME, 
        since=SINCE, 
        limit=LIMIT)        
    df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])    
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    Trend = trendstate(df,Length)

    # Get Position 수동으로 할걸을 대비 
    balance = binance.fetch_balance(params={"type": "future"})
    positions = balance['info']['positions']
    for position in positions:
        if position["symbol"] == SYMBOLPOSITION:
            Currentposition = float(position['positionAmt'])       
    # print(balance['USDT'])
    if(Currentposition == 0):
        posi        = None
        stoploss    = 0


    if(posi==True and df['close'][-1]<stoploss):
        # 롱일떄 청산 신호이니 숏 
        order = binance.create_market_sell_order(
        symbol=SYMBOL,
        amount=AMOUNT
        )
        # RESET
        stoploss = 0
        posi = None




    elif(posi==False and df['close'][-1]>stoploss):
        # 숏일떄 청산이니 롱 
        order = binance.create_market_buy_order(
        symbol=SYMBOL,
        amount=AMOUNT
        )
        # RESET
        stoploss = 0
        posi = None


        

    elif(Trend == True and posi != True):
        # 롱 진입 
        order = binance.create_market_buy_order(
        symbol=SYMBOL,
        amount=AMOUNT
        )
        # SWITCHING
        if(posi == False):
            order = binance.create_market_buy_order(
            symbol=SYMBOL,
            amount=AMOUNT
            )

        # STOPLOSS
        posi = True
        stoploss = df['low'][-2]
        print("Long Position")
    # 현제 추세는 하락과 전 추세가 하락은 아니여야함 

    elif(Trend == False and posi != False):
        # 숏 진입 
        order = binance.create_market_sell_order(
        symbol=SYMBOL,
        amount=AMOUNT
        )
        if(posi == True):
            order = binance.create_market_sell_order(
            symbol=SYMBOL,
            amount=AMOUNT
            )

        # STOPLOSS
        posi = False
        stoploss = df['high'][-2]
        print("SHORT POSITION")


    else:
        print(posi)

    time.sleep(0.5)


