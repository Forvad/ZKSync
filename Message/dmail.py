import time

from eth_account import Account

from Utils.EVMutils import EVM
from Abi.abi import open_abi
from config import RETRY


def message_dmail(private_key, retry=0):
    web3 = EVM.web3('zksync')
    address = Account.from_key(private_key).address
    contract = web3.eth.contract(address='0x981F198286E40F9979274E0876636E9144B8FB8E', abi=open_abi()['abi_Dmail'])
    tx = contract.functions.send_mail('0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5@dmail.ai',
                                      '0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5@dmail.ai').\
        build_transaction({
                            'from': address,
                            'gasPrice': web3.eth.gas_price,
                            'nonce': web3.eth.get_transaction_count(address),
                            "gas": 0
            })
    str_modules = f'Dmail message | {address}'
    tx_bool = EVM.sending_tx(web3, tx, 'zksync',  private_key, retry, str_modules)
    if not tx_bool:
        if RETRY > retry:
            time.sleep(15)
            return message(private_key, retry+1)
    else:
        return True


if __name__ == '__main__':
    pass


