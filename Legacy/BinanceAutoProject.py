import ccxt  # ccxt 라이브러리를 가져와 거래소 API를 사용
import pandas as pd  # pandas 라이브러리를 가져와 데이터 처리를 쉽게 함
import time  # time 라이브러리를 가져와 대기 시간을 설정
import math  # math 라이브러리를 가져와 수학적 계산 수행
import csv  # csv 라이브러리를 가져와 CSV 파일 작업 수행
import datetime as dt  # datetime 라이브러리를 dt로 가져와 날짜 및 시간 작업 수행
import subprocess  # subprocess 모듈을 가져와 외부 명령 실행
import sys  # sys 모듈을 가져와 프로그램 재실행
import os #os 라이브러리를 이용, pc의 시간 설정 재 기동

from RsiNew import get_recent_rsi  # 만둘어둔 RsiNew 모듈에서 get_recent_rsi 함수를 가져옴

print('Binance Automatic Futures trade Processing working.... ')  # 프로그램 시작을 알리는 메시지 출력

# api.txt 파일에서 API 키와 비밀 키를 읽어옴
with open("api.txt") as api_file:
    lines = api_file.readlines()  # 파일의 모든 라인을 읽어들임
    api_key = lines[0].strip()  # 첫 번째 줄에서 API 키를 읽어옴
    secret = lines[1].strip()  # 두 번째 줄에서 비밀 키를 읽어옴

# Binance 인스턴스를 생성할 때 API 키와 비밀 키를 설정
binance = ccxt.binance({
    'apiKey': api_key,  # API 키 설정
    'secret': secret,  # 비밀 키 설정
    'enableRateLimit': True,  # 속도 제한을 활성화하여 API 호출 속도를 관리
    'options': {
        'defaultType': 'future'  # 기본 시장 타입을 선물로 설정
    }
})

print("Start")  # 시작 메시지 출력

