import time
import datetime as dt
import subprocess
import sys
import os
import ccxt
import traceback
from exchange_utils import initialize_binance, fetch_balance, fetch_ticker, cancel_all_orders
from trading_utils import cal_amount, is_position_open, binance_long, binance_long_with_max_margin, calculate_position_size
from volume_utils import fetch_volume_data
from record_utils import read_last_csv_entry, record_trade, initialize_csv
from RsiNew import get_recent_rsi

print('Binance Automatic Futures trade Processing working....')

with open("api.txt") as api_file:
    lines = api_file.readlines()
    api_key = lines[0].strip()
    secret = lines[1].strip()

def run():
    binance = initialize_binance(api_key, secret)
    symbol = "BTC/USDT"
    leverage = 75
    volume_list = []
    position_open = False
    result_recorded = False
    startSeed = 0
    
    fee_rate = 0.0005 # taker 수수료율
    
    sl_multiplier = 0.15 #손절 15%라인
    tp_multiplier = 0.3 #수익 30#라인
    rsi_threshold = 4
    
    if read_last_csv_entry() is None:
        initialize_csv(binance, symbol)
        
    while True:
        balance = fetch_balance(binance)
        usdt = balance['total']['USDT'] #계좌 잔고를 받아오는 코드
        ticker = fetch_ticker(binance, symbol)
        cur_price = ticker
        daytime = dt.datetime.now()
        recent_rsi_6 = get_recent_rsi(symbol)


        #RSI가 4이하 이고
        #포지션이 열려있지 않고(is_position_open)
        #position_open 변수가 false이고
        #거래량 데이터가 조건을 충족할때
        #롱 포지션을 잡는다.
        #start seed를 롱 잡을때 미리 저장하고 record_trade 함수에 넣어준다.
        if (recent_rsi_6 <= rsi_threshold and
            not is_position_open(binance, symbol) and
            not position_open and
            fetch_volume_data(binance, symbol, volume_list)):
            cancel_all_orders(binance, symbol)
            print(f" 포지션 돌입시점 RSI : {recent_rsi_6:.2f}, 돌입 가격 : {cur_price}")
            startSeed = usdt
            #binance_long(binance, symbol, sl_multiplier, tp_multiplier, leverage, volume_list)
            binance_long_with_max_margin(binance, symbol, sl_multiplier, tp_multiplier, leverage, fee_rate)  # fee_rate를 추가로 전달
            result_recorded = False
            position_open = True

        #내용들이 정리 되면 거래 내역을 
        if position_open and not is_position_open(binance, symbol) and not result_recorded:
            trades = binance.fetch_my_trades(symbol, since=None, limit=20) #가장 최근 거래 기록 2개(buy,sell 한쌍) 가져오기
            for i in range(len(trades) - 1, 0, -1):
                if trades[i]['side'] == 'sell' and trades[i - 1]['side'] == 'buy' and trades[i]['order'] != trades[i - 1]['order']:
                    record_trade(binance, symbol, trades[i - 1], trades[i], startSeed, 0)
                    result_recorded = True
                    position_open = False
                    
        if not is_position_open(binance, symbol):
            cancel_all_orders(binance, symbol)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        run()
    except ccxt.BaseError as e:
        print(f"An Binance error occurred: {e}")
    except Exception as e:
      #그 외 모든 예외처리
        print(f"An Code error occurred: {e}")
        print(traceback.print_exc())  # 예외 발생 시 스택 트레이스 출력
