import ccxt 
import datetime
import time
import pandas as pd
from pandas.core.frame import DataFrame
import pprint
import ast
# EMA 길이 
Length = 14

# COIN NAME , TIMEFRAME , SINCE , CANDLE NUMBER , ENTRY AMOUNT ,LEVERAGE
SYMBOL         = "BTC/USDT"
SYMBOLPOSITION = "ETHUSDT"
TIMEFRAME      = '1h'
SINCE          = None
LIMIT          = 200
AMOUNT         = 0.040
LEVERAGE       = 4

# up = True , down = False , start = None
last_signal = None



# create key.txt in same folder , first line api_key , second secret_key  




# Set Leverage
# markets = binance.load_markets()
# market = binance.market(SYMBOL)

# resp = binance.fapiPrivate_post_leverage({
#     'symbol': market['id'],
#     'leverage': LEVERAGE
# })


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
    
    # 현봉과 , 전봉이 모두 상승하며 , 수치도 상승을 예고한다
    if(last_signal != True and currentlongCond):
        last_signal = True
        return True 
    # 현봉과 , 전봉이 모두 하강하며 , 수치도 하락을 예고한다
    elif(last_signal != False and currentshortcond):
        last_signal = False
        return False 
    else:
        return None 
    


# ttt = datetime.datetime(2021, 6, 1, 1, 1, 1)
# ttt = ttt+datetime.timedelta(minutes=1)
lia = []





stoploss    = 0
positio = None
price = 0
cha = 0
sum = 0
for q in range(5,20):
    f= open("btctesttxt30.txt",'r')
    stoploss    = 0
    positio = None
    price = 0
    cha = 0
    sum = 0
    last_signal = None
    while(True):
        line = f.readline()
        if not line: break  
        line = ast.literal_eval(line)
        
        df = pd.DataFrame(line, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])    
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        Trend = trendstate(df,q)

        # No Position 
        if(positio == None):
            if(Trend == True ):
                positio =True
                price = df['close'][-1]
                sum -= (df['close'][-1]*4)/10000
                stoploss = df['low'][-2]
                cha = price - stoploss
            elif(Trend == False):
                positio = False
                price = df['close'][-1]
                sum -= (df['close'][-1]*4)/10000
                stoploss = df['high'][-2]
                cha = stoploss-price
            else:
                pass

        # Long Position
        elif(positio == True):
            if(df['close'][-1]<stoploss):
                sum -= (df['close'][-1]*4)/10000
                positio =None
                sum -= price - stoploss
                last_signal = None
                # lia.append(stoploss-price)
                # print(datetime.datetime.now() + " Sell All Position")
            elif(Trend == False):
                sum -= (df['close'][-1]*8)/10000
                positio = False
                sum += df['close'][-1] - price
                # lia.append(df['close'][-1] - price)
            # elif(df['close'][-1] > stoploss + cha*2):
            #     stoploss += cha
        # short position
        elif(positio == False):
            if(df['close'][-1]>stoploss):
                sum -= (df['close'][-1]*4)/10000
                positio =None
                sum -= df['close'][-1] - price
                last_signal = None
                # lia.append(price-df['close'][-1])
            elif(Trend==True):
                sum -= (df['close'][-1]*8)/10000
                positio = True
                sum += price - df['close'][-1]
                # lia.append(price - df['close'][-1])
            # elif(df['close'][-1] < stoploss - cha*2):
            #     stoploss -= cha
        print(sum)
    lia.append(q)
    lia.append(sum)

    
    f.close()
print(lia)