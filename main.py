import time
import pyupbit

# 1 , 5 , 15 , 30 분봉 추세 방향 
# True : 상승 , False 하락 
minute1_trend = False
minute5_trend = False 
minute15_trend = False
minute30_trend = False

# 손절가 
stoploss = 0

#구매가 
buyprice = 0

#코인 이름 
Coinname = "KRW-BTC"

#한번에 들어갈 돈의 양 
inpmoney = 100000

#key
access_key = "v7K6pzKCAo8QH9o4SnoRYOPF4crNmpTfRrrJI4up"
secret_key = "GuoBhDkgVVb1feWYlif54hYlzQ1svFmBDejg4ioT"
upbit = pyupbit.Upbit(access_key,secret_key)

# Trend 계산용 함수 
def Trend():

    def Heikinashi(df):
        # 현재 캔들을 포함한 7개의 캔들을 저장 
        time7before = df.iloc[-7]
        time6before = df.iloc[-6]
        time5before = df.iloc[-5]
        time4before = df.iloc[-4]
        time3before = df.iloc[-3]
        time2before = df.iloc[-2]
        time1before = df.iloc[-1]

        # 7번째 Heikin Ashi
        time7before_open  = (time7before['open']+time7before['close'])/2
        time7before_close = (time7before['open']+time7before['high']+time7before['low']+time7before['close'])/4

        # 6번쨰 Heikin Ashi
        time6before_open  = (time7before_open+time7before_close)/2
        time6before_close = (time6before['open']+time6before['high']+time6before['low']+time6before['close'])/4

        # 5번쨰 Heikin Ashi
        time5before_open  = (time6before_open+time6before_close)/2
        time5before_close = (time5before['open']+time5before['high']+time5before['low']+time5before['close'])/4

        # 4번쨰 Heikin Ashi
        time4before_open  = (time5before_open+time5before_close)/2
        time4before_close = (time4before['open']+time4before['high']+time4before['low']+time4before['close'])/4

        # 3번쨰 Heikin Ashi
        time3before_open  = (time4before_open+time4before_close)/2
        time3before_close = (time3before['open']+time3before['high']+time3before['low']+time3before['close'])/4

        # 2번쨰 Heikin Ashi
        time2before_open  = (time3before_open+time3before_close)/2
        time2before_close = (time2before['open']+time2before['high']+time2before['low']+time2before['close'])/4

        # 1번쨰 Heikin Ashi
        time1before_open  = (time2before_open+time2before_close)/2
        time1before_close = (time1before['open']+time1before['high']+time1before['low']+time1before['close'])/4

        #  2번쨰 Heikin Ashi와 1번째 Heikin Ashi가 둘다 상승이라면 True 반환 아니라면 False 반환 
        if (time2before_open<time2before_close) and (time1before_open<time1before_close):
            return True
        else:
            return False

    # 상승인즈 하락인지 판별해주는 함수 
    def UpOrDown(trend):
        if(trend):
            return "UP"
        else:
            return "DOWN"


    # 1,5,15,30 분봉 기록을 각각 7개 가져옴 하이킨 아시 시가에 영향을 많이 줘서 7개 가져옴 
    df1  = pyupbit.get_ohlcv(Coinname,count=7,interval="minute1" )
    df5  = pyupbit.get_ohlcv(Coinname,count=7,interval="minute5" )
    df15 = pyupbit.get_ohlcv(Coinname,count=7,interval="minute15")
    df30 = pyupbit.get_ohlcv(Coinname,count=7,interval="minute30")

    # 각 분봉별로 추세를 파악하기 위함
    minute1_trend  = Heikinashi(df1) 
    minute5_trend  = Heikinashi(df5)
    minute15_trend = Heikinashi(df15)
    minute30_trend = Heikinashi(df30)

    # 아무것도 안뜨면 심심하잖아 이거라도 봐야지 
    print("# # -----------------------------------------------------------------------------")
    # print("1min : ",UpOrDown(minute1_trend),"      5min : ",UpOrDown(minute5_trend),"      15min : ",UpOrDown(minute15_trend),"      30min : ",UpOrDown(minute30_trend))
    print("stoploss : ",stoploss)
    print("buyprice  : ",buyprice)
    print("currentprice : ",pyupbit.get_current_price(Coinname))
        

    # 모든 추세가 상승을 예측하고 있으면 True와 Stoploss를 반환 
    # 손절을 짧게 잡기 위해 5분봉 전 캔들 저가로 잡음 
    if(minute1_trend and minute5_trend and minute15_trend and minute30_trend):
        return True , df5.iloc[-2]['low']
    else:
        return False , 0 

