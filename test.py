import time
from multiprocessing.dummy import Pool

from DEX.Openocean_Swap import Openocean
from DEX.SyncSwap import SyncSwap
from eth_abi import *
from eth_utils import to_hex, decode_hex
from Contract.Deploy_Contract import deploy, generate_name
from Utils.EVMutils import EVM, AddFee
from DEX.Zkswap import ZkSwap
from DEX.Odos_Swap import Odos
from DEX.SpaceFi_Swap import SpaceFi
from Lending_Protocol.RectorFusion import ProtocolRector
from DEX.Wrap_ETH import WrapETH
from Strategies.ROUTE import FuncZksync, StuffingTransactions, DepositETH, wallet
from Utils.Withdraw import withdrawal_token
from Info.wenser import get_info_wallet, get_info
from eth_account import Account
import pandas as pd
from json import loads

prv = "2c0680f08f9be8b24b5b4fabd97a53f59b4d774438940decc339d8de12875149"
# w3 = EVM.web3('zksync')
# address_to = '0x0000000000000000000000000000000000008006'
# adr = ''
# swapss = SyncSwap(prv, "USDC", 'ETH', 0.841665)
# swapss.swap()
# data_deploy = '0x9c4d535b0000000000000000000000000000000000000000000000000000000000000000010000934867662b76b5f394b0d7c453e1269cdad5c2fba05efafd64967039e200000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000094869207468657265210000000000000000000000000000000000000000000000'
# print("0x49404b7c" + encode(["uint256", "address"], [0, "0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5"]).hex())
# generate_name()

# swap = SyncSwap(prv, 'USDC', 'ETH', 0.328127)
# swap.swap()
# add = AddFee()
# add.balance_from = 3465381501636022
# add.balance_to = 3673240356652448
# add.trade_buy = 290329294470905
# print(add.fee_print())
# protocol = ProtocolRector(prv, "USDT", 0.52)
# print(protocol.check_rf())
# swap = Izumi(prv, "ETH", "USDC", 0.001)
# swap.swap()
# add = FuncZksync(prv)
# add.lending_protocol()
if __name__ == '__main__':
    # start_time_stamp = int(time.time())
    # private = wallet()
    # address = [Account.from_key(adr[0]).address for adr in private]
    # with Pool(10) as pols:
    #     all_balance = pols.map(lambda func: get_info_wallet(func), address)
    # time_stamp = int(time.time())
    # print(time_stamp - start_time_stamp)
    # for i in all_balance:
    #     print(i.__dict__)
    # soul = pd.read_excel('./info/table.xlsx')
    # soul = loads(soul.to_json(orient="records"))
    # print(soul)
    get_info()


