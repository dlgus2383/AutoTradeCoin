import pyupbit
import time

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

#key
access_key = "v7K6pzKCAo8QH9o4SnoRYOPF4crNmpTfRrrJI4up"
secret_key = "GuoBhDkgVVb1feWYlif54hYlzQ1svFmBDejg4ioT"
upbit = pyupbit.Upbit(access_key,secret_key)




print(upbit.get_balance_t(Coinname))
print(upbit.get_balance_t('KRW-BTC'))