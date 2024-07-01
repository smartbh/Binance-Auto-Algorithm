import ccxt
import datetime as dt
import csv
import os
import time
import subprocess
import sys
import pandas as pd
import numpy as np
from BinanceFuturesPositionHistory import BinanceFuturesAPI
from RsiNew import get_recent_rsi

# api.txt 파일에서 API 키와 비밀 키를 읽어옴
with open("api.txt") as api_file:
    lines = api_file.readlines()
    api_key = lines[0].strip()
    secret = lines[1].strip()

# Binance 인스턴스를 생성할 때 API 키와 비밀 키를 설정
binance = ccxt.binance({
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# 거래 심볼 정하기
symbol = "BTC/USDT"


# 오픈 포지션 조회
def fetch_futures_positions():
    # 연결이 작동하는지 확인하기 위해 잔액 조회
    balance = binance.fetch_balance()
    # 오픈 포지션 조회 (v2 엔드포인트 사용)
    positions = balance['info']['positions']

    #print(len(positions))
    # 포지션이 없는 경우
    # BTC/USDT 포지션 필터링 및 출력
    btc_positions = [position for position in positions if position['symbol'] == 'BTCUSDT']
    btc_positions = btc_positions[0]
    #print(btc_positions)
    return btc_positions
        
def read_last_csv_entry(filename='binance.csv'):
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()  # 파일의 모든 라인 읽기
                if lines:
                    last_line = lines[-1]  # 마지막 라인 가져오기
                    print(last_line.strip().split(','))
                    return last_line.strip().split(',')  # 마지막 라인을 리스트로 반환
                return None
        except (IndexError, FileNotFoundError):
            return None  # 파일이 없거나 읽을 라인이 없으면 None 반환


# 모든 주문 취소 함수
def cancel_all_orders():
    orders = binance.fetch_open_orders(symbol=symbol)
    print(len(orders))
    for order in orders:
        binance.cancel_order(order['id'], symbol)

# SMA 9 계산을 위한 거래량 리스트 초기화
volume_list = []
last_print_time = None
print_interval = 30  # 출력 간격 (초 단위)


# 거래량 데이터 가져오기 함수
def fetch_volume_data(symbol):
    while True:
        try:
            # 1분, 2분, 3분 전의 거래량 가져오기
            ohlcv = binance.fetch_ohlcv(symbol, timeframe='1m', limit=4)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # 현재 거래량은 최신 분봉의 거래량을 사용
            current_volume = df['volume'].iloc[-1]

            # 거래량 리스트에 추가
            volume_list.append(float(current_volume))
            if len(volume_list) > 9:
                volume_list.pop(0)

            # SMA 9 계산
            if len(volume_list) == 9:
                sma_9 = np.mean(volume_list)
            #else:
                #sma_9 = np.mean(volume_list)  # 거래량 리스트의 평균으로 계산

            volume_1_min_ago = df['volume'].iloc[-2]
            volume_2_min_ago = df['volume'].iloc[-3]
            volume_3_min_ago = df['volume'].iloc[-4]

            # 거래량 출력
            #print(f"현재 거래량(SMA 9 기준): {current_volume}")
            #print(f"1분 전 거래량: {volume_1_min_ago}")
            #print(f"2분 전 거래량: {volume_2_min_ago}")
            #print(f"3분 전 거래량: {volume_3_min_ago}")
            #print(f"3분 전 거래량들 평균 : {(volume_1_min_ago + volume_2_min_ago + volume_3_min_ago)/3}")

            now = dt.datetime.now()
            recent_rsi_6 = get_recent_rsi(symbol, limit=500)  # 최근 RSI 값 가져오기
            rsi_threshold = 4
            
            if current_volume > 1.5 * (volume_1_min_ago + volume_2_min_ago + volume_3_min_ago)/3 and recent_rsi_6 <= rsi_threshold:
                print(f"현재 RSI 6 : {recent_rsi_6}")
                print(f"거래량 조건 충족, 시간 : {now}", end="\n")
                print(f"현재 거래량(SMA 9 기준): {current_volume}")
                print(f"1분 전 거래량: {volume_1_min_ago}")
                print(f"2분 전 거래량: {volume_2_min_ago}")
                print(f"3분 전 거래량: {volume_3_min_ago}")
                print(f"3분 전 거래량들 평균 * 1.5 : {(volume_1_min_ago + volume_2_min_ago + volume_3_min_ago)/3*1.5}")
                return true


            # 1초 대기 후 다시 실행
            time.sleep(0.1)

        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(5)  # 오류 발생 시 5초 대기 후 재시도

            
# 함수 실행

#btcposition = fetch_futures_positions()
#initial_margin = float(btcposition['initialMargin'])
# entryPrice 값과 타입 출력
#for position in btcposition:
    #entry_price = position['entryPrice']
    #print(f"entryPrice: {entry_price}, type: {type(entry_price)}")
    #entry_price = float(entry_price)
    #print(f"entryPrice: {entry_price}, type: {type(entry_price)}")

#print(btcposition['entryPrice'])
#cancel_all_orders()

#orders = binance.fetch_open_orders(symbol=symbol)
#print(orders)

"""
if initial_margin == 0:
    print("포지션 없음")
    cancel_all_orders()
else:
    print("포지션 있음")
"""

#balance = binance.fetch_balance()
#print(balance)

# 함수 실행
fetch_volume_data(symbol)

