import time
import json

from Utils.EVMutils import EVM
from Bridge.Merkly import MerklyBridge
from random import choice
from Log.Loging import log, inv_log
from config import TX_MERKLY, VALUE_MERKLY, SLEEP_MERKLY


class MerklyTx:
    def __init__(self, private_key):
        self.private_key = private_key
        self.path_network = self.creating_path()
        self.address = EVM.web3("bsc").eth.account.from_key(self.private_key).address

    @staticmethod
    def to_chain_merkly() -> dict:
        with open('merkly_refuel.json', 'r') as file:
            return json.loads(file.read())

    def creating_path(self) -> list[list[str, str]] | bool:
        """Creating a chain of work"""
        list_work = []
        networks = self.coin_balance(self.private_key)
        if not networks:
            return False
        work_network = ['zksync']
        to_network = self.to_chain_merkly()
        amount_work = EVM.randint_(TX_MERKLY)
        for _ in range(amount_work):
            while True:
                if work_network:
                    from_chain = choice(work_network)
                    if to_network[from_chain]:
                        to_chain = to_network[from_chain].pop(EVM.randint_([0, len(to_network[from_chain])-1]))
                        list_work.append([from_chain, to_chain])
                        break
                    else:
                        work_network.remove(from_chain)
                else:
                    work_network = ['zksync']
                    to_network = self.to_chain_merkly()
                    time.sleep(1)
        return list_work

    @staticmethod
    def coin_balance(private_key: str) -> list:
        """Checking the balance 1$"""
        balance_chain, _ = EVM.check_balance(private_key, 'zksync', '')
        if balance_chain >= EVM.DecimalTO(1 / EVM.prices_network('zksync'), 18):
            return True

    @staticmethod
    def max_limit(amount, chain):
        """Checking the maximum bridge limit"""
        max_native = {
            "harmony": 0.07,
            "moonriver": 0.24,
            "celo": 0.02,
            "moonbeam": 1.4,
            "fuse": 0.0028,
            "klaytn": 0.01,
            "tenet": 0.01,
            "nova": 37,
            "kava": 0.85,
            "mantle": 0.11,
            "okx": 3.65,
            "coredao": 0.2,
            'base': 30,
            'meter': 0.04,
            'canto': 0.11
            }
        if max_native[chain] < amount:
            return max_native[chain]
        else:
            return amount

    def bridge_token(self):
        """Making breeches"""
        if self.path_network:
            EVM.delay_start()
            inv_log().info(f'{self.address, self.path_network}')
            for i, chain in enumerate(self.path_network):
                amount = round(self.max_limit(EVM.uniform_(VALUE_MERKLY), chain[1]) / EVM.prices_network(chain[0]), 6)
                bridge_ = MerklyBridge(self.private_key, chain[0], chain[1], amount)
                bridge_.bridge([i+1, len(self.path_network)])

                time.sleep(EVM.randint_(SLEEP_MERKLY))
        else:
            log().error(f"There is no negative on this wallet {self.address}")


if __name__ == '__main__':
    pass

