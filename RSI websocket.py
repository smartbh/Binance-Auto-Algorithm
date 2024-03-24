
import asyncio
import websockets
import json
import time

async def btc_future_price():
    uri = "wss://fstream.binance.com/ws/btcusdt@markPrice@1s"
    async with websockets.connect(uri) as websocket:
        prev_time = None  # 이전 메시지 수신 시간
        while True:
            current_time = time.time()  # 현재 메시지 수신 시간
            response = await websocket.recv()
            if prev_time is not None:
                interval = current_time - prev_time  # 메시지 수신 간격
                print(f"수신 간격: {interval}초")
            prev_time = current_time
            data = json.loads(response)
            print(f"BTC 선물 마크 가격: {data['p']}")

asyncio.run(btc_future_price())




###웹소켓 기반 rsi 계산하는 스크립
"""
import asyncio
import websockets
import json
import pandas as pd
import talib as ta

# OHLCV 데이터를 저장하기 위해 DataFrame 초기화
df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

async def fetch_ohlcv():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            candle = data['k']

            # DataFrame에 새로운 캔들 데이터 추가
            new_row = pd.DataFrame([{
                'timestamp': pd.to_datetime(candle['T'], unit='ms'),
                'open': float(candle['o']),
                'high': float(candle['h']),
                'low': float(candle['l']),
                'close': float(candle['c']),
                'volume': float(candle['v'])
            }])
            global df
            df = pd.concat([df, new_row], ignore_index=True)

            # 14 기간의 창을 사용하여 종가에 대한 RSI 계산
            if len(df) > 14:
                close_prices = df['close'].astype(float).values
                rsi_14 = ta.RSI(close_prices, timeperiod=14)[-1]  # 14 기간에 대한 RSI
                rsi_6 = ta.RSI(close_prices, timeperiod=6)[-1]  # 6 기간에 대한 RSI
                print(f"RSI 14: {rsi_14}")
                print(f"RSI 6: {rsi_6}")
            
            print(f"종가: {candle['c']}")

async def main():
    await fetch_ohlcv()

if __name__ == "__main__":
    asyncio.run(main())
"""
