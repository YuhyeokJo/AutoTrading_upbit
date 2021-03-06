# -*- coding: utf-8 -*-
import pyupbit
import time
import datetime

#%% 목표가 구하기(변동성 돌파 전략)
def cal_target(ticker):
    df = pyupbit.get_ohlcv(ticker, "minute240")
    print(df.tail())
    before = df.iloc[-2]
    after = df.iloc[-1]
    
    before_range = before['high']-before['low']
    target = after['open'] + before_range*0.4
    return target

#%% 객체생성
f = open("OpenAPIKey.txt") #경로설정필요
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
coin = 'KRW-BTC'
target = cal_target("KRW-BTC")
op_mode = False #프로그램이 시작하자마자 매수되는 것 방지 목적(다음날 처음 매수)
hold = False
print(target)
trading_log={}
# trading_log['selling_time']=[]
# trading_log['selling_price']=[]
# trading_log['selling_balance']=[]
# trading_log['buying_time']=[]
# trading_log['buying_price']=[]
# trading_log['buying_balance']=[]
# trading_log['state']=[]
#%% log_file 생성
f = open('trading_log.txt', 'w') #경로설정필요
f.close()

#%% 1초에 한 번 현재시간과 비트코인 현재가 출력
while True:
    now = datetime.datetime.now()

    # 상태출력
    price = pyupbit.get_current_price(coin)    
    log_str=f"현재시간: {now} 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}"
    print(log_str)
    time.sleep(1)
    
    
    # 8시 59분 50초 ~ 09:00:00 초 사이에 매도
    # 4시간 간격으로 매도되도록 수정 4, 8, 12, 16, 20 하루 5번
    list_selling_time = [4, 8, 12, 16, 20]
    
    if (now.hour in list_selling_time) and now.minute == 59  and (50 <= now.second <=59):
        if op_mode is True and hold is True:
            coin_balance = upbit.get_balance(coin)
            upbit.sell_market_order(coin, coin_balance)
            trading_log['selling_time']=now
            trading_log['selling_price']=pyupbit.get_current_price(coin)   
            trading_log['selling_balance']=coin_balance
            hold = False
        op_mode = False
        time.sleep(10) #매도 이후 목표가 갱신되기까지 프로그램 정지
        trading_log['state']=log_str
        f = open("trading_log.txt", "a") #경로설정필요
        dict_save=repr(trading_log)
        f.write(dict_save+'\n')
        f.close()
        
    # 9시 20~30초 기준 목표가 갱신
    # 매도 이후 1시간 뒤 목표가 갱신
    list_target_update_time = [5, 9, 13, 17, 21]
    
    if (now.hour in list_target_update_time) and now.minute == 0  and (20 <= now.second <=30):
        target = cal_target(coin)
        time.sleep(10)
        op_mode = True
    
       
    #매수 시도
    if op_mode is True and price is not None and price >= target and hold is False:
        krw_balance = upbit.get_balances("KRW") #원화 잔고 조회
        balance = round(float((krw_balance[0][0]['balance'])))
        upbit.buy_market_order(coin, balance-100) #전액 매수
        trading_log['buying_time']=now
        trading_log['buying_price']=pyupbit.get_current_price(coin)
        coin_balance = upbit.get_balance(coin)   
        trading_log['buying_balance']=coin_balance
        hold = True #연속해서 매수되는 것 방지
        

    


