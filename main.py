#
#*------------------- 주 로직이 돌아갈 메인 함수 --------------------*
#


import time
import datetime as dt
import subprocess
import sys
import os
from exchange_utils import initialize_binance, fetch_balance, fetch_ticker, cancel_all_orders
from trading_utils import cal_amount, is_position_open, binance_long
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
    if read_last_csv_entry() is None:
        initialize_csv(binance, symbol)
    while True:
        balance = fetch_balance(binance)
        usdt = balance['total']['USDT']
        ticker = fetch_ticker(binance, symbol)
        cur_price = ticker
        daytime = dt.datetime.now()
        recent_rsi_6 = get_recent_rsi(symbol)
        if 21 <= daytime.hour < 22:
            sl_multiplier = 0.15
            tp_multiplier = 0.23
            rsi_threshold = 7
        else:
            sl_multiplier = 0.15
            tp_multiplier = 0.3
            rsi_threshold = 4
        if (recent_rsi_6 <= rsi_threshold and not is_position_open(binance, symbol) and not position_open and fetch_volume_data(binance, symbol, volume_list)):
            cancel_all_orders(binance, symbol)
            print(f" 포지션 돌입시점 RSI : {recent_rsi_6:.2f}, 돌입 가격 : {cur_price}")
            binance_long(binance, symbol, sl_multiplier, tp_multiplier, leverage, volume_list)
            result_recorded = False
            position_open = True
        if position_open and not is_position_open(binance, symbol) and not result_recorded:
            trades = binance.fetch_my_trades(symbol, since=None, limit=4)
            for i in range(len(trades) - 1, 0, -1):
                if trades[i]['side'] == 'sell' and trades[i - 1]['side'] == 'buy' and trades[i]['order'] != trades[i - 1]['order']:
                    record_trade(binance, symbol, trades[i - 1], trades[i], 0, 0)
                    result_recorded = True
                    position_open = False
        if not is_position_open(binance, symbol):
            cancel_all_orders(binance, symbol)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        run()
    except ccxt.BaseError as e:
        print(f"An error occurred: {e}")
