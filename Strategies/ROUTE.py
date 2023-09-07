import random
import time

from Utils.EVMutils import EVM
from Exchange.OKX import okx_withdraw
from Exchange.BitGet import BitGetTr
import config as cng
from eth_account import Account
from Contract.Deploy_Contract import deploy
from DEX.Wrap_ETH import WrapETH
from Bridge.ZKBridge import ZkBridge
from Name_Service.Domains_Name import mint_name
from Strategies.Merkly_tx import MerklyTx
from Utils.Withdraw import withdrawal_token
from Lending_Protocol.RectorFusion import ProtocolRector
from DEX.Izumi_Swap import Izumi
from DEX.Zkswap import ZkSwap
from DEX.Odos_Swap import Odos
from DEX.SyncSwap import SyncSwap
from DEX.Openocean_Swap import Openocean
from DEX.MuteSwap import Mute
from DEX.SpaceFi_Swap import SpaceFi
from NFT.Tevaera import Tevaera
from Log.Loging import log, inv_log
from Message.dmail import message_dmail


class FuncZksync:
    def __init__(self, private_key: str):
        self.private_key = private_key
        self.route = []
        self.address = Account.from_key(private_key).address

    def defence_balance(self, value: (float, int), chain: str):
        balance_eth, decimal = EVM.check_balance(self.private_key, chain, '')
        if EVM.DecimalTO(balance_eth, decimal) < value:
            raise ValueError(f'The deposit is less than you need to --- {value}')

    def okx_withdraw(self):
        value = EVM.uniform_(cng.OKX_AMOUNT)
        okx_withdraw(cng.OKX_CHAIN, self.address, value)
        for chain in cng.OKX_CHAIN:
            EVM.waiting_coin(self.private_key, chain, '', value)

    def BitGet(self):
        value = EVM.uniform_(cng.BitGet_AMOUNT)
        chain = {"zksync": "ZKSYNC ERA", "ethereum": "ERC20"}
        BitGetTr.withdrawal("ETH", self.address, value, chain[cng.BitGet_CHAIN])
        EVM.waiting_coin(self.private_key, cng.BitGet_CHAIN, '', value)

    def deploy_contract(self):
        deploy(self.private_key)

    def Wrapped_ETH(self):
        value = EVM.uniform_(cng.WRAP_VALUE)
        WrapETH.wrapped_ETH(self.private_key, "deposit", value)
        time.sleep(EVM.randint_([30, 60]))
        WrapETH.wrapped_ETH(self.private_key, "withdraw", value)

    def zk_bridge(self):
        value = EVM.uniform_(cng.VALUE_BRIDGE)
        self.defence_balance(value, 'ethereum')
        bridges = ZkBridge(self.private_key, 'ethereum', value)
        bridges.bridge()

    def domains_name(self):
        self.defence_balance(0.003, 'zksync')
        mint_name(self.private_key)

    def merkly_tx(self):
        bridges = MerklyTx(self.private_key)
        bridges.bridge_token()

    def lending_protocol(self):
        value = EVM.uniform_(cng.LENDING_VOLUME)
        protocol = ProtocolRector(self.private_key, 'ETH', value)
        protocol.work_lending()
        time.sleep(15)

    def dex(self):
        amount = EVM.randint_(cng.DEX_AMOUNT)
        name_dex = {'Izumi': Izumi, 'Mute': Mute, 'Odos': Odos, 'Openocean': Openocean, 'Spacefi': SpaceFi,
                    'Syncswap': SyncSwap, 'Zkswap': ZkSwap}
        list_dex = [name_dex[dex] for dex in cng.WORK_DEX]
        last_token = 'ETH'
        l_dex = list_dex.copy()
        random.shuffle(l_dex)
        token = cng.DEX_TOKEN.copy()
        add_ = []
        while amount != 0:
            if amount == 1 and last_token != 'ETH':
                token_to = 'ETH'
            elif amount == 1 and last_token == 'ETH':
                break
            else:
                token.remove(last_token)
                random.shuffle(token)
                token_to = token.pop()
            if not l_dex:
                l_dex = list_dex.copy()
                random.shuffle(l_dex)
            while True:
                dex_add = l_dex.pop()
                if dex_add.token_address(token_to) and dex_add.token_address(last_token):
                    break
                elif not l_dex:
                    l_dex = list_dex.copy()
                    random.shuffle(l_dex)
            add_.append([dex_add, last_token, token_to])
            last_token = token_to
            amount -= 1
            if token_to == 'ETH':
                self.route.append(add_)
                add_ = []
            token = cng.DEX_TOKEN.copy()

    def mint_nft(self):
        nft = [Tevaera.mint_pass, Tevaera.mint_hero]
        for i in range(EVM.randint_(cng.NFT_AMOUNT)):
            nft[i](self.private_key)

    def swap_dex(self, data_all: list):
        for data in data_all:
            if data[1] == 'ETH':
                value = EVM.randint_(cng.DEX_VALUE) / EVM.prices_network('zksync')
            else:
                balance, decimal = EVM.check_balance(self.private_key, 'zksync', data[0].token_address(data[1]))
                value = EVM.DecimalTO(balance, decimal)
            DEX = data[0](self.private_key, data[1], data[2], value)
            DEX.swap()
            wait_token = data[0].token_address(data[2])
            if data[1] == 'ETH':
                value = value * EVM.prices_network('zksync')
            elif data[2] == 'ETH':
                value = value / EVM.prices_network('zksync')
                wait_token = ''
                time.sleep(10)
            EVM.waiting_coin(self.private_key, 'zksync', wait_token, value)
            time.sleep(EVM.randint_(cng.DEX_SLEEP))

    def dmail_msg(self):
        message_dmail(self.private_key)


