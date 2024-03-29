import time

from web3 import Web3
from Contract.Swap_Contract import ContractSync
from Utils.EVMutils import EVM
from config import RETRY
from DEX.Izumi_Swap import Izumi


class SpaceFi:
    """ https://app.spacefi.io/ """
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
                          'BUSD': Web3.to_checksum_address('0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181')
                          }
        return tokens_address.get(name_token)

    def swap(self):
        web3, contract = ContractSync.spacefi()
        balance, decimal = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_from))
        wallet = web3.eth.account.from_key(self.private_key).address
        value = EVM.DecimalFrom(self.amount, decimal)
        amount_out = contract.functions.getAmountsOut(value, [self.token_address(self.token_from),
                                                              self.token_address(self.token_to)]).call()[1]
        min_tokens = int(amount_out * (1 - (3 / 100)))

        if self.token_from != "ETH":
            EVM.approve(value, self.private_key, "zksync", self.token_address(self.token_from),
                        "0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d")
            contract_txn = contract.functions.swapExactTokensForETH(
                value,
                min_tokens,
                [self.token_address(self.token_from), self.token_address(self.token_to)],
                wallet,
                (int(time.time()) + 10000),  # deadline
            )
        else:
            contract_txn = contract.functions.swapETHForExactTokens(
                min_tokens,
                [self.token_address(self.token_from), self.token_address(self.token_to)],
                wallet,
                (int(time.time()) + 10000),  # deadline
            )
        contract_txn = contract_txn.build_transaction({
            'chainId': web3.eth.chain_id,
            'from': wallet,
            'value': value if self.token_from == "ETH" else 0,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
            "gas": 0
        })
        module_str = f'SpaceFi Swap | {wallet} | {self.token_from} | {self.token_to}'
        add_buy = EVM.DecimalFrom(self.amount / EVM.prices_network("ethereum"), 18) if self.token_to == 'ETH' else 0
        sell_add = value if self.token_from == 'ETH' else 0
        tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', self.private_key, self.retry, module_str,
                                 add_buy=add_buy, sell_add=sell_add)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.swap()
            else:
                swaps = Izumi(self.private_key, self.token_from, self.token_to, self.amount)
                swaps.swap()
        else:
            return True
