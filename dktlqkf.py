import ccxt 
import datetime
import time
import pandas as pd
from pandas.core.frame import DataFrame
import pprint




# COIN NAME 
SYMBOL1         = "BTC/USDT"
SYMBOLPOSITION1 = "BTCUSDT"

SYMBOL2         = "ETH/USDT"
SYMBOLPOSITION2 = "ETHUSDT"

SYMBOL3         = "BNB/USDT"
SYMBOLPOSITION3 = "BNBUSDT"

SYMBOL4         = "XRP/USDT"
SYMBOLPOSITION4 = "XRPUSDT"

SYMBOL5         = "DOGE/USDT"
SYMBOLPOSITION5 = "DOGEUSDT"

# TIMEFRAME , SINCE , LIMIT , EMALENGTH
TIMEFRAME      = '30m'
SINCE          = None
LIMIT          = 200


# ENTRY AMOUNT 
# BTCAMOUNT         = 0.002
# ETHAMOUNT         = 0.004
# BNBAMOUNT         = 0.03
# XRPAMOUNT         = 13.3
# DOGEAMOUNT        = 64
BTCAMOUNT         = 0.001
ETHAMOUNT         = 0.002
BNBAMOUNT         = 0.01
XRPAMOUNT         = 6.3
DOGEAMOUNT        = 32

# LEVERAGE
BTCLEVERAGE       = 10
ARTLEVERAGE       = 2






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
    'options': {'defaultType': 'future'}
})

# Set Leverage
markets    = binance.load_markets()
btcmarket  = binance.market(SYMBOL1)
ethmarket  = binance.market(SYMBOL2)
bnbmarket  = binance.market(SYMBOL3)
xrpmarket  = binance.market(SYMBOL4)
dogemarket = binance.market(SYMBOL5)


    

stoploss    = 0


