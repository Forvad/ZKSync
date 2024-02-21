import requests
import time

from eth_account import Account
from Utils.EVMutils import EVM
from config import RETRY
from Log.Loging import log

def signature(address):


    headers = {
        'authority': 'api.rhino.fi',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,en-US;q=0.6',
        'if-none-match': 'W/"86-qmHpM7Hzm4vh+aiXiTosnxd/Sec"',
        'origin': 'https://app.rhino.fi',
        'referer': 'https://app.rhino.fi/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    params = {
        'address': address.lower(),
    }

    r = requests.get('https://api.rhino.fi/activity-trackers/nftSignature/ZKSYNC', params=params,
                            headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        log().error(r.text)


def mint(private_key, retry=0):
    balance, decimal = EVM.check_balance(private_key, 'zksync', '')
    if (balance > EVM.DecimalFrom(0.00134, decimal) and
            '0x88D86B4B62A0F2A5D0e251b0f2Ac0dDdBEF981A5' != Account.from_key(private_key).address):
        web3 = EVM.web3('zksync')
        address_contract = web3.to_checksum_address('0xdD01108F870F087B54c28aCF1a8bBAf6f6A851Ae')
        abi = requests.get(f'https://block-explorer-api.mainnet.zksync.io/api?module=contract&action=getabi&address='
                           f'{address_contract}').json()['result']
        if not abi:
            log().error(f'NOT ABI -> {abi}')
            return

        contract = web3.eth.contract(address=address_contract, abi=abi)
        address = Account.from_key(private_key).address
        module_str = f'Mint rhino Nft | {address}'
        sing = signature(address)
        if sing:
            tx = contract.functions.mint(
                sing[1:-1]
            ).build_transaction(
                {
                    "from": address,
                    "nonce": web3.eth.get_transaction_count(address),
                    'gasPrice': web3.eth.gas_price,
                    'gas': 0,
                }
            )
            # tx = {
            #     'data': f'0x7ba0e2e7000000000000000000000000000000000000000000000000000000000000002000000000000000000000000'
            #             f'00000000000000000000000000000000000000041{sing[2:-1]}000000000000000000000000000000000000000000000'
            #             f'00000000000000000',
            #     'from': address,
            #     'to': address_contract,
            #     'chainId': web3.eth.chain_id,
            #     'gasPrice': web3.eth.gas_price,
            #     'nonce': web3.eth.get_transaction_count(address),
            #     'gas': 0
            # }
            tx_hash = EVM.sending_tx(web3, tx, 'zksync', private_key, retry, module_str)
            if not tx_hash:
                if retry < RETRY:
                    time.sleep(15)
                    return mint(private_key, retry + 1)
            time.sleep(EVM.randint_([20, 40]))
        else:
          log().error(f'NOT SIGN -> {sing}')
    else:
        log().info(f'Balance acc {Account.from_key(private_key).address} not 3$')