class DepositETH:
    def __init__(self, private_key):
        self.private_key = private_key
        self.address = Account.from_key(private_key).address

    def withdraw_cex(self):
        if cng.Deposit == "OKX":
            value = EVM.uniform_(cng.OKX_AMOUNT)
            okx_withdraw(cng.OKX_CHAIN, self.address, value)
            for chain in cng.OKX_CHAIN:
                EVM.waiting_coin(self.private_key, chain, '', value)
        if cng.Deposit == "BitGet":
            value = EVM.uniform_(cng.BitGet_AMOUNT)
            chain = {"zksync": "ZKSYNC ERA", "ethereum": "ERC20"}
            BitGetTr.withdrawal("ETH", self.address, value, chain[cng.BitGet_CHAIN])
            EVM.waiting_coin(self.private_key, cng.BitGet_CHAIN, '', value)

    def zkbridge(self):
        value = EVM.uniform_(cng.OKX_AMOUNT)
        okx_withdraw(cng.OKX_CHAIN, self.address, value)
        for chain in cng.OKX_CHAIN:
            EVM.waiting_coin(self.private_key, chain, '', value)
        bridges = ZkBridge(self.private_key, 'ethereum', value, True)
        value = bridges.bridge()
        EVM.waiting_coin(self.private_key, 'zksync', '', value)

    def withdraw(self):
        if cng.Deposit in ["OKX", "BitGet"]:
            self.withdraw_cex()
        elif cng.Deposit == 'ZK_bridge':
            self.zkbridge()


class StuffingTransactions(FuncZksync):
    def creating_path(self):
        name = {'Merkly': self.merkly_tx, 'Wrapped_ETH': self.Wrapped_ETH, 'Domains_Name': self.domains_name,
                'Deploy_Contract': self.deploy_contract, 'Lending_Protocol': self.lending_protocol, 'DEX': self.dex,
                'NFT': self.mint_nft, 'DMAIL': self.dmail_msg}
        list_work = cng.Route.copy()
        if 'DEX' in list_work:
            self.dex()
            list_work.remove('DEX')

        def multiple_addition(data_: list):
            if data_[0] in list_work:
                if not isinstance(data_[1], int):
                    data_[1] = 1
                for _ in range(data_[1]):
                    self.route.append(name[data_[0]])
                list_work.remove(data_[0])

        add_func = [['Lending_protocol', cng.LENDING_AMOUNT], ['Wrapped_ETH', cng.WRAP_AMOUNT],
                    ['DMAIL', cng.DMAIL_AMOUNT]]
        for data in add_func:
            multiple_addition(data)

        for add_name in list_work:
            self.route.append(name[add_name])
        random.shuffle(self.route)

    def start_work(self):
        self.creating_path()
        inv_log().info(self.route)
        for func in self.route:
            if isinstance(func, list):
                self.swap_dex(func)
            else:
                func()
            time.sleep(EVM.randint_([30, 60]))


class WithdrawETH:
    def __init__(self, private_key, address_to):
        self.private_key = private_key
        self.address = Account.from_key(private_key).address
        self.address_to = address_to

    def withdraw(self):
        if cng.Withdraw:
            withdrawal_token(self.private_key, self.address_to)


def main(private_key: str, address_to: str):
    deposit = DepositETH(private_key)
    deposit.withdraw()

    work = StuffingTransactions(private_key)
    work.start_work()

    time.sleep(EVM.randint_([100, 200]))

    withdraw = WithdrawETH(private_key, address_to)
    withdraw.withdraw()

    log().success(f'Worked out wallet {withdraw.address}')


def wallet() -> list:
    with open('wallet.txt', 'r') as file:
        wallets = file.read().splitlines()
        wallets = [wal.split(';') for wal in wallets]
        return wallets

if __name__ == '__main__':
    pass






