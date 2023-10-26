import time
import requests
import random

from eth_account import Account
from Utils.EVMutils import EVM
from config import RETRY
from pyuseragents import random as random_useragent
from Contract.Bridge_Contract import OpenContract


class Tevaera:
    @staticmethod
    def mint_pass(private_key, retry=0):
        address = Account.from_key(private_key).address
        web3 = EVM.web3('zksync')
        module_str = f'Mint TEVAN PASS | {address}'

        tx = {
            'data': '0xfefe409d',
            'from': address,
            'to': '0xd29Aa7bdD3cbb32557973daD995A3219D307721f',
            'chainId': web3.eth.chain_id,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(address),
            'gas': 0,
            'value': EVM.DecimalFrom(0.0003, 18)
        }
        tx_hash = EVM.sending_tx(web3, tx, 'zksync', private_key, retry, module_str)
        if not tx_hash:
            if retry < RETRY:
                time.sleep(15)
                return Tevaera.mint_pass(private_key, retry+1)
        time.sleep(EVM.randint_([20, 40]))

    @staticmethod
    def mint_hero(private_key, retry=0):
        address = Account.from_key(private_key).address
        web3 = EVM.web3('zksync')
        module_str = f'Mint TEVAN HERO | {address}'

        tx = {
            'data': '0x1249c58b',
            'from': address,
            'to': '0x50B2b7092bCC15fbB8ac74fE9796Cf24602897Ad',
            'chainId': web3.eth.chain_id,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(address),
            'gas': 0,
        }
        tx_hash = EVM.sending_tx(web3, tx, 'zksync', private_key, retry, module_str)
        if not tx_hash:
            if retry < RETRY:
                time.sleep(15)
                return Tevaera.mint_pass(private_key, retry+1)
        time.sleep(EVM.randint_([20, 40]))

    @staticmethod
    def mint_unicorn(private_key, retry=0):
        address = Account.from_key(private_key).address
        web3 = EVM.web3('zksync')
        module_str = f'Mint Innovative Unicorn | {address}'

        tx = {
            'data': '0x410404b7',
            'from': address,
            'to': '0x5dE117628B5062F56f37d8fB6603524C7189D892',
            'chainId': web3.eth.chain_id,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(address),
            'value': EVM.DecimalFrom(0.0009, 18),
            'gas': 0,
        }
        tx_hash = EVM.sending_tx(web3, tx, 'zksync', private_key, retry, module_str)
        if not tx_hash:
            if retry < RETRY:
                time.sleep(15)
                return Tevaera.mint_pass(private_key, retry + 1)
        time.sleep(EVM.randint_([20, 40]))

    @staticmethod
    def bridge_unicorn(private_key, retry=0):
        address = Account.from_key(private_key).address
        get_id = Tevaera.get_id_nft(address)
        if not get_id:
            Tevaera.mint_unicorn(private_key)
            time.sleep(20)
            get_id = Tevaera.get_id_nft(address)
        while not get_id:
            time.sleep(20)
            get_id = Tevaera.get_id_nft(address)
        web3, contract = OpenContract.tevaera()
        module_str = f'Bridge Innovative Unicorn | {address}'
        _from = address
        _dstChainId = random.choice([110, 183])
        _toAddress = address
        _tokenId = get_id
        _refundAddress = '0x76426D2381baDf0f5Ee50E82aF9092fb1d1A81db'
        _zroPaymentAddress = '0x0000000000000000000000000000000000000000'
        _adapterParams = '0x00010000000000000000000000000000000000000000000000000000000000055730'
        fee = contract.functions.estimateSendFee(_dstChainId, _toAddress, _tokenId, True, _adapterParams).call()[0]
        tx = contract.functions.sendFrom(_from, _dstChainId, _toAddress, _tokenId, _refundAddress, _zroPaymentAddress,
                                         _adapterParams).build_transaction({
                            'chainId': web3.eth.chain_id,
                            'nonce': web3.eth.get_transaction_count(address),
                            "from": address,
                            'value': fee,
                            'gas': 0,
                            'gasPrice': web3.eth.gas_price
                        })
        tx_bool = EVM.sending_tx(web3, tx, 'zksync', private_key, retry, module_str)
        if not tx_bool:
            if RETRY > retry:
                time.sleep(15)
                return Tevaera.bridge_unicorn(private_key, retry + 1)
        else:
            return True


    @staticmethod
    def get_id_nft(address):
        headers = {
            'authority': 'api.tevaera.com',
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,en-US;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://market.tevaera.com',
            'referer': 'https://market.tevaera.com/',
            'referrer-policy': 'strict-origin-when-cross-origin',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'strict-transport-security': 'Strict-Transport-Security',
            'user-agent': random_useragent(),
            'x-content-type-options': 'nosniff',
            'x-daoiq-apim': 'dhn23uytf7v3ybtf79yj93rtj3d78654vhy',
            'x-frame-options': 'SAMEORIGIN',
            'x-xss-protection': '1; mode=block',
        }

        json_data = {
            'operationName': 'onfts',
            'variables': {
                'owner': address,
            },
            'query': 'query onfts($network: Network, $tokenId: String, $owner: String!, $contract: String)'
                     ' {\n  onfts(network: $network, tokenId: $tokenId, contract: $contract, owner: $owner) '
                     '{\n    contract {\n      address\n      arbitrumAddress\n      lineaAddress\n      bannerImage\n '
                     '     description\n      externalLink\n      floorPrice\n      image\n      isApproved\n   '
                     '   name\n      owner\n      standard\n      tokenBaseUri\n      totalOwners\n      totalSupply\n '
                     '     totalVolume\n      __typename\n    }\n    owner\n    tokenId\n    uri\n    network\n   '
                     ' __typename\n  }\n}',
        }

        response = requests.post('https://api.tevaera.com/', headers=headers, json=json_data)
        if response.status_code == 200:
            for nft in response.json()['data']['onfts']:
                if nft['network'] == 'ZKSYNC_ERA':
                    return int(nft['tokenId'])
            return 0
        else:
            return 0

if __name__ == '__main__':
    print(Tevaera.get_id_nft('0x8D26e499377556AEc66D993aD818C40949374e77'))