def Trend_30min():

    def Heikinashi(df):
        time7before = df.iloc[-7]
        time6before = df.iloc[-6]
        time5before = df.iloc[-5]
        time4before = df.iloc[-4]
        time3before = df.iloc[-3]
        time2before = df.iloc[-2]

        # 7번째 Heikin Ashi
        time7before_open  = (time7before['open']+time7before['close'])/2
        time7before_close = (time7before['open']+time7before['high']+time7before['low']+time7before['close'])/4

        # 6번쨰 Heikin Ashi
        time6before_open  = (time7before_open+time7before_close)/2
        time6before_close = (time6before['open']+time6before['high']+time6before['low']+time6before['close'])/4

        # 5번쨰 Heikin Ashi
        time5before_open  = (time6before_open+time6before_close)/2
        time5before_close = (time5before['open']+time5before['high']+time5before['low']+time5before['close'])/4

        # 4번쨰 Heikin Ashi
        time4before_open  = (time5before_open+time5before_close)/2
        time4before_close = (time4before['open']+time4before['high']+time4before['low']+time4before['close'])/4

        # 3번쨰 Heikin Ashi
        time3before_open  = (time4before_open+time4before_close)/2
        time3before_close = (time3before['open']+time3before['high']+time3before['low']+time3before['close'])/4

        # 2번쨰 Heikin Ashi
        time2before_open  = (time3before_open+time3before_close)/2
        time2before_close = (time2before['open']+time2before['high']+time2before['low']+time2before['close'])/4

        # 전 봉이 하방으로 끝나는것만 확인하면 되기 때문에 1번쨰 Heikin Ashi는 필요 없음 

        print("# # -----------------------------------------------------------------------------")
        print("stoploss : ",stoploss)
        print("buyloss  : ",buyprice)
        print("currentprice : ",pyupbit.get_current_price(Coinname))

        # 위와 마찬가지로 상승이면 True 반환 하락이면 False 반환 
        if (time2before_open<time2before_close):
            return True
        else:
            return False

    # 5분봉 트렌드 전 캔들이 상승일경우 True 하락일경우 False 반환 
    return Heikinashi(pyupbit.get_ohlcv(Coinname,count=7,interval="minute30"))

try:
    while True:
        if(int(upbit.get_balance(Coinname))==0):
            print("2번 성공")        
        elif(int(upbit.get_balance(Coinname))>0):
            print("3번 성공")
        elif(upbit.get_balance(Coinname)==0):
            print("4번 성공")

        if(upbit.get_balance(Coinname)):

            # 5분봉 추세 확인 
            tren = Trend_30min()
            
            # 5분봉이 상승 추세라면 조건하에 
            if(tren and (pyupbit.get_current_price(Coinname)>stoploss)):
                # 만약 가격이 산 금액에 400000 만큼 오를떄마다 스탑 로스 가격 올리기 
                if(pyupbit.get_current_price(Coinname) > buyprice+400000):
                    stoploss+=100000
                    buyprice+=400000
            


            # 5분봉이 하락 추세라면 매도 
            else:
                upbit.sell_market_order(Coinname, upbit.get_balance(Coinname))
                stoploss = 0
                buyprice = 0
            print("position")
            time.sleep(1)

        # 포지션이 없을경우  
        else:
            print("1번")
            # 모든 추세와 스탑 로스가 조사 
            current_all_trend , stoploss= Trend()   
            # 만약 모든 추세가 상승이라면 
            print("2번")
            if(current_all_trend):
                #가지고있는 모든 금액 매수 
                print("3번")
                upbit.buy_market_order(Coinname,inpmoney)
                print("4번")
                buyprice = pyupbit.get_current_price(Coinname)
                print("5번 ")
            time.sleep(1)  

except:
    raise


 


# 하이킨 아시의 종가 (o + h + l + c)/4 
# 하이킨 아시의 시가 (전 하이킨아시의 시가 + 전 하이킨 아시의 종가)/2
# 하이킨 아시의 처음 캔들의 시가 (현 캔들의 종가 + 현 캔들의 시가)/2
# 하이킨 아시의 처음 캔들의 종가 (o + h + l + c)/4 

# # -----------------------------------------------------------------------------
# # - Name : main
# # - Desc : 메인
# # -----------------------------------------------------------------------------

# # 암호화폐 목록
# print(pyupbit.get_tickers())           # 모든 티커 조사 
# print(pyupbit.get_tickers(fiat="KRW")) # 한가지 화폐만 지정 가능 

# # 최근 체결가격
# while True:
#     print(pyupbit.get_current_price(Coinname))              # 단일 조사 
#     time.sleep(0.2)
# print(pyupbit.get_current_price([Coinname, "KRW-XRP"])) # 여러개 동시 조사도 가능 

# # 차트 데이터

# # interval 은 파라미터로 
# # day/minute1/minute3/minute5/minute10/minute15/minute30/minute60/minute240/week/month 를 이용가능하다
# 값으로 시작가 , 고가 , 저가 , 종가 , 양 , 시간 표시  

# # 매수/매도 호가 (현제가가 중요해서 별로 쓸 일은 없을듯 )
# print(pyupbit.get_orderbook(tickers=Coinname))

# # Exchange API 주문은 초당 8회, 분당 200회 / 주문 외 요청은 초당 30회, 분당 900회 사용 가능합니다

# #잔고 조회
# print(upbit.get_balance("KRW-XRP"))                             #KRW-BTC 조회
# print(upbit.get_balance("KRW"))                                 # 보유 현금 조회
# print(upbit.get_balances())                                     # 모든 암호화폐 조회

# # 시장가 매수/매도 주문
# print(upbit.buy_market_order(Coinname, 10000))                 # 주문시에는 돈의 양으로 매수 
# print(upbit.sell_market_order("KRW-XRP", 30))                   # 판매시에는 코인의 수로 매도 

# #미체결 주문 조회 
# upbit.get_order(Coinname)                                      # 시장가 거래라 미체결은 희박

# #완료된 주문 조회 
# print(upbit.get_order("KRW-LTC", state="done"))

# # 매수/매도 주문 취소
# print(upbit.cancel_order('50e184b3-9b4f-4bb0-9c03-30318e3ff10a')) # 이도 역시 희박 



# if __name__ == "__main__":
#     wm = WebSocketManager("ticker", [Coinname])
#     for i in range(10):
#         print(i,"차")
#         data = wm.get()
#         print("가저오기 성공")
#         print(data)
#     wm.terminate()








