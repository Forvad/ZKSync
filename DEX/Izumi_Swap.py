import time

from web3 import Web3
from Contract.Swap_Contract import ContractSync
from Utils.EVMutils import EVM
from config import RETRY
from eth_abi import *


class Izumi:
    """ https://izumi.finance/trade/swap """
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
                          'USDT': Web3.to_checksum_address('0x496d88D1EFc3E145b7c12d53B78Ce5E7eda7a42c'),
                          }
        return tokens_address.get(name_token)

    def swap(self):
        web3, contract = ContractSync.zizumi()
        balance, decimal = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_from))
        wallet = web3.eth.account.from_key(self.private_key).address
        value = EVM.DecimalFrom(self.amount, decimal)
        decimal, _ = EVM.decimal_token("zksync", self.token_address(self.token_to))
        if self.token_from == "ETH":
            min_value = EVM.DecimalFrom(self.amount * EVM.prices_network("zksync") * 0.9, decimal)
            mode = "0007d0"
        elif self.token_to == "ETH":
            min_value = EVM.DecimalFrom(self.amount / EVM.prices_network("zksync") * 0.9, decimal)
            mode = "000190"
        else:
            min_value = EVM.DecimalFrom(self.amount * 0.9, decimal)
            mode = "000190"
        data = '0x75ceafe600000000000000000000000000000000000000000000000000000000000000200000000000000000000000000' \
               '0000000000000000000000000000000000000a0' + encode(['address', 'uint128', 'uint256', 'uint256'],
                                                                  [wallet,
                 value,
                 min_value,
                 int(time.time()) + 10000]).hex() + f"000000000000000000000000000000000000000000000000000000000000002b" \
                                                     f"{self.token_address(self.token_from)[2:].lower()}{mode}" \
                                                     f"{self.token_address(self.token_to)[2:].lower()}" \
                                                     f"000000000000000000000000000000000000000000"
        data2 = "0x12210e8a" if self.token_to != "ETH" else "0x49404b7c" +\
                                                              encode(["uint256", "address"], [0, wallet]).hex()

        if self.token_from != "ETH":
            EVM.approve(value, self.private_key, "zksync", self.token_address(self.token_from),
                        "0x943ac2310D9BC703d6AB5e5e76876e212100f894")
        if self.token_from != "ETH" and self.token_to != "ETH":
            contract_txn = contract.functions.swapAmount(
                (f"{self.token_address(self.token_from)}000190{self.token_address(self.token_to)[2:]}",
                wallet,
                value,
                min_value,
                int(time.time()) + 10000)
            ).build_transaction({
                'from': wallet,
                'value': value if self.token_from == "ETH" else 0,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(wallet),
                "gas": 0
            })
        else:
            contract_txn = contract.functions.multicall(
                [data, data2]
            ).build_transaction({
                'from': wallet,
                'value': value if self.token_from == "ETH" else 0,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(wallet),
                "gas": 0
            })
        module_str = f'Izumi Swap | {wallet} | {self.token_from} | {self.token_to}'
        add_buy = EVM.DecimalFrom(self.amount / EVM.prices_network("ethereum"), 18) if self.token_to == 'ETH' else 0
        sell_add = value if self.token_from == 'ETH' else 0
        tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', self.private_key, self.retry, module_str,
                                 add_buy=add_buy, sell_add=sell_add)
        if not tx_bool:
            if RETRY < self.retry:
                self.retry += 1
                time.sleep(15)
                return self.swap()
