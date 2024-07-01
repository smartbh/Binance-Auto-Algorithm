import ccxt
import pandas as pd
import talib as ta
import time

def fetch_ohlcv(symbol, timeframe='1m', limit=500):
    exchange = ccxt.binance({
        'options': {
            'defaultType': 'future'  # 선물 시장 데이터를 가져오도록 설정
        }
    })
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_rsi(df, periods=[6, 12, 24]):
    for period in periods:
        df[f'RSI_{period}'] = ta.RSI(df['close'], timeperiod=period)
    return df

def main():
    symbol = 'BTC/USDT'
    limit = 500  # 과거 데이터 포인트 수
    update_interval = 0.01  # 업데이트 간격(초)

    while True:
        df = fetch_ohlcv(symbol, limit=limit)
        df = calculate_rsi(df)

        # 최근 RSI 값 출력
        #print(df[['timestamp', 'RSI_6', 'RSI_12', 'RSI_24']].tail(1))

        # 최근 RSI_6 값 출력 및 변수에 저장
        recent_rsi_6 = df['RSI_6'].iloc[-1]
        print(f"Recent RSI_6: {recent_rsi_6:.2f}")

        time.sleep(update_interval)

if __name__ == "__main__":
    main()


