import time

import requests
from Utils.EVMutils import EVM, Web3
from config import RETRY
from Log.Loging import inv_log


class Openocean:
    def __init__(self, private_key, token_from, token_to, amount):
        self.private_key = private_key
        self.token_from = token_from
        self.token_to = token_to
        self.amount = amount
        self.retry = 0

    @staticmethod
    def token_address(name_token):
        tokens_address = {'USDC': Web3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),
                          'ETH': Web3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'),
                          'USDT': Web3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'),
                          }
        return tokens_address.get(name_token)

    def swap(self):
        web3 = EVM.web3('zksync')
        wallet = web3.eth.account.from_key(self.private_key).address
        from_token_address = self.token_address(self.token_from)
        token_to_buy = self.token_address(self.token_to)

        def req():
            url = f'https://open-api.openocean.finance/v3/324/swap_quote?inTokenAddress={from_token_address.lower()}&' \
                  f'outTokenAddress={token_to_buy.lower()}&account={wallet.lower()}' \
                  f'&amount={self.amount}&gasPrice=5&slippage=3'
            response = requests.get(url=url)
            json_data = response.json()
            value = int(json_data['data']['value'])
            return value, json_data
        while True:
            try:
                value, json_data = req()
                break
            except BaseException:
                inv_log().error(f'openocean error request')
        if self.token_from != "ETH":
            decimal, _ = EVM.decimal_token('zksync', from_token_address)
            EVM.approve(EVM.DecimalFrom(self.amount, decimal),
                        self.private_key, "zksync", Web3.to_checksum_address(from_token_address),
                        json_data['data']['to'])
        txn = {
            'chainId': 324,
            'data': json_data['data']['data'],
            'from': wallet,
            'to': Web3.to_checksum_address(json_data['data']['to']),
            'value': value,
            'nonce': web3.eth.get_transaction_count(wallet),
            'gasPrice': web3.eth.gas_price,
            'gas': 0
        }
        add_buy = EVM.DecimalFrom(self.amount / EVM.prices_network('zksync'), 18) if self.token_to == 'ETH' else 0
        sell_add = EVM.DecimalFrom(self.amount, 18) if self.token_from == 'ETH' else 0
        module_str = f'Openocean Swap | {wallet} | {self.token_from} | {self.token_to}'
        tx_bool = EVM.sending_tx(web3, txn, 'zksync', self.private_key, self.retry, module_str, add_buy=add_buy,
                                 sell_add=sell_add)
        if not tx_bool:
            if RETRY > self.retry:
                self.retry += 1
                time.sleep(15)
                return self.swap()


if __name__ == '__main__':
    pass