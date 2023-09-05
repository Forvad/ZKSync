import time

from web3 import Web3
from eth_abi import encode
from Utils.EVMutils import EVM
import config as cng
from Contract.RPC import RPC
from Log.Loging import log


class WrapETH:
    @staticmethod
    def get_adapterParams(amount: int, mode: str):
        amount = EVM.DecimalFrom(amount, 18)
        name_func = {"withdraw": "0x2e1a7d4d", "deposit": "0xd0e30db0"}
        if mode == "withdraw":
            return 0, name_func[mode] + Web3.to_hex(encode(["uint256"], [amount]))[2:]
        else:
            return amount, name_func[mode]

    @staticmethod
    def wrapped_ETH(private_key, mode, amount, retry=0):
        w3 = EVM.web3("zksync")
        contract = w3.to_checksum_address("0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91")
        address = w3.eth.account.from_key(private_key).address
        nonce = w3.eth.get_transaction_count(address)
        amount_buy = amount
        amount, data = WrapETH.get_adapterParams(amount, mode)
        tx = {
            'from': address,
            'to': contract,
            'nonce': nonce,
            'value': amount,
            'data': data,
            'chainId': w3.eth.chain_id,
            'maxFeePerGas': int(w3.eth.gas_price * 1.1),
            'maxPriorityFeePerGas': w3.eth.gas_price
        }
        if mode == 'deposit':
            sell_add = amount
            buy_add = 0
        else:
            sell_add = 0
            buy_add = EVM.DecimalFrom(amount_buy, 18)
        tx_bool = EVM.sending_tx(w3, tx, "zksync", private_key, retry, "Wrapped ETH", sell_add=sell_add, add_buy=buy_add)
        if not tx_bool:
            time.sleep(15)
            if retry < cng.RETRY:
                return WrapETH.wrapped_ETH(private_key, mode, amount_buy, retry+1)
        else:
            return True

