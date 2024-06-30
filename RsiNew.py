# RsiNew.py

import ccxt
import pandas as pd
import talib as ta

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

def calculate_rsi(df, periods=[6]):
    for period in periods:
        df[f'RSI_{period}'] = ta.RSI(df['close'], timeperiod=period)
    return df

def get_recent_rsi(symbol='BTC/USDT', limit=500):
    df = fetch_ohlcv(symbol, limit=limit)
    df = calculate_rsi(df)
    recent_rsi_6 = df['RSI_6'].iloc[-1]
    return recent_rsi_6
