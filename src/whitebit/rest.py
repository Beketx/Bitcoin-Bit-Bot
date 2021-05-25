import json
import base64
import requests
import time
import hmac
import hashlib


class WhiteBitClient:
    def __init__(self, API_KEY, API_SECRET, host="https://whitebit.com"):
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.host = host  # last slash. Do not use https://whitebit.com/

    def signature_payload(self, data):
        data_json = json.dumps(data, separators=(',', ':'))  # use separators param for deleting spaces
        payload = base64.b64encode(data_json.encode('ascii'))
        signature = hmac.new(self.API_SECRET.encode('ascii'), payload, hashlib.sha512).hexdigest()
        return payload, signature, data_json

    def ticker(self, coin):
        request = '/api/v1/public/ticker?market={}'.format(coin)
        nonce = str(int(time.time()))

        data = {
            'ticker': '{}'.format(coin),  # for example for obtaining trading balance for BTC currency
            'request': request,
            'nonce': nonce
        }

        complete_url = self.host + request

        payload, signature, data_json = self.signature_payload(data)

        headers = {
            'Content-type': 'application/json',
            'X-TXC-APIKEY': self.API_KEY,
            'X-TXC-PAYLOAD': payload,
            'X-TXC-SIGNATURE': signature,
        }

        resp = requests.get(complete_url)
        resp_json = resp.json()

        if resp_json["success"]:
            return resp_json
        else:
            print(resp_json)
            return None

    def buy_order_market(self, market, amount):
        """
            curl --location --request POST 'https://whitebit.com/api/v1/order/new' \
                    --header 'Content-Type: application/json' \
                    --header 'X-TXC-APIKEY: XXXXXXX' \
                    --header 'X-TXC-PAYLOAD: XXXXXXX' \
                    --header 'X-TXC-SIGNATURE: XXXXXXX' \
                    --data-raw '{
            "market": "ETH_BTC",
            "side": "buy",
            "amount": "0.001",
            "price": "1000",

            put here request path. Example, for obtaining trading balance use: /api/v4/trade-account/balance
            "request": "/api/v4/order/new",

            nonce is a number that is always higher than the previous request number
            "nonce": "1577450895353"
            }'
        """
        try:
            request = '/api/v4/order/market'
            nonce = str(int(time.time()))

            paydata = {
                "market": "{}".format(market),
                "side": "buy",
                "amount": "{}".format(amount),
                "request": request,
                "nonce": nonce
            }

            complete_url = self.host + request

            payload, signature, data_json = self.signature_payload(paydata)

            headers = {'Content-Type': 'application/json',
                       'X-TXC-APIKEY': '{}'.format(self.API_KEY),
                       'X-TXC-PAYLOAD': '{}'.format(payload.decode("ascii")),
                       'X-TXC-SIGNATURE': '{}'.format(signature),
                       }

            resp = requests.post(complete_url, headers=headers, data=data_json)
            json_data = json.loads(resp.text)
            return resp
        except Exception as e:
            result = {"FAIL": "Transaction for \"BUY\" {} has't done, Amount was {}".format(market, amount),
                      "Error": e}
            print(result)
            return None

    def sell_order_market(self, market, amount):
        """
        curl --location --request POST 'https://whitebit.com/api/v4/order/new' \
        --header 'Content-Type: application/json' \
        --header 'X-TXC-APIKEY: XXXXX' \
        --header 'X-TXC-PAYLOAD: XXXXXX' \
        --header 'X-TXC-SIGNATURE: XXXXXX' \
        --data-raw '{
            "market": "BTC_USD",
            "side": "sell",
            "amount": "0.3",
            "price": "7064",

            put here request path. For obtaining trading balance use: /api/v4/trade-account/balance
            "request": "/api/v4/main-account/balance",

            nonce: is a number that is always higher than the previous request number
            If the nonce is similar to or lower than the previous request number,
            you will receive the 'too many requests' error message
            "nonce": "1577450895353"
        }'
        """
        try:
            request = '/api/v4/order/market'
            nonce = str(int(time.time()))

            paydata = {
                "market": "{}".format(market),
                "side": "sell",
                "amount": "{}".format(amount),
                "request": request,
                "nonce": nonce
            }

            complete_url = self.host + request

            payload, signature, data_json = self.signature_payload(paydata)

            headers = {
                'Content-Type': 'application/json',
                'X-TXC-APIKEY': '{}'.format(self.API_KEY),
                'X-TXC-PAYLOAD': '{}'.format(payload.decode("ascii")),
                'X-TXC-SIGNATURE': '{}'.format(signature),
            }

            resp = requests.post(complete_url, headers=headers, data=data_json)
            json_data = json.loads(resp.text)
            return resp
        except Exception as e:
            result = {"FAIL": "Transaction for \"BUY\" {} has't done, Amount was {}".format(market, amount),
                      "Error": e}
            print(result)
            return None

    def get_wallets(self):
        """
        curl --location --request POST 'https://whitebit.com/api/v1/account/balances' \
        --header 'Content-Type: application/json' \
        --header 'X-TXC-APIKEY: XXXXX' \
        --header 'X-TXC-PAYLOAD: XXXXX' \
        --header 'X-TXC-SIGNATURE: XXXXXX' \
        --data-raw '{
            "request": "/api/v1/account/balance",
            "nonce": "1577450895353"
        }'
        """
        try:
            request = '/api/v1/account/balances'
            nonce = str(int(time.time()))

            paydata = {
                "request": request,
                "nonce": nonce
            }

            complete_url = self.host + request

            payload, signature, data_json = self.signature_payload(paydata)

            headers = {
                'Content-Type': 'application/json',
                'X-TXC-APIKEY': '{}'.format(self.API_KEY),
                'X-TXC-PAYLOAD': '{}'.format(payload.decode("ascii")),
                'X-TXC-SIGNATURE': '{}'.format(signature),
            }

            resp = requests.post(complete_url, headers=headers, data=data_json)
            json_data = json.loads(resp.text)
            return json_data
        except Exception as e:
            return None
