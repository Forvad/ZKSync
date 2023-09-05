import time

from eth_abi import *
from eth_account import Account

from Utils.EVMutils import EVM
from config import RETRY


class ProtocolRector:
    """ https://app.reactorfusion.xyz/ """
    def __init__(self, private_key, token,  amount):
        self.private_key = private_key
        self.token = token
        self.amount = EVM.DecimalFrom(amount, 18 if token == 'ETH' else 6)
        self.address = Account.from_key(private_key).address
        self.retry = 0
        self.web3 = EVM.web3('zksync')

    def supply_assets(self):

        address_contract = {'ETH': '0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6',
                            'USDC': '0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29'}
        data = '0xc2998238' + encode(['address[]'], [[address_contract[self.token]]]).hex()
        tx = {
            'chainId': self.web3.eth.chain_id,
            'from': self.address,
            'data': data,
            'to': '0x23848c28Af1C3AA7B999fA57e6b6E8599C17F3f2',
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.address),
            "gas": 0
        }
        module_str = f'Supply Assets | {self.address}'
        tx_bool = EVM.sending_tx(self.web3, tx, 'zksync', self.private_key, self.retry, module_str)
        if not tx_bool:
            if RETRY < self.retry:
                self.retry += 1
                time.sleep(15)
                return self.supply_assets()
        else:
            return True

    def deposit(self):
        address_contract = {'ETH': '0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6',
                            'USDC': '0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29'}

        data = {'ETH': '0x1249c58b', 'USDC': '0xa0712d68' + encode(['uint256'], [self.amount]).hex()}
        tx = {
            'chainId': self.web3.eth.chain_id,
            'from': self.address,
            'value': self.amount if self.token == 'ETH' else 0,
            'data': data[self.token],
            'to': address_contract[self.token],
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.address),
            "gas": 0
        }
        module_str = f'Deposit | {self.token} | {self.address}'
        tx_bool = EVM.sending_tx(self.web3, tx, 'zksync', self.private_key, self.retry, module_str, sell_add=self.amount)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.deposit()
        else:
            return True

    def withdraw(self):
        address_contract = {'ETH': '0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6',
                            'USDC': '0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29'}

        balance_rfETH, balance_rfUSDC = self.check_rf()

        data = '0xdb006a75' + encode(['uint256'], [balance_rfETH if self.token == 'ETH' else balance_rfUSDC]).hex()
        tx = {
            'chainId': self.web3.eth.chain_id,
            'from': self.address,
            'data': data,
            'to': address_contract[self.token],
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.address),
            "gas": 0
        }
        add_buy = self.amount if self.token == 'ETH' else 0
        module_str = f'Withdraw | {self.token} | {self.address}'
        tx_bool = EVM.sending_tx(self.web3, tx, 'zksync', self.private_key, self.retry, module_str, add_buy=add_buy)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.withdraw()
        else:
            return True

    def check_rf(self):
        balance_rfETH, _ = EVM.check_balance(self.private_key, 'zksync', '0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6')
        balance_rfUSDC, _ = EVM.check_balance(self.private_key, 'zksync', '0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29')
        return balance_rfETH, balance_rfUSDC

    def work_lending(self):
        self.supply_assets()
        time.sleep(EVM.randint_([15, 30]))
        self.deposit()
        time.sleep(EVM.randint_([30, 60]))
        self.withdraw()


if __name__ == '__main__':
    pass
