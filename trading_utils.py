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
    
#수수료 반영된 포지션 사이즈 계산 함수
def calculate_position_size(usdt_balance, cur_price, leverage, fee_rate):
    portion = 0.95  # 잔고의 95% 사용수수료에 의한 거래 실패 방지
    usdt_trade = usdt_balance * portion  # 거래할 USDT 양 계산
    print(f"usdt_balance 수량 : {usdt_balance}")
    print(f"usdt_trade 수량 : {usdt_trade}")
    
    # 포지션 크기 계산
    amount = (usdt_trade / cur_price) * leverage / (1 + fee_rate)
    amount = math.floor(amount * 1000) / 1000  # BTC의 경우 소수점 셋째 자리로 내림
    print(f"계산된 거래량(수수료 포함): {amount}")
    
    # 최소 거래량 체크
    min_btc_trade_size = 0.001
    if amount < min_btc_trade_size:
        print(f"계산된 거래량 {amount}이 최소 거래량 {min_btc_trade_size} BTC보다 작습니다.")
        raise ValueError(f"계산된 거래량 {amount}이 최소 거래량 {min_btc_trade_size} BTC보다 작습니다.")
    
    return amount

def is_position_open(exchange, symbol):
    balance = exchange.fetch_balance()  # 잔고 정보 가져오기
    positions = balance['info']['positions']  # 포지션 정보 가져오기
    btc_positions = [position for position in positions if position['symbol'] == symbol.replace('/', '')]  # 해당 심볼의 포지션 필터링
    position = btc_positions[0] if btc_positions else None  # 첫 번째 포지션 선택
    initial_margin = float(position['initialMargin']) if position else 0  # 초기 마진 값 가져오기
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

def binance_long(exchange, symbol, sl, tp, leverage):
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

def binance_long_with_max_margin(exchange, symbol, sl, tp, leverage, fee_rate):
    cur_price = exchange.fetch_ticker(symbol)['last']  # 현재 가격 가져오기
    balance = exchange.fetch_balance(params={"type": "future"})  # 선물 잔고 가져오기
    usdt = balance['total']['USDT']

    # 수수료를 반영한 포지션 크기 계산
    Amount = calculate_position_size(usdt, cur_price, leverage, fee_rate)
    
    try:
        # 시장가 주문 생성
        exchange.create_market_buy_order(symbol=symbol, amount=Amount)

        # 스탑로스와 타겟 프로핏 설정
        sl_price = round(cur_price * (1 - sl / leverage), 2)
        tp_price = round(cur_price * (1 + tp / leverage), 2)
        set_stop_loss_take_profit(exchange, symbol, Amount, sl_price, tp_price)
    except Exception as e:
        print(f"거래 생성 중 오류 발생: {e}")