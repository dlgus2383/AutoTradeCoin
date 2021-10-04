import ccxt 
import datetime
import time
import pandas as pd
from pandas.core.frame import DataFrame

# EMA 길이 
Length = 9

# 가져올 코인과 분봉 정보 
SYMBOL = "ETH/USDT"
TIMEFRAME = '1m'
# SINCE = binance.parse8601('2018-07-24T00:00:00Z')
SINCE = None
LIMIT = 200

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
    

    # long or short trend 
    # if(df['mavi'][-2] > df['kirmizi'][-2] and df['mavi'][-3] <= df['kirmizi'][-3]):
    #     beforelongCond = True
    # else:
    #     beforelongCond = False

    # if(df['mavi'][-2] < df['kirmizi'][-2] and df['mavi'][-3] >= df['kirmizi'][-3]):
    #     beforeshortcond = True   
    # else:
    #     beforeshortcond = False


    # 현재는 상승 전봉은 하락 
    if(((last_signal == None)  or (last_signal == False)) and currentlongCond):
        last_signal = True
        return True 
    # 현재는 하락 전봉은 상승 
    elif(currentshortcond and  ((last_signal == None)  or (last_signal == True))):
        last_signal = False
        return False 
    else:
        return None 
    



    
# ttt = datetime.datetime(2020, 12, 12, 3, 3, 3)

# ema 1:2798 2:-15490 3:-15550 4:-45587 5:2896 6:2671 7:2614 8:2500 9:2348 10:2014
# 백테스팅을 위한 자료 (삭제 예정)
# ttt = datetime.datetime(2020, 12, 12, 3, 3, 3)
# ttt = ttt+datetime.timedelta(minutes=1)
# SINCE = binance.parse8601(ttt.strftime('%Y-%m-%d %H:%M:%S'))
# for _ in range(4000):
# 백테스팅을위한 자료 (삭제 예정)
# ttt = ttt+datetime.timedelta(minutes=1)
# SINCE = binance.parse8601(ttt.strftime('%Y-%m-%d %H:%M:%S'))
# 백테스팅을 위한 자료 (삭제 예정)

# i = EmaLength
sum         = 0
long        = 0
short       = 0
last_signal = None
posi        = None
stoploss    = 0
# tradelist = []
ttt = datetime.datetime(2021, 5, 27, 1, 1, 1)
tr  = 2
fai = 1

# while(True):
for j in range(15000):
    ttt = ttt+datetime.timedelta(minutes=1)
    btc = binance.fetch_ohlcv(
        symbol=SYMBOL, 
        timeframe=TIMEFRAME, 
        since=binance.parse8601(ttt.strftime('%Y-%m-%d %H:%M:%S')),            # SINCE, 
        limit=LIMIT)        
    df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])    
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    # 75ema 180ema 540ema 그리고 633em
    # 1min ema 9 : 0.457 ,10 : 0.439 , 11 : 0.431 , 12 : 0.431 , 13 : 0.425 , 14: 0.458 , 15 : 0.448 , 16:0.441
    # 5min ema 9 : 0.42  ,10 :
    # 1min ema 9 14가 상당히 정확하다. 내일 표본을 5000개로 늘리고 두개 승률을 비교하자  
    # 1min 6:45.8% 7:44.8%  8:44.1%  9:44.3% 13  10:41.2%  11: 41.5%  : 40.6% 14 : 40.9%
    a = trendstate(df,Length)

    # 손절가 없이 오로지 스위칭으로만 조사

    # 만약 롱 포지션이 stoploss 이하로 떨어지거나 숏 포지션이 stoploss 이상으로 올라가면 포지션 종료 
    # 아래 if 를 elif 로 만들고 위 내용을 if 로 만듬 lastsignal은 None로 초기화 
    if(posi==True and df['heiclose'][-1]<stoploss):
        print("stoploss : " ,stoploss , "   long = ", long, "     stoploss - long :",stoploss-long)
        sum -= ((df['close'][-1])*4)/10000
        sum += stoploss - long
        # tradelist.append(stoploss - long)
        stoploss = 0
        long = 0
        posi = None

        fai += 1


    elif(posi==False and df['heiclose'][-1]>stoploss):
        print("stoploss : " ,stoploss , "   short = ", short, "     short - stoploss :",short - stoploss)
        sum -= ((df['close'][-1])*4)/10000
        sum += short - stoploss
        # tradelist.append(short - stoploss)
        stoploss = 0
        short = 0
        posi = None

        fai += 1
        

    elif(a == True and posi != True):
        sum -= ((df['close'][-1])*4)/10000
        long = df['close'][-1]
        if(posi == False):
            print("short - long = ",short - long  )
            # tradelist.append(short - long)
            sum += short - long  
            posi = True
            if(short - long<0):
                fai+=1

            short = 0



        else:
            posi = True
        stoploss = df['low'][-2]
        print("long signal")
        tr += 1

        # if 만약 숏 포지션이 있을경우 
        #   스위칭 개념으로 목표가에 2배 매수 
        # else 만약 포지션이 없을경우 
        #   바이낸스 매수


        # print("Long Position")
        # long = df['high'][-1]
    elif(a == False and posi != False):
        sum -= ((df['close'][-1])*4)/10000
        short = df['close'][-1]
        if(posi == True):
            print("short - long = ",short - long  )
            # tradelist.append(short - long)
            sum += short - long
            if(short - long<0):
                fai +=1
            posi = False
            long = 0


        else:
            posi = False
        stoploss = df['high'][-2]
        print("short signal")
        tr +=1
        # if 롱 포지션이 있을경우
        #   2배 매도 
        # 만약 포지션이 없을경우 
        #   그냥 매도 
        # print("Short Position")
    else:
        # if 포지션이 있을경우
        #   현재 포지션 표시 
        # else 없을경우 
        # print("No Postion")
        # print("try : ",tr,"   fail : ",fai,"    win rate : ",(tr-fai)/tr)
        # ,"         last signal = ",last_signal,"    stoploss = ",stoploss,"    long = ",long,"  short = ",short
        print("sum = ", sum)
        print("try : ",tr,"   fail : ",fai,"    win rate : ",(tr-fai)/tr)
    time.sleep(0.1)


