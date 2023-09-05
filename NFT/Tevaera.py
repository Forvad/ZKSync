import time

from eth_account import Account
from Utils.EVMutils import EVM
from config import RETRY


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
