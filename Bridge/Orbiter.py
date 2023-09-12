import time

from eth_account import Account

from Utils.EVMutils import EVM
from config import BALANCE_WALLET, RETRY


def transfer_orbiter(private_key: str, retry=0):
    web3 = EVM.web3('zksync')
    address = Account.from_key(private_key).address
    balance, _ = EVM.check_balance(private_key, 'zksync', '')
    if BALANCE_WALLET:
        value = balance - EVM.DecimalFrom(EVM.uniform_(BALANCE_WALLET) / EVM.prices_network('zksync') + 0.0013, 18)
    else:
        value = balance - EVM.DecimalFrom(0.002, 18)
    value = reconstruction_value(value)
    contract_txn = {
        'chainId': web3.eth.chain_id,
        'nonce': web3.eth.get_transaction_count(address),
        "from": address,
        'to': '0x80C67432656d59144cEFf962E8fAF8926599bCF8',
        'value': value,
        'gas': 0,
        'gasPrice': web3.eth.gas_price
    }
    module_str = f'Obiter bridge | {address}'
    tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', private_key, retry, module_str)
    if not tx_bool:
        if RETRY > retry:
            time.sleep(15)
            return transfer_orbiter(private_key, retry+1)
    else:
        EVM.waiting_coin(private_key, 'arbitrum', '', EVM.DecimalTO(value, 18))
        return True


def reconstruction_value(base_value: int) -> int:
    return int(str(base_value)[:-4] + '9002')

