import json
from json import loads
import random
import hmac
import base64
import requests
import time
import datetime
from config import api_BitGet, secret_BitGet, pass_BitGet
from Log.Loging import log, inv_log


class BitGetTr:
    @staticmethod
    def sing(request_path="/api/spot/v1/account/assets", body='', meth="GET"):
        try:

            def signature(timestamp: str, method: str, request_path: str, secret_key: str, body: str = "") -> str:
                if not body:
                    body = ""

                message = timestamp + method.upper() + request_path + body
                mac = hmac.new(
                    bytes(secret_key, encoding="utf-8"),
                    bytes(message, encoding="utf-8"),
                    digestmod="sha256",
                )
                d = mac.digest()
                return base64.b64encode(d).decode("utf-8")

            dt_now = datetime.datetime.utcnow()
            ms = str(dt_now.microsecond).zfill(6)[:3]
            timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

            base_url = "https://api.bitget.com"
            headers = {
                "Content-Type": "application/json",
                "ACCESS-KEY": api_BitGet,
                "ACCESS-SIGN": signature(timestamp, meth, request_path, secret_BitGet, body),
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": pass_BitGet,
                'x-simulated-trading': '0',
                "locale": "en-US",
            }
            return base_url, request_path, headers
        except Exception as ex:
            raise ValueError(ex)

    @staticmethod
    def get_uid():
        try:
            patch = '/api/spot/v1/account/getInfo'
            _, _, headers = BitGetTr.sing(request_path=patch, meth="GET")
            reponse = requests.get(f"https://api.bitget.com{patch}", timeout=10, headers=headers)
            return int(json.loads(reponse.text)['data']['user_id'])
        except BaseException as error:
            inv_log().error(f'{error}')
            time.sleep(10)
            return BitGetTr.get_uid()

    @staticmethod
    def get_steable():
        try:
            patch = '/api/spot/v1/account/assets'
            _, _, headers = BitGetTr.sing(request_path=patch, meth="GET")
            reponse = requests.get(f"https://api.bitget.com{patch}", timeout=10, headers=headers)
            rep = loads(reponse.text)
            for i in rep['data']:
                if i['coinName'] == 'USDT':
                    return float(i['available'])
        except BaseException as error:
            log().error(f'{error}')
            time.sleep(10)
            return BitGetTr.get_steable()

    @staticmethod
    def get_sub_tokens():
        try:
            patch = '/api/spot/v1/account/sub-account-spot-assets'
            _, _, headers = BitGetTr.sing(request_path=patch, meth="POST")
            reponse = requests.post(f"https://api.bitget.com{patch}", timeout=10, headers=headers)
            rep = loads(reponse.text)
            balance = {}
            for i in rep['data']:
                balance[i['userId']] = []
                for j in i['spotAssetsList']:
                    balance[i['userId']].append([j['coinName'], j['available']])
            return balance
        except BaseException:
            return {}

    @staticmethod
    def transfer(sub_id, list_):
        try:
            uid = BitGetTr.get_uid()
            patch = '/api/spot/v1/wallet/subTransfer'
            body = {"fromType": "spot", "toType": "spot", "amount": float(list_[1]), "coin": list_[0],
                    "clientOid": random.randint(100_000, 999_999),
                    "fromUserId": int(sub_id), "toUserId": uid}
            body = json.dumps(body)
            _, _, headers = BitGetTr.sing(request_path=patch, body=str(body), meth="POST")
            reponse = requests.post(f"https://api.bitget.com{patch}", timeout=10, headers=headers, data=str(body))
            if reponse.status_code == 200:
                print(f'transfer sub_id {sub_id}, coin {list_[0]}, amount {float(list_[1])}')
            else:
                print('----')
        except BaseException as error:
            log().error(f'{error}')
            time.sleep(15)
            BitGetTr.transfer(sub_id, list_)

    @staticmethod
    def get_sub_list():
        patch = '/api/user/v1/sub/virtual-list'

        _, _, headers = BitGetTr.sing(request_path=patch, meth="GET")
        reponse = requests.get(f"https://api.bitget.com{patch}", timeout=10, headers=headers)
        print(reponse.text)

    @staticmethod
    def withdrawal(token_name, to_address, amount, chain):
        patch = '/api/spot/v1/wallet/withdrawal-v2'
        body = {"coin": token_name, "address": to_address, "chain": chain, "amount": amount}
        body = json.dumps(body)
        _, _, headers = BitGetTr.sing(request_path=patch, body=str(body), meth="POST")
        reponse = requests.post(f"https://api.bitget.com{patch}", timeout=10, headers=headers, data=str(body))
        try:
            if json.loads(reponse.text)["msg"] == "success":
                inv_log().success(reponse.text)
                return True
            else:
                inv_log().error(reponse.text)
                inv_log().error(body)
                return False
        except BaseException:
            log().error(reponse.text)
            return False

    @staticmethod
    def transfer_sub():
        try:
            sub_balance = BitGetTr.get_sub_tokens()
            time.sleep(1)
            for sub_id, balance_all in sub_balance.items():
                for balance in balance_all:
                    BitGetTr.transfer(sub_id, balance)
                    time.sleep(1)
                time.sleep(1)
        except BaseException:
            time.sleep(3)