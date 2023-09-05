import time

from Utils.EVMutils import EVM
from Contract.Bridge_Contract import OpenContract


class ZkBridge:
    def __init__(self, private_key: str, from_chain: str, amount: (int, float), gas=False):
        self.private_key = private_key
        self.from_chain = from_chain
        self.amount = amount if not gas else amount - self.get_gas()
        self.retry = 0

    def bridge(self):
        web3, contract = OpenContract.ZkBridge(self.from_chain)
        wallet = web3.eth.account.from_key(self.private_key).address
        module_str = f'ZKBridge | {wallet} | {self.from_chain}'
        l2_value = EVM.DecimalFrom(self.amount, 18)
        tx = contract.functions.requestL2Transaction(
            wallet,
            l2_value,
            "0x",
            762908,
            800,
            [],
            wallet
        ).build_transaction({
            "value": l2_value + EVM.DecimalFrom(0.7 / EVM.prices_network("ethereum"), 18),
            'from': wallet,
            'gas': 0,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
        })
        add_sell = l2_value
        tx_bool = EVM.sending_tx(web3, tx, self.from_chain, self.private_key, self.retry, module_str, sell_add=add_sell)
        if not tx_bool:
            self.retry += 1
            time.sleep(15)
            return self.bridge()
        else:
            return EVM.DecimalTO(l2_value, 18)

    def get_gas(self):
        web3, contract = OpenContract.ZkBridge(self.from_chain)
        wallet = web3.eth.account.from_key(self.private_key).address
        l2_value = EVM.DecimalFrom(0.0011, 18)
        tx = contract.functions.requestL2Transaction(
            wallet,
            l2_value,
            "0x",
            732390,
            800,
            [],
            wallet
        ).build_transaction({
            'chainId': web3.eth.chain_id,
            "value": l2_value + EVM.DecimalFrom(0.7 / EVM.prices_network("ethereum"), 18),
            'from': wallet,
            'gas': 0,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
        })
        gas = web3.eth.estimate_gas(tx) * tx["gasPrice"] * 1.5 + EVM.DecimalFrom(0.7 / EVM.prices_network("ethereum"), 18)
        return EVM.DecimalTO(gas, 18)
