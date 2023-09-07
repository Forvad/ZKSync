import time

from web3 import Web3
from eth_abi import encode
from Contract.Swap_Contract import ContractSync
from Utils.EVMutils import EVM
from config import RETRY


class SyncSwap:
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
        balance_from, decimal_from = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_from))
        balance_to, decimal_to = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_to))
        self.amount = EVM.DecimalFrom(self.amount, decimal_from)
        zero_address = '0x0000000000000000000000000000000000000000'
        web3, contract_get_pool = ContractSync.geet_pool()
        wallet = web3.eth.account.from_key(self.private_key).address
        module_str = f'SyncSwap | {wallet} | {self.token_from} | {self.token_to}'
        pool_address = contract_get_pool.functions.getPool(self.token_address(self.token_from),
                                                           self.token_address(self.token_to)).call()
        _, sync_pool = ContractSync.sync_pool(pool_address)
        reserves_token, reserves_eth = sync_pool.functions.getReserves().call()
        data = encode(['address', 'address', 'uint8'], [self.token_address(self.token_from), wallet, 1])
        steps = [
            {
                'pool': pool_address,
                'data': data,
                'callback': zero_address,
                'callbackData': '0x'
            }
        ]
        reserves_token = EVM.DecimalTO(reserves_token, decimal_to)
        reserves_eth = EVM.DecimalTO(reserves_eth, 18)
        if self.token_from == "ETH":
            price_one_token = reserves_eth / reserves_token
            amountOutMin = EVM.DecimalFrom(EVM.DecimalTO(self.amount, 18) / price_one_token * 0.97, decimal_to)
        else:
            price_one_token = reserves_token / reserves_eth
            amountOutMin = EVM.DecimalFrom(EVM.DecimalTO(self.amount, decimal_to) / price_one_token * 0.97, 18)
        paths = [
            {
                'steps': steps,
                'tokenIn': zero_address if self.token_from == "ETH" else self.token_address(self.token_from),
                'amountIn': self.amount
            }
        ]
        _, contract = ContractSync.sync_router()
        if self.token_from != "ETH":
            EVM.approve(self.amount, self.private_key, "zksync", self.token_address(self.token_from),
                        "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295")
        tx = contract.functions.swap(
            paths,
            amountOutMin,
            (int(time.time()) + 10000)
        ).build_transaction({'from': wallet,
                             'gasPrice': web3.eth.gas_price,
                             'nonce': web3.eth.get_transaction_count(wallet),
                             "gas": 0,
                             "value": self.amount if self.token_from == "ETH" else 0
                             })
        if self.token_from == 'ETH':
            amount = self.amount
        else:
            amount = EVM.DecimalFrom(EVM.DecimalTO(self.amount, decimal_to) / price_one_token, 18)
        add_buy = amount if self.token_to == 'ETH' else 0
        sell_add = amount if self.token_from == 'ETH' else 0
        tx_bool = EVM.sending_tx(web3, tx, 'zksync', self.private_key, self.retry, module_str, add_buy=add_buy,
                                 sell_add=sell_add)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.swap()

    def add_liquidity(self):
        module_str = 'Add Liquidity Sync'
        balance_from, decimal_from = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_from))
        balance_to, decimal_to = EVM.check_balance(self.private_key, "zksync", self.token_address(self.token_to))
        web3, contract_get_pool = ContractSync.geet_pool()
        wallet = web3.eth.account.from_key(self.private_key).addressz
        pool_address = contract_get_pool.functions.getPool(self.token_address(self.token_from),
                                                           self.token_address(self.token_to)).call()
        _, sync_pool = ContractSync.sync_pool(pool_address)
        reserves = sync_pool.functions.getReserves().call()
        native_eth_address = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")
        data = encode(
            ["address"],
            [wallet]
        )
        reserves_from, reserves_to = reserves
        reserves_from = EVM.DecimalTO(reserves_from, decimal_from)
        reserves_to = EVM.DecimalTO(reserves_to, decimal_to)
        price_one_token = reserves_to / reserves_from
        value_eth = price_one_token * self.amount
        value_eth = EVM.DecimalFrom(value_eth, 18)
        min_liquidity = EVM.DecimalFrom(self.amount * 0.95, decimal_from)
        value = EVM.DecimalFrom(self.amount, decimal_from)
        EVM.approve(self.amount, self.private_key, "zksync", self.token_address(self.token_from),
                    "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295")
        _, contract = ContractSync.sync_router()
        contract_txn = contract.functions.addLiquidity2(
            pool_address,
            [(self.token_address(self.token_from), value), (native_eth_address, value_eth)],
            data,
            min_liquidity,
            native_eth_address,
            '0x'
        ).build_transaction(
            {
                'from': wallet,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': value_eth,
                'gas': 0
            }
        )
        sell_add = value_eth
        tx_bool = EVM.sending_tx(web3, contract_txn, 'zksync', self.private_key, self.retry, module_str,
                                 sell_add=sell_add)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.add_liquidity()
