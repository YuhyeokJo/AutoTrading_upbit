# -*- coding: utf-8 -*-
import pyupbit
import time
import datetime

#%% 목표가 구하기(변동성 돌파 전략)
def cal_target(ticker):
    df = pyupbit.get_ohlcv(ticker, "day")
    print(df.tail())
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    
    yesterday_range = yesterday['high']-yesterday['low']
    target = today['open'] + yesterday_range*0.5
    return target

#%% 객체생성
f = open("OpenAPIKey.txt")
lines = f.readlines()
access = lines[1].strip()
access = access.split()
access = access[3]
secret = lines[2].strip()
secret = secret.split()
secret = secret[3]
f.close()
upbit = pyupbit.Upbit(access, secret)

#%%
# price = pyupbit.get_current_price("KRW-BTC")
# print(price)

#%% 변수설정
target = cal_target("KRW-BTC")
op_mode = False #프로그램이 시작하자마자 매수되는 것 방지 목적(다음날 처음 매수)
hold = False
print(target)

#%% 1초에 한 번 현재시간과 비트코인 현재가 출력
while True:
    now = datetime.datetime.now()
    
    # 8시 59분 50초 ~ 09:00:00 초 사이에 매도
    if now.hour == 8 and now.minute == 59  and (50 <= now.second <=59):
        if op_mode is True and hold is True:
            btc_balance = upbit.get_balance("KRW-BTC")
            upbit.sell_market_order("KRW-BTC", btc_balance)
            hold = False
        op_mode = False
        time.sleep(10) #매도 이후 목표가 갱신되기까지 프로그램 정지
    
    # 9시 20~30초 기준 목표가 갱신
    if now.hour == 9 and now.minute == 0  and (20 <= now.second <=30):
        target = cal_target("KRW-BTC")
        time.sleep(10)
        op_mode = True
    
    price = pyupbit.get_current_price("KRW-BTC")
    
    #매수 시도
    if op_mode is True and price is not None and price >= target and hold is False:
        krw_balance = upbit.get_balances("KRW") #원화 잔고 조회
        upbit.buy_market_order('KRW-BTC', krw_balance) #전액 매수
        hold = True #연속해서 매수되는 것 방지
        
    # 상태출력
    print(f"현재시간: {now} 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}")
    time.sleep(1)
    

