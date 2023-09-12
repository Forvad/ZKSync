import time

from eth_account import Account

from Utils.EVMutils import EVM
from config import BALANCE_WALLET, RETRY
from Contract.Bridge_Contract import OpenContract
from requests import get


# https://across.to/api/suggested-fees?token=0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91&destinationChainId=42161&
# originChainId=324&amount=200000000000000000&skipAmountLimit=true

def transfer_across(private_key: str, retry=0):
    web3, contract = OpenContract.acrossbridge()
    address = Account.from_key(private_key).address
    balance, _ = EVM.check_balance(private_key, 'zksync', '')
    if BALANCE_WALLET:
        value = balance - EVM.DecimalFrom(EVM.uniform_(BALANCE_WALLET) / EVM.prices_network('zksync') + 0.0006, 18)
    else:
        value = balance - EVM.DecimalFrom(0.001, 18)
    WETH = "0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91"
    chain_id = 42161
    relayFeePct = relayerFeePct(value)
    quoteTimestamp = (int(time.time()) + 1000)
    message = '0x'
    maxCount = 115792089237316195423570985008687907853269984665640564039457584007913129639935
    contract_txn = contract.functions.deposit(address, WETH, value, chain_id, relayFeePct, quoteTimestamp, message,
                                              maxCount)\
        .build_transaction({
                            'chainId': web3.eth.chain_id,
                            'nonce': web3.eth.get_transaction_count(address),
                            "from": address,
                            'value': value,
                            'gas': 0,
                            'gasPrice': web3.eth.gas_price
                        })
    module_str = f'Across bridge | {address}'
    tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', private_key, retry, module_str)
    if not tx_bool:
        if RETRY > retry:
            time.sleep(15)
            return transfer_across(private_key, retry+1)
    else:
        EVM.waiting_coin(private_key, 'arbitrum', '', EVM.DecimalTO(value, 18))
        return True


def relayerFeePct(value: int):
    r = get(f'https://across.to/api/suggested-fees?token=0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91&'
            f'destinationChainId=42161&originChainId=324&amount={value}&skipAmountLimit=true').json()
    return int(r['relayFeePct'])

if __name__ == '__main__':
    print(relayerFeePct(int(0.01e18)))