#
#*------------------- 거래량 체크 관련 기능 --------------------*
#

import pandas as pd  # 데이터 처리를 위해 pandas 라이브러리를 가져옴
import numpy as np  # 수치 계산을 위해 numpy 라이브러리를 가져옴

def fetch_volume_data(exchange, symbol, volume_list):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=6)  # 1분 간격의 최근 4개 OHLCV 데이터 가져오기
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])  # 데이터프레임으로 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # 타임스탬프를 datetime 형식으로 변환
    current_volume = df['volume'].iloc[-1]  # 최신 분봉의 거래량 가져오기
    volume_list.append(float(current_volume))  # 거래량 리스트에 추가
    
    if len(volume_list) > 9:  # 리스트 길이가 9를 초과하면
        volume_list.pop(0)  # 가장 오래된 항목 제거
        
    sma_9 = np.mean(volume_list)  # 단순 이동 평균 9 계산
    
    volume_1_min_ago = df['volume'].iloc[-2]  # 1분 전 거래량
    volume_2_min_ago = df['volume'].iloc[-3]  # 2분 전 거래량
    volume_3_min_ago = df['volume'].iloc[-4]  # 3분 전 거래량
    volume_4_min_ago = df['volume'].iloc[-5]  # 4분 전 거래량
    volume_5_min_ago = df['volume'].iloc[-6]  # 5분 전 거래량
    
    if current_volume > (1.5 * (volume_1_min_ago + volume_2_min_ago + volume_3_min_ago + volume_4_min_ago + volume_5_min_ago) / 5):  # 현재 거래량이 이전 5분 평균의 1.5배 초과시
        return True
