import time
from multiprocessing.dummy import Pool

from requests import get
from web3 import Web3

from Log.Loging import log
from pyuseragents import random as random_useragent
from eth_account import Account
from Strategies.ROUTE import wallet
import pandas as pd
from Utils.EVMutils import EVM


class Balance:
    def __init__(self):
        self.address = ''
        self.ETH = []
        self.fee = []
        self.tx = 0
        self.value = []
        self.active_contract = 0
        self.last_date = ''


class InfoBalance:
    def __init__(self, address, price_ETH):
        self.balance = Balance()
        self.address = address
        self.price_ETH = price_ETH

    def add_fee(self):
        url = f"https://block-explorer-api.mainnet.zksync.io/transactions?address={self.address}&limit=100&page=1"
        headers = {
            'user-agent': random_useragent(),
        }
        response = get(url, headers=headers).json()

        def fee_(data):
            fee = 0
            if data["items"]:
                for data_ in data["items"]:
                    if "fee" in data_:
                        fee += Web3.to_int(hexstr=data_["fee"])

            return EVM.DecimalTO(fee, 18) if fee > 0 else 0

        def contracts(data):
            contract = []
            if data["items"]:
                for data_ in data["items"]:
                    if data_["to"] not in contract:
                        contract.append(data_["to"])
            self.balance.active_contract = len(contract)
        fees = fee_(response)
        contracts(response)
        if int(response["meta"]["totalPages"]) > 1:
            url = url[:-1] + "2"
            response = get(url, headers=headers).json()
            fees += fee_(response)
        self.balance.fee = [round(fees, 3), round(fees * self.price_ETH, 3)]

    def add_value(self):
        decimal_token = {"ETH": 18, "WETH": 18, "BUSD": 18, "USDT": 6, "USDC": 6, "rfETH": 18, "rfUSDC": 6}
        headers = {
            'user-agent': random_useragent(),
        }
        value = 0

        response = get(f'https://block-explorer-api.mainnet.zksync.io/address/{self.address}/'
                       f'transfers?limit=100&page=1', headers=headers).json()
        json_data = response["items"]

        def cnculate(data_: dict):
            contract = ["0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91", "0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6",
                        "0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29", "0x8B791913eB07C32779a16750e3868aA8495F5964",
                        "0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d", "0x18381c0f738146Fb694DE18D1106BdE2BE040Fa4",
                        "0x943ac2310D9BC703d6AB5e5e76876e212100f894", '0xE0B015E54d54fc84a6cB9B666099c46adE9335FF']
            values = 0
            if data_:
                for data in data_:
                    if data["amount"] and data["token"]["symbol"] in decimal_token:
                        if data["from"] in contract or data["to"] in contract or data["from"] == self.address:
                            if "ETH" in data["token"]["symbol"]:
                                data["amount"] = int(data["amount"]) * self.price_ETH
                            values += EVM.DecimalTO(int(data["amount"]), decimal_token[data["token"]["symbol"]])
            return values

        value += cnculate(json_data)
        meta = int(response["meta"]["totalPages"])
        # self.balance.tx = response["meta"]["totalItems"]
        self.balance.last_date = response["items"][0]["timestamp"].split("T")[0]
        if meta > 1:
            response_2 = get(f'https://block-explorer-api.mainnet.zksync.io/address/{self.address}/'
                             f'transfers?limit=100&page=2', headers=headers).json()["items"]
            value += cnculate(response_2)
        self.balance.value = [round(value / self.price_ETH, 3), round(value, 1)]

    def get_info_wallet(self):
        self.add_fee()
        self.add_value()
        self.balance.address = self.address
        balances, _ = EVM.check_balance(self.address, "zksync", "")
        self.balance.ETH = [round(EVM.DecimalTO(balances, 18), 3), round(EVM.DecimalTO(balances, 18)
                                                                         * self.price_ETH, 3)]
        self.balance.tx = EVM.web3('zksync').eth.get_transaction_count(self.address)
        time.sleep(1)
        return self.balance

    @staticmethod
    def address_acc(private_key):
        try:
            address = Account.from_key(private_key).address
            return address
        except BaseException:
            return private_key


def get_info():
    decorate = {'Wallets': None, '*': None, '**': None, '***': None, '****': None,
                '*****': None, 'ETH': None, '$': None, 'Tx': None, '******': None, 'Value': None, 'Value$': None,
                'Fee': None, 'Fee$': None, 'Active Contract': None, '*******': None, 'Last date': None}
    address = [InfoBalance.address_acc(adr[0]) for adr in wallet()]
    save_balance = [decorate.copy() for _ in range(len(address))]
    price_ETH = EVM.prices_network("zksync")
    with Pool(10) as pols:
        all_balance = pols.map(lambda func: InfoBalance(func, price_ETH).get_info_wallet(), address)
    for i, balance in enumerate(all_balance):
        save_balance[i]['Wallets'] = balance.address
        save_balance[i]['ETH'] = balance.ETH[0]
        save_balance[i]['$'] = balance.ETH[1]
        save_balance[i]['Tx'] = balance.tx
        save_balance[i]['Value'] = balance.value[0]
        save_balance[i]['Value$'] = balance.value[1]
        save_balance[i]['Fee'] = balance.fee[0]
        save_balance[i]['Fee$'] = balance.fee[1]
        save_balance[i]['Active Contract'] = balance.active_contract
        save_balance[i]['Last date'] = balance.last_date

    soul = pd.DataFrame(save_balance)
    soul.to_excel('Info_acc.xlsx')

    log().success('File recorded Info_acc.xlsx')


if __name__ == '__main__':
    pass

