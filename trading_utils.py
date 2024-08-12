#
#*------------------- 거래 관련 기능 --------------------*
#


import math  # 수학적 계산을 수행하기 위해 math 라이브러리를 가져옴
import ccxt  # ccxt 라이브러리를 가져와 거래소 API를 사용
from exchange_utils import fetch_ticker, fetch_balance, cancel_all_orders

def cal_amount(usdt_balance, cur_price, leverage):
    portion = 0.95  # 잔고의 95%를 거래에 사용
    usdt_trade = usdt_balance * portion  # 거래할 USDT 양 계산
    amount = math.floor((usdt_trade * 1000000) / cur_price) / 1000000 * leverage  # 거래량 계산
    return amount

def is_position_open(exchange, symbol):
    balance = exchange.fetch_balance()  # 잔고 정보 가져오기
    positions = balance['info']['positions']  # 포지션 정보 가져오기
    btc_positions = [position for position in positions if position['symbol'] == symbol.replace('/', '')]  # 해당 심볼의 포지션 필터링
    print(f"btc_positions : {btc_positions}")
    position = btc_positions[0] if btc_positions else None  # 첫 번째 포지션 선택
    print(f"position : {position}")
    initial_margin = float(position['initialMargin']) if position else 0  # 초기 마진 값 가져오기
    print(f"initial_margin : {initial_margin}")
    print(f"initial_margin : {initial_margin != 0}")
    return initial_margin != 0  # 초기 마진 값이 0이 아니면 포지션이 열려있다고 간주

def fetch_entry_price(exchange, symbol):
    balance = exchange.fetch_balance()  # 잔고 정보 가져오기
    positions = balance['info']['positions']  # 포지션 정보 가져오기
    btc_positions = [position for position in positions if position['symbol'] == symbol.replace('/', '')]  # 해당 심볼의 포지션 필터링
    entry_price = float(btc_positions[0]['entryPrice']) if btc_positions else 0.0  # 엔트리 가격 가져오기
    return entry_price

def set_stop_loss_take_profit(exchange, symbol, amount, sl_price, tp_price):
    exchange.create_order(symbol=symbol, type='STOP_MARKET', side='sell', amount=amount, params={'stopPrice': sl_price})  # 스탑 로스 설정
    exchange.create_order(symbol=symbol, type='TAKE_PROFIT_MARKET', side='sell', amount=amount, params={'stopPrice': tp_price})  # 타겟 프로핏 설정

def binance_long(exchange, symbol, sl, tp, leverage, volume_list):
    cur_price = fetch_ticker(exchange, symbol)  # 현재 가격 가져오기
    cancel_all_orders(exchange, symbol)  # 모든 주문 취소
    balance = fetch_balance(exchange)  # 잔고 정보 가져오기
    usdt = balance['total']['USDT']  # 총 USDT 잔고 가져오기
    amount = cal_amount(usdt, cur_price, leverage)  # 거래량 계산
    exchange.create_market_buy_order(symbol=symbol, amount=amount)  # 시장 매수 주문 생성
    entry_price = fetch_entry_price(exchange, symbol)  # 엔트리 가격 가져오기
    sl_price = round(entry_price * (1 - sl / leverage), 2)  # 스탑 로스 가격 계산
    tp_price = round(entry_price * (1 + tp / leverage), 2)  # 타겟 프로핏 가격 계산
    set_stop_loss_take_profit(exchange, symbol, amount, sl_price, tp_price)  # 스탑 로스와 타겟 프로핏 설정
