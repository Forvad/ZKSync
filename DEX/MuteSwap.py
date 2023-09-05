import time

from web3 import Web3
from Contract.Swap_Contract import ContractSync
from Utils.EVMutils import EVM
from config import RETRY


class Mute:
    """ https://app.mute.io/swap """
    def __init__(self, private_key, token_from, token_to, amount):
        self.private_key = private_key
        self.token_from = token_from
        self.token_to = token_to
        self.amount = amount
        self.retry = 0

    @staticmethod
    def token_address(name_token):
        tokens_address = {'USDC': Web3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),
                          'ETH': Web3.to_checksum_address('0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'),
                          'USDT': Web3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'),
                          }
        return tokens_address.get(name_token)

    def swap(self):
        web3, contract = ContractSync.mute()
        balance, decimal = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_from))
        wallet = web3.eth.account.from_key(self.private_key).address
        value = EVM.DecimalFrom(self.amount, decimal)
        amount_out = contract.functions.getAmountsOut(value, [self.token_address(self.token_from),
                                                              self.token_address(self.token_to)],
                                                      [False, True]).call()[1]
        min_tokens = int(amount_out * (1 - (1 / 100)))
        if self.token_from != "ETH":
            contract_txn = contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                value,
                min_tokens,
                [self.token_address(self.token_from), self.token_address(self.token_to)],
                wallet,
                (int(time.time()) + 10000),  # deadline
                [False, False]
            )
        else:
            contract_txn = contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                min_tokens,
                [self.token_address(self.token_from), self.token_address(self.token_to)],
                wallet,
                (int(time.time()) + 10000),  # deadline
                [False, True]
            )
        contract_txn = contract_txn.build_transaction({
            'from': wallet,
            'value': value if self.token_from == "ETH" else 0,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
            "gas": 0
        })
        if self.token_from != "ETH":
            EVM.approve(value, self.private_key, "zksync", self.token_address(self.token_from),
                        "0x8B791913eB07C32779a16750e3868aA8495F5964")
        module_str = f'Mute Swap | {wallet} | {self.token_from} | {self.token_to}'
        add_buy = value if self.token_to == 'ETH' else 0
        sell_add = value if self.token_from == 'ETH' else 0
        tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', self.private_key, self.retry, module_str,
                                 add_buy=add_buy, sell_add=sell_add)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.swap()
        else:
            return True

    def add_liquidity(self):
        module_str = 'Add Liquidity Mute'
        web3, contract = ContractSync.mute()
        wallet = web3.eth.account.from_key(self.private_key).address
        _, decimal = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_from))
        value = EVM.DecimalFrom(self.amount, decimal)
        amount_out = contract.functions.getAmountsOut(value, [self.token_address(self.token_from),
                                                              self.token_address(self.token_to)],
                                                      [True, False]).call()[1]
        EVM.approve(value, self.private_key, "zksync", self.token_address(self.token_from),
                    "0x8B791913eB07C32779a16750e3868aA8495F5964")
        contract_txn = contract.functions.addLiquidityETH(
            self.token_address(self.token_from),
            value,
            int(value * 0.95),
            int(amount_out * 0.95),
            wallet,
            (int(time.time()) + 10000),  # deadline
            50,
            False
        ).build_transaction({
            'from': wallet,
            'value': amount_out,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
            'gas': 0
        })
        tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', self.private_key, self.retry, module_str,)

        if not tx_bool:
            if RETRY < self.retry:
                self.retry += 1
                time.sleep(15)
                return self.add_liquidity()
