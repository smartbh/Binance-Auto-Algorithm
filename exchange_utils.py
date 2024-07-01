#
#*------------------- Binance 초기화 및 공통 기능 제공 모듈 --------------*
#

import ccxt  # ccxt 라이브러리를 가져와 거래소 API를 사용

def initialize_binance(api_key, secret):
    return ccxt.binance({
        'apiKey': api_key,  # Binance API 키 설정
        'secret': secret,  # Binance 비밀 키 설정
        'enableRateLimit': True,  # 속도 제한을 활성화하여 API 호출 속도 관리
        'options': {
            'defaultType': 'future'  # 기본 시장 타입을 선물로 설정
        }
    })

def fetch_balance(exchange):
    return exchange.fetch_balance(params={"type": "future"})  # 선물 잔고 가져오기

def fetch_ticker(exchange, symbol):
    return exchange.fetch_ticker(symbol)['last']  # 현재 심볼 가격 가져오기

def cancel_all_orders(exchange, symbol):
    orders = exchange.fetch_open_orders(symbol=symbol)  # 현재 열린 주문 가져오기
    for order in orders:  # 각 주문을 순회하며
        exchange.cancel_order(order['id'], symbol)  # 주문 취소
