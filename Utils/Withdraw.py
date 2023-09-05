import time
from web3 import Web3

from Log.Loging import log
from Utils.EVMutils import EVM
from eth_account import Account
import config as cng


def withdrawal_token(private_key: str, to_address: str, retry=0) -> None:
    EVM.delay_start()
    wallet = Account.from_key(private_key).address
    for chain in cng.CHAIN_WITHDRAW:
        # try:
        web3 = EVM.web3(chain)
        limit = EVM.DecimalFrom(0.3 / EVM.prices_network('ethereum'), 18)
        value, _ = EVM.check_balance(private_key, chain, '')
        if value > limit:

            contract_txn = {
                'from': wallet,
                'chainId': web3.eth.chain_id,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(wallet),
                'gas': 0,
                'to': Web3.to_checksum_address(to_address),
                'value': 0
            }
            contract_txn = EVM.add_gas(web3, contract_txn)
            if not cng.BALANCE_WALLET:
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'] * 1.3)
            else:
                value_balance = EVM.DecimalFrom(EVM.randint_(cng.BALANCE_WALLET) /
                                                EVM.prices_network('ethereum'), 18)
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'] * 1.3) + value_balance

            values = int(value - gas_gas)
            contract_txn['value'] = values
            module = f'>>>>> Withdrawal of wallet tokens {wallet} <<<<<'
            EVM.sending_tx(web3, contract_txn, chain, private_key, retry, module, sell_add=values)

        # except ValueError as errors:
        #     if errors == 'The private kev must be exactly 32 bytes long. instead of 42 bvtes.':
        #         log().error('Private key error')
        #         if retry < cng.RETRY:
        #             time.sleep(15)
        #             return withdrawal_token(to_address, private_key, retry + 1)
        # except BaseException as error:
        #     log().error(f'An error occurred when withdrawing coins from the EVM address | {error}')
        #     if retry < cng.RETRY:
        #         time.sleep(15)
        #         return withdrawal_token(to_address, private_key, retry + 1)
