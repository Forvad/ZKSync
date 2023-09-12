import time

import requests
from web3 import Web3
from eth_account import Account
from Utils.EVMutils import EVM
from Log.Loging import log, inv_log
from config import RETRY
from DEX.MuteSwap import Mute


class Odos:
    """ https://app.odos.xyz/"""

    def __init__(self, private_key: str, token_from: str, token_to: str, amount: (int, float)):
        self.private_key = private_key
        self.token_from = token_from
        self.token_to = token_to
        self.amount = amount
        self.retry = 0

    @staticmethod
    def token_address(name_token):
        tokens_address = {'USDC': Web3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),
                          'ETH': Web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                          'USDT': Web3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'),
                          'BUSD': Web3.to_checksum_address('0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181')
                          }
        return tokens_address.get(name_token)

    def create_quote(self):
        address = Account.from_key(self.private_key).address
        quote_url = "https://api.odos.xyz/sor/quote/v2"
        if self.token_from != "ETH":
            decimal, _ = EVM.decimal_token("zksync", self.token_address(self.token_from))
        else:
            decimal = 18

        quote_request_body = {
            "chainId": 324,  # Replace with desired chainId
            "inputTokens": [
                {
                    "tokenAddress": Web3.to_checksum_address(self.token_address(self.token_from)),
                    # checksummed input token address
                    "amount": str(EVM.DecimalFrom(self.amount, decimal)),  # input amount as a string in fixed integer
                }
            ],
            "outputTokens": [
                {
                    "tokenAddress": Web3.to_checksum_address(self.token_address(self.token_to)),
                    # checksummed output token address
                    "proportion": 1
                }
            ],
            "slippageLimitPercent": 3,  # set your slippage limit percentage (1 = 1%)
            "userAddr": address,  # checksummed user address
            "referralCode": 0,  # referral code (recommended)
            "compact": True,
        }

        response = requests.post(
            quote_url,
            headers={"Content-Type": "application/json"},
            json=quote_request_body
        )

        quote = response.json()
        return quote

    def swap(self):
        quote = self.create_quote()
        if quote.get('pathId'):
            assemble_url = "https://api.odos.xyz/sor/assemble"
            address = Account.from_key(self.private_key).address

            assemble_request_body = {
                "userAddr": address,  # the checksummed address used to generate the quote
                "pathId": quote["pathId"],  # Replace with the pathId from quote response in step 1
                "simulate": False,
                # this can be set to true if the user isn't doing their own estimate gas call for the transaction
            }

            response = requests.post(
                assemble_url,
                headers={"Content-Type": "application/json"},
                json=assemble_request_body
            )

            if response.status_code == 200:
                assembled_transaction = response.json()
                web3 = EVM.web3('zksync')
                tx = assembled_transaction["transaction"]
                tx["chainId"] = 324
                tx["value"] = int(tx["value"])
                if self.token_from != "ETH":
                    EVM.approve(1e18,
                                self.private_key, "zksync",
                                Web3.to_checksum_address(self.token_address(self.token_from)),
                                tx["to"])
                tx['nonce'] = web3.eth.get_transaction_count(address)
                add_buy = EVM.DecimalFrom(self.amount / EVM.prices_network("zksync"), 18) if self.token_to == "ETH"\
                    else 0
                add_sell = tx["value"] if self.token_from == "ETH" else 0
                tx['gas'] = 0
                str_modules = f'Odos Swap | {address} | {self.token_from} | {self.token_to}'
                inv_log().info(f'odos tx: {tx}')
                tx_bool = EVM.sending_tx(web3, tx, 'zksync', self.private_key, 0, str_modules, add_buy=add_buy, sell_add=add_sell)
                if not tx_bool:
                    if RETRY > self.retry:
                        self.retry += 1
                        time.sleep(15)
                        return self.swap()
                    else:
                        swaps = Mute(self.private_key, self.token_from, self.token_to, self.amount)
                        swaps.swap()
                # handle transaction assembly response data
            else:
                log().error(f"Error in Transaction Assembly: {response.json()}")
                # handle transaction assembly failure cases
        else:
            log().error(quote.get('detail'))


if __name__ == '__main__':
    pass