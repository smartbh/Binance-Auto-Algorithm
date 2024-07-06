#
#*------------------- 파일 기록 관련 기능 --------------------*
#

import csv  # CSV 파일 작업을 위해 csv 라이브러리를 가져옴
import datetime as dt  # 날짜 및 시간 작업을 위해 datetime 라이브러리를 dt로 가져옴

def read_last_csv_entry(filename='binance.csv'):
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()  # 파일의 모든 라인 읽기
            if lines:
                return lines[-1].strip().split(',')  # 마지막 라인을 리스트로 반환
        return None
    except (IndexError, FileNotFoundError):
        return None

def record_trade(exchange, symbol, buy_trade, sell_trade, start_seed, finish_seed):
    entry_price = float(buy_trade['price'])  # 매매 돌입 가격
    exit_price = float(sell_trade['price'])  # 매매 종료 가격
    pnl = float(sell_trade['info'].get('realizedPnl', 0))  # 오늘의 수익, 기본값 0
    entry_time = dt.datetime.fromtimestamp(buy_trade['timestamp'] / 1000)  # 매매 돌입 시간
    exit_time = dt.datetime.fromtimestamp(sell_trade['timestamp'] / 1000)  # 매매 종료 시간
    result = '승' if pnl > 0 else '패' if pnl < 0 else '무'  # 승무패 결과

    # 선물 잔고 가져오기
    balance = exchange.fetch_balance(params={"type": "future"})
    usdt = balance['total']['USDT']
    finish_seed = usdt
    
    last_entry = read_last_csv_entry()

    # 수수료 계산 추가
    buy_trade_fee = buy_trade['fee']['cost']
    sell_trade_fee = sell_trade['fee']['cost']
    total_fee = buy_trade_fee + sell_trade_fee

    # 순수익 계산 추가
    net_profit = pnl - total_fee
    
    if last_entry and (entry_price == float(last_entry[1]) and exit_price == float(last_entry[2]) and pnl == float(last_entry[3])):
        print("거래 내역이 이미 기록되어 있습니다. 기록을 생략합니다.")
        return
    
    print(f"매매 완료 : (돌입가격 = {entry_price}), (마무리 가격 = {exit_price}), (오늘의 수익 = {pnl}), (매매 돌입 시간 = {entry_time}), (매매 종료 시간 = {exit_time}), (승무패 = {result})")
    
    # CSV 기록 부분에 수수료(total_fee)와 순수익(net_profit) 추가
    with open('binance.csv', 'a', encoding='utf-8-sig', newline='') as f:
        wr = csv.writer(f)
        wr.writerow([start_seed, entry_price, exit_price, pnl, total_fee, net_profit, finish_seed, entry_time.strftime('%Y-%m-%d %H:%M:%S'), exit_time.strftime('%Y-%m-%d %H:%M:%S'), result, 75])
        
def initialize_csv(exchange, symbol):
    trades = exchange.fetch_my_trades(symbol, since=None, limit=4)  # 최근 4개의 거래 히스토리 가져오기
    with open('binance.csv', 'w', encoding='utf-8-sig', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['Start Seed', 'Entry Price', 'Exit Price', 'Profit/Loss', 'Fee', 'Net Profit', 'Finish Seed', 'Entry Time', 'Exit Time', 'Result', 'Leverage'])
    for i in range(len(trades) - 1):
        if trades[i]['side'] == 'buy' and trades[i + 1]['side'] == 'sell' and trades[i]['order'] != trades[i + 1]['order']:
            record_trade(exchange, symbol, trades[i], trades[i + 1], 0, 0)