class server:
    def __init__(self , le , coi):
        self.ema = le
        self.posi = 0
        self.sum  = 0 
        self.stoploss = 0
        self.coin = coi
        self.last_signal = None
        self.df = []
    def trendstatus(self, df):
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
        df['ema1']  = df['haC'].ewm(span=self.ema).mean()
        df['ema2']  = df['ema1'].ewm(span=self.ema).mean()
        df['ema3']  = df['ema2'].ewm(span=self.ema).mean()
        df['tma1']  = df['ema1']*3 - df['ema2']*3 + df['ema3']
        df['ema4']  = df['tma1'].ewm(span=self.ema).mean()
        df['ema5']  = df['ema4'].ewm(span=self.ema).mean()
        df['ema6']  = df['ema5'].ewm(span=self.ema).mean()
        df['tma2']  = df['ema4']*3 - df['ema5']*3 + df['ema6']
        df['IPEK']  = df['tma1'] - df['tma2']
        df['YASIN'] = df['tma1'] + df['IPEK']
        df['ema7']  = df['hlc3'].ewm(span=self.ema).mean()
        df['ema8']  = df['ema7'].ewm(span=self.ema).mean()
        df['ema9']  = df['ema8'].ewm(span=self.ema).mean()
        df['tma3']  = df['ema7']*3 - df['ema8']*3 + df['ema9']
        df['ema10'] = df['tma3'].ewm(span=self.ema).mean()
        df['ema11'] = df['ema10'].ewm(span=self.ema).mean()
        df['ema12'] = df['ema11'].ewm(span=self.ema).mean()
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
        if(self.last_signal != True and currentlongCond):
            self.last_signal = True
            return True 
        # 현봉과 , 전봉이 모두 하강하며 , 수치도 하락을 예고한다
        elif(self.last_signal != False and currentshortcond):
            self.last_signal = False
            return False 
        else:
            return None  

    def Get_sum(self):
        return self.sum
    def GET_last_signal(self):
        return self.last_signal
    def Getdf(self):
        coin = binance.fetch_ohlcv(
        symbol   = self.coin,
        timeframe= '1m', 
        since    = None, 
        limit    = 200
        )
        self.df = pd.DataFrame(coin, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        self.df['datetime'] = pd.to_datetime(self.df['datetime'], unit='ms')     
        self.df.set_index('datetime', inplace=True)
        return self.df
    
    def trade(self):
        Trend = self.trendstatus(self.Getdf())
        if(self.posi==0):
            if(Trend == True):
                self.posi  = self.df['close'][-1]
                self.sum  -= (self.df['close'][-1]*4)/10000
                self.stoploss = self.df['low'][-2]
            elif(Trend == False):
                self.posi        = -self.df['close'][-1]
                self.sum        -= (self.df['close'][-1]*4)/10000
                self.stoploss = self.df['high'][-2]
        elif(self.posi>0):
            if(self.df['close'][-1]<self.stoploss):
                self.sum        -= self.posi - self.df['close'][-1]
                self.sum        -= (self.df['close'][-1]*4)/10000
                self.posi        = 0
                self.last_signal = None
            elif(Trend == False):
                self.sum        -= (self.df['close'][-1]*8)/10000
                self.sum        += self.df['close'][-1]-self.posi
                self.posi        = -self.df['close'][-1]
                self.stoploss = self.df['high'][-2]

        elif(self.posi<0):
            if(self.df['close'][-1] > self.stoploss):
                self.sum        -= (self.df['close'][-1]*4)/10000
                self.sum        -= self.df['close'][-1] + self.posi
                self.posi        = 0
                self.last_signal = None
            elif(Trend == True):
                self.sum        -= (self.df['close'][-1]*8)/10000
                self.sum        -= self.df['close'][-1] + self.posi
                self.posi        = self.df['close'][-1]
                self.stoploss    = self.df['low'][-2]







if __name__ == "__main__":
    BtcCoin5  = server(5,"BTC/USDT")
    BtcCoin6  = server(6,"BTC/USDT")
    BtcCoin7  = server(7,"BTC/USDT")
    BtcCoin8  = server(8,"BTC/USDT")
    BtcCoin9  = server(9,"BTC/USDT")
    BtcCoin10 = server(10,"BTC/USDT")
    BtcCoin11 = server(11,"BTC/USDT")
    BtcCoin12 = server(12,"BTC/USDT")
    BtcCoin13 = server(13,"BTC/USDT")
    BtcCoin14 = server(14,"BTC/USDT")
    BtcCoin15 = server(15,"BTC/USDT")
    BtcCoin16 = server(16,"BTC/USDT")

    EthCoin5  = server(5,"ETH/USDT")
    EthCoin6  = server(6,"ETH/USDT")
    EthCoin7  = server(7,"ETH/USDT")
    EthCoin8  = server(8,"ETH/USDT")
    EthCoin9  = server(9,"ETH/USDT")
    EthCoin10 = server(10,"ETH/USDT")
    EthCoin11 = server(11,"ETH/USDT")
    EthCoin12 = server(12,"ETH/USDT")
    EthCoin13 = server(13,"ETH/USDT")
    EthCoin14 = server(14,"ETH/USDT")
    EthCoin15 = server(15,"ETH/USDT")
    EthCoin16 = server(16,"ETH/USDT")

    DogeCoin5  = server(5,"DOGE/USDT")
    DogeCoin6  = server(6,"DOGE/USDT")
    DogeCoin7  = server(7,"DOGE/USDT")
    DogeCoin8  = server(8,"DOGE/USDT")
    DogeCoin9  = server(9,"DOGE/USDT")
    DogeCoin10  = server(10,"DOGE/USDT")
    DogeCoin11 = server(11,"DOGE/USDT")
    DogeCoin12  = server(12,"DOGE/USDT")
    DogeCoin13  = server(13,"DOGE/USDT")
    DogeCoin14  = server(14,"DOGE/USDT")
    DogeCoin15  = server(15,"DOGE/USDT")
    DogeCoin16  = server(16,"DOGE/USDT")


# BtcCoin5
# BtcCoin5 
# BtcCoin6  
# BtcCoin7  
# BtcCoin8  
# BtcCoin9  
# BtcCoin10
# BtcCoin11
# BtcCoin12 
# BtcCoin13 
# BtcCoin14
# BtcCoin15 
# BtcCoin16 

# EthCoin5 
# EthCoin6 
# EthCoin7 
# EthCoin8  
# EthCoin9  
# EthCoin10 
# EthCoin11
# EthCoin12 
# EthCoin13 
# EthCoin14 
# EthCoin15 
# EthCoin16 

# DogeCoin5  
# DogeCoin6  
# DogeCoin7  
# DogeCoin8 
# DogeCoin9  
# DogeCoin10 
# DogeCoin11
# DogeCoin12  
# DogeCoin13 
# DogeCoin14
# DogeCoin15
# DogeCoin16
    while(True):
        try:
            BtcCoin5.trade()
            BtcCoin5.trade() 
            BtcCoin6.trade()  
            BtcCoin7.trade()  
            BtcCoin8.trade()  
            BtcCoin9.trade()  
            BtcCoin10.trade()
            BtcCoin11.trade()
            BtcCoin12.trade() 
            BtcCoin13.trade() 
            BtcCoin14.trade()
            BtcCoin15.trade() 
            BtcCoin16.trade() 
            time.sleep(0.5)
            EthCoin5.trade() 
            EthCoin6.trade() 
            EthCoin7.trade() 
            EthCoin8.trade()  
            EthCoin9.trade()  
            EthCoin10.trade() 
            EthCoin11.trade()
            EthCoin12.trade() 
            EthCoin13.trade() 
            EthCoin14.trade() 
            EthCoin15.trade() 
            EthCoin16.trade() 
            time.sleep(0.5)
            DogeCoin5.trade()  
            DogeCoin6.trade()  
            DogeCoin7.trade()  
            DogeCoin8.trade() 
            DogeCoin9.trade() 
            DogeCoin10.trade() 
            DogeCoin11.trade()
            DogeCoin12.trade()  
            DogeCoin13.trade() 
            DogeCoin14.trade()
            DogeCoin15.trade()
            DogeCoin16.trade()
            print(datetime.datetime.now())
            print("BTC")
            print("5 :",BtcCoin5.Get_sum()," 6 :",BtcCoin6.Get_sum()," 7 :",BtcCoin7.Get_sum()," 8 :",BtcCoin8.Get_sum()," 9 :",BtcCoin9.Get_sum()," 10 :",BtcCoin10.Get_sum()," 11 :",BtcCoin11.Get_sum()," 12 :",BtcCoin12.Get_sum()," 13 :",BtcCoin13.Get_sum()," 14 :",BtcCoin14.Get_sum()," 15 :",BtcCoin15.Get_sum()," 16 :",BtcCoin16.Get_sum()) 
            print("ETH")
            print("5 :",EthCoin5.Get_sum()," 6 :",EthCoin6.Get_sum()," 7 :",EthCoin7.Get_sum()," 8 :",EthCoin8.Get_sum()," 9 :",EthCoin9.Get_sum()," 10 :",EthCoin10.Get_sum()," 11 :",EthCoin11.Get_sum()," 12 :",EthCoin12.Get_sum()," 13 :",EthCoin13.Get_sum()," 14 :",EthCoin14.Get_sum()," 15 :",EthCoin15.Get_sum()," 16 :",EthCoin16.Get_sum())
            print("DOGE")
            print("5 :",DogeCoin5.Get_sum()," 6 :",DogeCoin6.Get_sum()," 7 :",DogeCoin7.Get_sum()," 8 :",DogeCoin8.Get_sum()," 9 :",DogeCoin9.Get_sum()," 10 :",DogeCoin10.Get_sum()," 11 :",DogeCoin11.Get_sum()," 12 :",DogeCoin12.Get_sum()," 13 :",DogeCoin13.Get_sum()," 14 :",DogeCoin14.Get_sum()," 15 :",DogeCoin15.Get_sum()," 16 :",DogeCoin16.Get_sum())
            print("BTC")
            print("5 :",BtcCoin5.GET_last_signal()," 6 :",BtcCoin6.GET_last_signal()," 7 :",BtcCoin7.GET_last_signal()," 8 :",BtcCoin8.GET_last_signal()," 9 :",BtcCoin9.GET_last_signal()," 10 :",BtcCoin10.GET_last_signal()," 11 :",BtcCoin11.GET_last_signal()," 12 :",BtcCoin12.GET_last_signal()," 13 :",BtcCoin13.GET_last_signal()," 14 :",BtcCoin14.GET_last_signal()," 15 :",BtcCoin15.GET_last_signal()," 16 :",BtcCoin16.GET_last_signal())
            print("ETH")
            print("5 :",EthCoin5.GET_last_signal()," 6 :",EthCoin6.GET_last_signal()," 7 :",EthCoin7.GET_last_signal()," 8 :",EthCoin8.GET_last_signal()," 9 :",EthCoin9.GET_last_signal()," 10 :",EthCoin10.GET_last_signal()," 11 :",EthCoin11.GET_last_signal()," 12 :",EthCoin12.GET_last_signal()," 13 :",EthCoin13.GET_last_signal()," 14 :",EthCoin14.GET_last_signal()," 15 :",EthCoin15.GET_last_signal()," 16 :",EthCoin16.GET_last_signal())
            print("DOGE")
            print("5 :",DogeCoin5.GET_last_signal()," 6 :",DogeCoin6.GET_last_signal()," 7 :",DogeCoin7.GET_last_signal()," 8 :",DogeCoin8.GET_last_signal()," 9 :",DogeCoin9.GET_last_signal()," 10 :",DogeCoin10.GET_last_signal()," 11 :",DogeCoin11.GET_last_signal()," 12 :",DogeCoin12.GET_last_signal()," 13 :",DogeCoin13.GET_last_signal()," 14 :",DogeCoin14.GET_last_signal()," 15 :",DogeCoin15.GET_last_signal()," 16 :",DogeCoin16.GET_last_signal())

            # print("BTC : ",btc_last_signal,"  ETH : ",eth_last_signal,"  BNB : ",bnb_last_signal,
            #         "  XRP : ",xrp_last_signal," DOGE : ", doge_last_signal)
        except Exception as e:
            print('ERROR NAME : ', e)
            time.sleep(0.1)