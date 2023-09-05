from Log.Loging import log, inv_log
import config as cng
from Utils.EVMutils import EVM
from json import loads
import random
import hmac
import base64
import requests
import time
import datetime


def okx_data(api_key, secret_key, passphras, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):
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

        base_url = "https://www.okex.com"
        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": passphras,
            'x-simulated-trading': '0'
        }
        return base_url, request_path, headers
    except Exception as ex:
        log().error(ex)
        raise ValueError(ex)


def fee_chain():
    try:
        chain_token = ['BNB', 'AVAX', 'MATIC', 'ETH', 'FTM']
        chain = ['ETH-Arbitrum One', 'AVAX-Avalanche C-Chain', 'BNB-BSC', 'FTM-Fantom', 'MATIC-Polygon',
                 "ETH-zkSync Era", "ETH-ERC20"]
        _, _, headers = okx_data(cng.OKX_api_key, cng.OKX_secret_key, cng.OKX_password,
                                 request_path=f"/api/v5/asset/currencies",
                                 meth="GET")
        reponse = requests.get("https://www.okx.cab/api/v5/asset/currencies", timeout=10, headers=headers)
        rep = loads(reponse.text)
        fee_network = {}
        if "data" in rep:
            for i in rep['data']:
                if i['ccy'] in chain_token:
                    if i["chain"] in chain:
                        fee_network[i["chain"].replace(i['ccy'] + '-', '')] = i["minFee"]
        else:
            log().error(rep)
            time.sleep(15)
            return fee_chain()
        return fee_network
    except BaseException as errors:
        inv_log().error(errors)
        raise BaseException(errors)


def okx_withdraw(chains: list, address: str, value: (int, float), retry=0):
    name_chain = {
        "bsc": "BSC",
        "ethereum": "ERC20",
        "polygon": "Polygon",
        "avalanche": "Avalanche C-Chain",
        "arbitrum": "Arbitrum One",
        "optimism": "Optimism",
        "fantom": "Fantom",
        "zksync": "zkSync Era"
    }
    name_native = {
        'bsc': 'BNB',
        'avalanche': 'AVAX',
        'polygon': 'MATIC',
        'optimism': 'ETH',
        'arbitrum': 'ETH',
        'fantom': 'FTM',
        'zksync': 'ETH',
        'ethereum': 'ETH'
                   }
    random.shuffle(chains)
    fee = fee_chain()
    for chain in chains:
        SYMBOL = name_native[chain]
        CHAIN = name_chain[chain]
        FEE = fee[CHAIN]
        api_key = cng.OKX_api_key
        secret_key = cng.OKX_secret_key
        passphras = cng.OKX_password

        # if is_private_key == True:
        #     wallet = evm_wallet(privatekey)
        # else:
        #     wallet = privatekey

        try:
            try:
                _, _, headers = okx_data(api_key, secret_key, passphras,
                                         request_path=f"/api/v5/account/balance?ccy={SYMBOL}")
                balance = requests.get(f'https://www.okx.cab/api/v5/account/balance?ccy={SYMBOL}', timeout=10,
                                       headers=headers)
                balance = balance.json()
                balance = balance["data"][0]["details"][0]["cashBal"]
                # print(balance)

                if balance != 0:
                    body = {"ccy": f"{SYMBOL}", "amt": float(balance), "from": 18, "to": 6, "type": "0",
                            "subAcct": "",
                            "clientId": "", "loanTrans": "", "omitPosRisk": ""}
                    _, _, headers = okx_data(api_key, secret_key, passphras, request_path=f"/api/v5/asset/transfer",
                                             body=str(body), meth="POST")
                    a = requests.post("https://www.okx.cab/api/v5/asset/transfer", data=str(body), timeout=10,
                                      headers=headers)
                    time.sleep(1)
            except Exception:
                pass
            if value:
                body = {"ccy": SYMBOL, "amt": value, "fee": FEE, "dest": "4", "chain": f"{SYMBOL}-{CHAIN}",
                        "toAddr": address}
                _, _, headers = okx_data(api_key, secret_key, passphras, request_path=f"/api/v5/asset/withdrawal",
                                         meth="POST",
                                         body=str(body))
                a = requests.post("https://www.okx.cab/api/v5/asset/withdrawal", data=str(body), timeout=10,
                                  headers=headers)
                result = a.json()

                if result['code'] == '0':
                    log().success(f"withdraw success => {address} | {value} {SYMBOL}")
                    time.sleep(EVM.randint_([15, 30]))
                else:
                    error = result['msg']
                    log().error(f"withdraw unsuccess => {address} {SYMBOL} {CHAIN} | error : {error}")
                    if error == 'Insufficient balance':
                        time.sleep(EVM.randint_([15, 30]))
                    elif retry < cng.RETRY:
                        log().info(f"try again in 10 sec. => {address}")
                        time.sleep(EVM.randint_([10, 10]))
                        return okx_withdraw(chains, address, retry + 1)

        except Exception as error:
            log().error(f"withdraw unsuccess => {address} | error : {error}")
            if retry < cng.RETRY:
                log().info(f"try again in 10 sec. => {address}")
                time.sleep(10)
                return okx_withdraw(chains, address, retry + 1)


if __name__ == '__main__':
    pass
