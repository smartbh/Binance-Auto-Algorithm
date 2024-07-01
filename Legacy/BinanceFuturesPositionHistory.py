import requests
import time
import hmac
import hashlib

class BinanceFuturesAPI:
    BASE_URL = "https://fapi.binance.com"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign(self, params):
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def _get(self, endpoint, params):
        params['timestamp'] = int(time.time() * 1000)
        params['signature'] = self._sign(params)
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        response = requests.get(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)
        return response.json()

    def get_account_trades(self, symbol, start_time=None, end_time=None, limit=500):
        endpoint = "/fapi/v1/userTrades"
        params = {
            'symbol': symbol,
            'limit': limit
        }
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return self._get(endpoint, params)
