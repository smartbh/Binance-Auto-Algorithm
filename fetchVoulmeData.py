#fetch volume date funtion py
#실시간 4분치 거래량 가져오는 함수.

import ccxt
import pandas as pd




def fetch_volume_data(symbol):
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
    else:
        sma_9 = np.mean(volume_list)  # 거래량 리스트의 평균으로 계산

    volume_1_min_ago = df['volume'].iloc[-2]
    volume_2_min_ago = df['volume'].iloc[-3]
    volume_3_min_ago = df['volume'].iloc[-4]
        
    # 거래량 출력
    print(f"현재 거래량(SMA 9 기준): {current_volume}")
    print(f"1분 전 거래량: {volume_1_min_ago}")
    print(f"2분 전 거래량: {volume_2_min_ago}")
    print(f"3분 전 거래량: {volume_3_min_ago}")
    print(f"3분 전 거래량들 평균 : {(volume_1_min_ago + volume_2_min_ago + volume_3_min_ago)/3}")
