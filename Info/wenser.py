import time
from multiprocessing.dummy import Pool

from requests import get

from Log.Loging import log
from pyuseragents import random as random_useragent
from eth_account import Account
from Strategies.ROUTE import wallet
import pandas as pd
from json import loads


class Balance:
    def __init__(self):
        self.address = ''
        self.ETH = []
        self.fee = []
        self.tx = 0
        self.value = []
        self.active_contract = 0
        self.last_date = ''


def get_info_wallet(address):
    headers = {
        'authority': 'wenser.vercel.app',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,en-US;q=0.6',
        # 'cookie': '_ga=GA1.1.1252210018.1693466371; _ga_NJDL4PSH4L=GS1.1.1693722968.14.1.1693723041.0.0.0',
        'referer': 'https://wenser.vercel.app/check/zksync/0x8D26e499377556AEc66D993aD818C40949374e77',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': random_useragent(),
    }

    response = get(f'https://wenser.vercel.app/api/airdrops/zksync/mainnet?address={address}&type=full_wallet_data',
                   headers=headers).json()
    balance = Balance()
    balance.address = address
    for i, j in response.items():
        if i == 'spentFees':
            balance.fee = [j["result"], j["usdValue"]]
        elif i == 'ethBalance':
            balance.ETH = [j["balance"], j["usdValue"]]
        elif i == 'contractsActivity':
            balance.active_contract = j["uniqueContractAddressesCount"]
        elif i == 'tokenTxs':
            balance.last_date = j["lastTx"]["date"].split()[0]
        elif i == 'txVolume':
            balance.value = [j["ethValue"], j["usdValue"]]
        elif i == 'assignTxs':
            balance.tx = len(j)
    if not balance.value:
        time.sleep(1)
        return get_info_wallet(address)
    time.sleep(1)
    return balance


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
    address = [address_acc(adr[0]) for adr in wallet()]
    save_balance = [decorate.copy() for _ in range(len(address))]
    with Pool(10) as pols:
        all_balance = pols.map(lambda func: get_info_wallet(func), address)
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