try:
    # 심볼과 레버리지 정하기 (1회)
    markets = binance.load_markets()  # 거래 가능한 모든 시장을 로드
    symbol = "BTC/USDT"  # 거래할 심볼 설정
    leverage = 75  # 레버리지 설정
    imr = 1 / leverage  # 초기 마진 비율 계산

    # 레버리지 설정
    binance.fapiprivate_get_positionside_dual({
        'symbol': symbol.replace('/', ''),  # 심볼에서 슬래시를 제거하고 설정
        'leverage': leverage  # 설정한 레버리지 값 설정
    })

    # 전역 변수들 초기화
    count = 0  # 거래 횟수 카운트 초기화
    start_seed = 0  # 시작 시드 초기화
    finish_seed = 0 # 종료 시드 초기화
    daytime = dt.datetime.now()  # 현재 시간 가져오기
    days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']  # 요일 리스트
    day = dt.datetime.today().weekday()  # 오늘의 요일 인덱스 가져오기
    today_profit = 0  # 오늘의 수익 초기화
    today_result = None  # 오늘의 결과 초기화
    last_amount = 0  # 마지막 거래량 초기화
    start_position = 0  # 시작 포지션 초기화
    isItFirst = False # 프로그램 시작 시 첫 실행 여부를 확인하는 변수

    # 잔고 계산 함수
    def cal_amount(usdt_balance, cur_price):
        portion = 0.95  # 잔고의 95% 사용
        usdt_trade = usdt_balance * portion  # 거래할 USDT 양 계산
        amount = math.floor((usdt_trade * 1000000) / cur_price) / 1000000 * leverage  # 거래량 계산
        return amount

    balance = binance.fetch_balance(params={"type": "future"})  # 선물 잔고 가져오기
    usdt = balance['total']['USDT']  # 총 USDT 잔고 가져오기

    # 티커 정보를 한 번만 가져옴
    ticker = binance.fetch_ticker(symbol)  # 티커 정보 가져오기
    cur_price = ticker['last']  # 현재 가격 가져오기

    # 포지션 상태 확인 함수
    def is_position_open():
        # 포지션 리스크 정보 가져오기
        #포지션이 있으면 true를, 없으면 false를 반환한다.
        balance = binance.fetch_balance()
        positions = balance['info']['positions']
        
        # BTC/USDT 포지션 필터링
        btc_positions = [position for position in positions if position['symbol'] == symbol.replace('/', '')]
        
        # 첫 번째 포지션 가져오기 (여기서는 한 개만 있다고 가정)
        position = btc_positions[0]
        
        # 'initialMargin' 값 확인
        initial_margin = float(position['initialMargin'])
        
        # initialMargin이 0이면 포지션이 없다고 간주
        if initial_margin == 0:
            cancel_all_orders()
            return False #없으면 false
        else:
            return True # 포지션이 열려있으면 true

    # 모든 주문 취소 함수
    def cancel_all_orders():
        orders = binance.fetch_open_orders(symbol=symbol)
        for order in orders:
            binance.cancel_order(order['id'], symbol)
    
    # 포지션 설정 함수
    def binance_long(sl,tp):
        global cur_price, start_position, last_amount, count, daytime, start_seed
        cur_price = binance.fetch_ticker(symbol)['last']  # 현재 가격 가져오기

        #일단 있는 오더들 전부 삭제 그 후 거래시작
        cancel_all_orders()
        
        balance = binance.fetch_balance(params={"type": "future"})  # 선물 잔고 가져오기
        usdt = balance['total']['USDT']
        start_seed = usdt
        entry_price = 0.0
        
        order = binance.create_market_buy_order(
            symbol=symbol,  # 거래할 심볼 설정
            amount=cal_amount(usdt, cur_price)  # 거래량 계산 후 매수 주문 생성
        )
        
        last_amount = cal_amount(usdt, cur_price)  # 마지막 거래량 저장

        """
        수정해야한다. 정확한 시작지점을 알아내기 위해선
        position을 가져오는 함수를 이용하여 대입하는것이 더 정확하다.
        entryprice 값을 넣어야한다.
        """
        #거래 entry 값을 얻어내는 코드
        balance = binance.fetch_balance()
        positions = balance['info']['positions']
        btc_positions = [position for position in positions if position['symbol'] == 'BTCUSDT']
        for position in btc_positions:
            entry_price = position['entryPrice']
        entry_price = float(entry_price)

        #스탑로스, 타겟 프로핏을 설정하는 코드와 함수
        sl_price = round(entry_price * (1 - sl / leverage), 2)  # 스탑 로스 가격 계산
        tp_price = round(entry_price * (1 + tp / leverage), 2)  # 타겟 프로핏 가격 계산
        set_stop_loss_take_profit(sl_price, tp_price)  # 스탑 로스와 타겟 프로핏 설정
        
        print("거래 시작")  # 거래 시작 메시지 출력
        print("오늘 날짜 =", daytime)  # 현재 날짜 출력
        print("오늘 요일 =", days[day])  # 오늘 요일 출력
        print("시작 비트 가격 =", entry_price)  # 시작 가격 출력
        print("현재 내 남은 잔고 =", round(balance['USDT']['free'], 2))  # 남은잔고 출력
        print("현재 레버리지 =", leverage)  # 레버리지 출력
        print("", end="\n")

    # 스탑 로스와 타겟 프로핏 설정 함수
    def set_stop_loss_take_profit(sl_price, tp_price):
        global symbol, last_amount
        binance.create_order(
            symbol=symbol,  # 거래할 심볼 설정
            type='STOP_MARKET',  # 주문 타입 설정
            side='sell',  # 매도 주문 설정
            amount=last_amount,  # 거래량 설정
            params={'stopPrice': sl_price}  # 스탑 로스 가격 설정
        )
        binance.create_order(
            symbol=symbol,  # 거래할 심볼 설정
            type='TAKE_PROFIT_MARKET',  # 주문 타입 설정
            side='sell',  # 매도 주문 설정
            amount=last_amount,  # 거래량 설정
            params={'stopPrice': tp_price}  # 타겟 프로핏 가격 설정
        )

    # 포지션 종료 함수
    def binance_short():
        global count
        order = binance.create_market_sell_order(
            symbol=symbol,  # 거래할 심볼 설정
            amount=last_amount  # 매도 주문 생성
        )
        count = 0  # 거래 횟수 초기화

    # 거래 히스토리 가져오기
    def get_trade_history():
        return binance.fetch_my_trades(symbol, since=None, limit=4)  # 최근 10개의 거래 히스토리 가져오기

    # CSV 파일의 마지막 행 읽기
    def read_last_csv_entry(filename='binance.csv'):
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()  # 파일의 모든 라인 읽기
                if lines:
                    last_line = lines[-1]  # 마지막 라인 가져오기
                    return last_line.strip().split(',')  # 마지막 라인을 리스트로 반환
                return None
        except (IndexError, FileNotFoundError):
            return None  # 파일이 없거나 읽을 라인이 없으면 None 반환

    # 매매 완료 내역 기록 함수
    def record_trade(buy_trade, sell_trade):
        global isItFirst, start_seed, finish_seed  # 전역 변수로 선언
        entry_price = float(buy_trade['price'])  # 매매 돌입 가격
        exit_price = float(sell_trade['price'])  # 매매 종료 가격
        pnl = float(sell_trade['info'].get('realizedPnl', 0))  # 오늘의 수익, 기본값 0
        entry_time = dt.datetime.fromtimestamp(buy_trade['timestamp'] / 1000)  # 매매 돌입 시간
        exit_time = dt.datetime.fromtimestamp(sell_trade['timestamp'] / 1000)  # 매매 종료 시간
        result = '승' if pnl > 0 else '패' if pnl < 0 else '무'  # 승무패 결과

        balance = binance.fetch_balance(params={"type": "future"})  # 선물 잔고 가져오기
        usdt = balance['total']['USDT']
        finish_seed = usdt
        
        # 기존 CSV 파일의 마지막 엔트리 가져오기
        last_entry = read_last_csv_entry()
        
        # 기존 엔트리와 비교
        if isItFirst:
            if last_entry:
                last_entry_price = float(last_entry[1])
                last_exit_price = float(last_entry[2])
                last_pnl = float(last_entry[3])
                last_entry_time = dt.datetime.strptime(last_entry[5], '%Y-%m-%d %H:%M:%S')
                last_exit_time = dt.datetime.strptime(last_entry[6], '%Y-%m-%d %H:%M:%S')
                last_result = last_entry[7]
                
            
            # 현재 거래와 마지막 기록된 거래가 동일한지 확인
            if (entry_price == last_entry_price and exit_price == last_exit_price and 
                pnl == last_pnl and entry_time == last_entry_time and 
                exit_time == last_exit_time and result == last_result):
                print("거래 내역이 이미 기록되어 있습니다. 기록을 생략합니다.")
                return  # 동일하면 함수 종료
            
        else: #기존 엔트리가 아닌 
            if (entry_price == last_entry_price and exit_price == last_exit_price and 
                pnl == last_pnl and entry_time == last_entry_time and 
                exit_time == last_exit_time and result == last_result):
                print("거래 내역이 이미 기록되어 있습니다. 기록을 생략합니다.")
                return  # 동일하면 함수 종료
    
        # 매매 완료 내역 출력
        print(f"매매 완료 : (돌입가격 = {entry_price}), (마무리 가격 = {exit_price}), (오늘의 수익 = {pnl}), (매매 돌입 시간 = {entry_time}), (매매 종료 시간 = {exit_time}), (승무패 = {result})")
        print("", end="\n")

        # 매매 완료 내역을 CSV 파일에 기록
        with open('binance.csv', 'a', encoding='utf-8-sig', newline='') as f:
            wr = csv.writer(f)
            wr.writerow([start_seed,entry_price, exit_price, pnl,finish_seed, entry_time.strftime('%Y-%m-%d %H:%M:%S'), exit_time.strftime('%Y-%m-%d %H:%M:%S'), result,75])
            start_seed = 0
            finish_seed = 0
            isItFirst = True

    # CSV 파일이 없으면 생성하고 기본 헤더 작성
    def initialize_csv(filename='binance.csv'):
        trades = get_trade_history()
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(['Start Seed','Entry Price', 'Exit Price', 'Profit/Loss', 'Finish Seed' ,'Entry Time', 'Exit Time', 'Result', 'Leverage'])  # CSV 헤더 작성
        #for i in range(len(trades) - 1, 0, -1):
        #    if trades[i]['side'] == 'sell' and trades[i - 1]['side'] == 'buy' and trades[i]['order'] != trades[i - 1]['order']:
        #        record_trade(trades[i - 1], trades[i])
        for i in range(len(trades) - 1):
            if trades[i]['side'] == 'buy' and trades[i + 1]['side'] == 'sell' and trades[i]['order'] != trades[i + 1]['order']:
                record_trade(trades[i], trades[i + 1])
                
    
    # 메인 로직
    position_open = False  # 포지션 상태를 추적하는 변수
    result_recorded = False  # 결과 기록 여부를 추적하는 변수

    # CSV 파일 초기화 (존재하지 않는 경우)
    if read_last_csv_entry() is None:
        initialize_csv()

    while True:
        # 네트워크 요청 빈도는 기존대로 유지
        balance = binance.fetch_balance(params={"type": "future"})  # 선물 잔고 가져오기
        usdt = balance['total']['USDT']  # 총 USDT 잔고 가져오기
        ticker = binance.fetch_ticker(symbol)  # 티커 정보 가져오기
        cur_price = ticker['last']  # 현재 가격 가져오기
        
        daytime = dt.datetime.now()  # 현재 시간 가져오기
        day = dt.datetime.today().weekday()  # 오늘의 요일 인덱스 가져오기
        
        recent_rsi_6 = get_recent_rsi(symbol, limit=500)  # 최근 RSI 값 가져오기
        
        if 21 <= daytime.hour < 22:
            sl_multiplier = 0.15  # 21:00~22:00 사이 스탑로스 배수 설정
            tp_multiplier = 0.23 # 타겟 프로핏 배수 설정 
            rsi_threshold = 7  # 21:00~22:00 사이 RSI 임계값 설정
        else:
            sl_multiplier = 0.15  # 스탑로스 배수 설정
            tp_multiplier = 0.3 # 타겟 프로핏 배수 설정
            rsi_threshold = 4  # 나머지 시간 RSI 임계값 설정

        # 포지션이 없는 경우에만 새로운 포지션을 염
        if recent_rsi_6 <= rsi_threshold and not is_position_open() and not position_open:
            cancel_all_orders()
            print(f" 포지션 돌입시점 RSI : {recent_rsi_6:.2f}, 돌입 가격 : {cur_price}")
            binance_long(sl_multiplier,tp_multiplier) #sl,tp순
            result_recorded = False
            position_open = True

        # 포지션이 닫힌 경우 결과를 기록 (한 번만)
        # 포지션이 열렸다 닫힌걸 아는 방법
        # position_open =이 true이고 is_position_open()이 false면
        # 거래가 한번 생성되어 position_open이 바뀐것이고,
        # is_position_open()은 false인것은 거래가 종료되어 포지션이 없다는뜻.
        if position_open and not is_position_open() and not result_recorded:
            trades = get_trade_history()
            for i in range(len(trades) - 1, 0, -1):
                if trades[i]['side'] == 'sell' and trades[i - 1]['side'] == 'buy' and trades[i]['order'] != trades[i - 1]['order']:
                    record_trade(trades[i - 1], trades[i])
                    result_recorded = True
                    position_open = False
        
        #포지션이 없을시
        if not is_position_open():
            cancel_all_orders()

        time.sleep(0.1)  # 0.1초 대기

except ccxt.BaseError as e:
    print(f"An error occurred: {e}")  # 예외 발생 시 오류 메시지 출력
