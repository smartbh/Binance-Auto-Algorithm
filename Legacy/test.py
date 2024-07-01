import ccxt
import talib as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


exchange = ccxt.binance()
symbol = 'BTC/USDT'
limit = 1500


candle = exchange.fetch_ohlcv(symbol=symbol, limit=limit)

df = pd.DataFrame(candle, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')


def calc_rsi(close, period):
    delta = close.diff()
    ups, downs = delta.copy(), delta.copy()
    ups[ups < 0] = 0
    downs[downs > 0] = 0

    au = ups.ewm(com=(period-1), min_periods=period).mean()
    ad = downs.abs().ewm(com=(period-1), min_periods=period).mean()

    rs = au / ad
    rsi = pd.Series(100 - (100 / (1 + rs)))

    return rsi


df['ta_rsi_6'] = ta.RSI(df['close'], timeperiod=6)
df['ta_rsi_12'] = ta.RSI(df['close'], timeperiod=12)
df['ta_rsi_24'] = ta.RSI(df['close'], timeperiod=24)
df['calc_rsi_6'] = calc_rsi(df['close'], period=6)

# print(round(df['ta_rsi_6'], 3))


fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=.01, row_heights=[0.4, 0.1, 0.1])

fig.add_trace(go.Candlestick(x=df['datetime'],
                             open=df['open'],
                             high=df['high'],
                             low=df['low'],
                             close=df['close'],
                             name='candle'))

color = ['blue' if row['open'] - row['close'] >= 0 else 'red' for index, row in df.iterrows()]
fig.add_trace(go.Bar(x=df['datetime'],
                     y=df['volume'],
                     marker_color=color,
                     name='volume'
                     ),
              row=2, col=1)

fig.add_trace(go.Scatter(x=df['datetime'],
                         y=df['ta_rsi_6'],
                         name='rsi_6'
                         ),
              row=3, col=1)

fig.add_trace(go.Scatter(x=df['datetime'],
                         y=df['ta_rsi_12'],
                         name='rsi_12'
                         ),
              row=3, col=1)

fig.add_trace(go.Scatter(x=df['datetime'],
                         y=df['ta_rsi_24'],
                         name='rsi_24'
                         ),
              row=3, col=1)

fig.add_annotation(x=df['datetime'][500],
                   y=df['close'][500],
                   text='point',
                   showarrow=True,
                   arrowhead=1,
                   row=1, col=1)

fig.update_layout(
    xaxis_rangeslider_visible=False,
    hovermode='x unified',
)
fig.update_yaxes(title_text='Price', row=1, col=1)
fig.update_yaxes(title_text='Volume', row=2, col=1)
fig.update_yaxes(title_text='RSI', row=3, col=1)
fig.show()


# print(df.loc['2024-02-12 10:07:00'])
# margin_candle = exchange.fetch_ohlcv(symbol=symbol, limit=10)
# target_value = 7
# target_column = 'Y'

# 해당 조건을 만족하는 행의 인덱스를 가져오기
# index_of_target_value = df[df[target_column] == target_value].index[0]

# print(f"좌표 ({df.loc[index_of_target_value, 'X']}, {df.loc[index_of_target_value, 'Y']})의 인덱스: {index_of_target_value}")

# print(margin_candle)