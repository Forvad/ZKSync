import random
import time
import datetime

from eth_account import Account
from requests import get
from pyuseragents import random as random_useragent
from config import Range_Operation, Route
from Log.Loging import inv_log
from Strategies.ROUTE import FuncZksync, wallet
import config as cng
from Utils.EVMutils import EVM

from DEX.Izumi_Swap import Izumi
from DEX.Zkswap import ZkSwap
from DEX.Odos_Swap import Odos
from DEX.SyncSwap import SyncSwap
from DEX.Openocean_Swap import Openocean
from DEX.MuteSwap import Mute
from DEX.SpaceFi_Swap import SpaceFi
from NFT.Tevaera import Tevaera
from NFT.Nfts2 import Nfts2


class Contract:
    contract = {'Merkly': ['0x06092ebA6e014D3eF3802Fe1bc843056F640656A'],
                'Wrapped_ETH': ['0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'],
                # izumi, mute, spacefi, sync, zk, odos, openocean
                'DEX': ['0x943ac2310D9BC703d6AB5e5e76876e212100f894', '0x8B791913eB07C32779a16750e3868aA8495F5964',
                        '0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d', '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
                        '0x18381c0f738146Fb694DE18D1106BdE2BE040Fa4', '0x4bBa932E9792A2b917D47830C93a9BC79320E4f7',
                        '0x36A1aCbbCAfca2468b85011DDD16E7Cb4d673230'],
                'Domains_Name': ['0xAE23B6E7f91DDeBD3B70d74d20583E3e674Bd94f'],
                'Deploy_Contract': ['0x0000000000000000000000000000000000008006'],
                'Lending_Protocol': ['0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6'],
                'NFT': ['0xd29Aa7bdD3cbb32557973daD995A3219D307721f', '0x50B2b7092bCC15fbB8ac74fE9796Cf24602897Ad'],
                'DMAIL': ['0x981F198286E40F9979274E0876636E9144B8FB8E']}
    DEX = {'0x943ac2310D9BC703d6AB5e5e76876e212100f894': Izumi,
           "0x8B791913eB07C32779a16750e3868aA8495F5964": Mute,
           "0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d": SpaceFi,
           "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295": SyncSwap,
           "0x18381c0f738146Fb694DE18D1106BdE2BE040Fa4": ZkSwap,
           "0x4bBa932E9792A2b917D47830C93a9BC79320E4f7": Odos,
           "0x36A1aCbbCAfca2468b85011DDD16E7Cb4d673230": Openocean}
    NFT = {'0xd29Aa7bdD3cbb32557973daD995A3219D307721f': Tevaera.mint_pass,
           '0x50B2b7092bCC15fbB8ac74fE9796Cf24602897Ad': Tevaera.mint_hero,
           '0x19677384AC7a374D46E252a803e345f7257FC10D': Nfts2,
           '0x9294ff686298dF54019Ed56B9C9C6195Ba87af18': Nfts2}


def checking_last_date(address: str) -> bool:
    try:
        headers = {
            'user-agent': random_useragent(),
        }
        response = get(f'https://block-explorer-api.mainnet.zksync.io/address/{address}/'
                       f'transfers?limit=100&page=1', headers=headers).json()
        json_data = response["items"]
        if json_data:
            time_ = json_data[0]["timestamp"].replace('Z', '').replace('T', ' ')
            api_time = datetime.datetime.fromisoformat(time_) + datetime.timedelta(days=Range_Operation)
            return datetime.datetime.now() > api_time
            # time_str = json_data[0]["timestamp"].split(".")[0].replace('T', '-').replace(':', '-')
            # time_list = time_str.split('-')
            # time_list = [int(i)for i in time_list]
            # time_ = datetime.date(time_list[0], time_list[1], time_list[2])
            # range_op = 86400 * Range_Operation
            # need_time = int(time.mktime(time_.timetuple()) + range_op + (3600 * time_list[3] + 60 * time_list[4]
            #                                                              + time_list[5]))
            # return int(time.time()) > need_time
        else:
            inv_log().error(f'address: {address}, response: {response}')
            return False
    except BaseException as errors:
        inv_log().error(f'address: {address}, error: {errors}')
        return False


class WorkAuto(FuncZksync):
    @staticmethod
    def use_contract(address):
        url = f"https://block-explorer-api.mainnet.zksync.io/transactions?address={address}&limit=100&page=1"
        headers = {
            'user-agent': random_useragent(),
        }
        data = get(url, headers=headers).json()
        contract = []
        if data["items"]:
            for data_ in data["items"]:
                if data_["to"] not in contract:
                    contract.append(data_["to"])
        return contract

    @staticmethod
    def not_use_contract(address):
        not_use = {}
        use = WorkAuto.use_contract(address)
        random.shuffle(use)
        for func in Route:
            for contract in Contract.contract[func]:
                if contract not in use:
                    if func in not_use:
                        not_use[func].append(contract)
                        random.shuffle(not_use[func])
                    else:
                        not_use[func] = [contract]
        return not_use

    def check_USDC(self):
        balance_USDC, decimal = EVM.check_balance(self.private_key, 'zksync', Mute.token_address('USDC'))
        if balance_USDC >= EVM.DecimalFrom(0.1, decimal):
            return 'USDC', 'ETH'
        else:
            return 'ETH', 'USDC'

    def work_patch(self):
        name = {'Merkly': self.merkly_tx, 'Wrapped_ETH': self.Wrapped_ETH,
                'Domains_Name': self.domains_name,
                'Deploy_Contract': self.deploy_contract, 'Lending_Protocol': self.lending_protocol,
                'DMAIL': self.dmail_msg}
        need_work = self.not_use_contract(self.address)
        amount = EVM.randint_(cng.Tx_Operation)
        while amount > 0:
            if need_work:
                for name_func, contract in need_work.items():
                    if amount <= 0:
                        return
                    if name_func == 'DEX':
                        for contracts in contract:
                            symbol_from_to = self.check_USDC()
                            self.swap_dex([[Contract.DEX[contracts], symbol_from_to[0], symbol_from_to[1]]])
                            amount -= 1
                            if amount <= 0:
                                return
                    elif name_func == 'NFT':
                        for contract_ in contract:
                            if amount <= 0:
                                return
                            if isinstance(Contract.NFT[contract_], Nfts2):
                                for name, contract_nft in Nfts2.contract.items():
                                    if contract_nft.lower() == contract_.lower():
                                        Nfts2.mint(self.private_key, name)
                                        amount -= 1
                            else:
                                Contract.NFT[contract_](self.private_key)
                                amount -= 1
                    else:
                        name[name_func]()
                        amount -= 1
                    time.sleep(EVM.randint_([5, 10]))
            else:
                func = ['Merkly']#, 'DMAIL', 'DEX']
                funcs = func.copy()
                random.shuffle(funcs)
                for _ in range(amount):
                    if not funcs:
                        funcs = func.copy()
                        random.shuffle(funcs)
                    work_func = funcs.pop()
                    if work_func == 'DEX':
                        contract = random.choice(Contract.contract['DEX'])
                        symbol_from_to = self.check_USDC()
                        self.swap_dex([[Contract.DEX[contract], symbol_from_to[0], symbol_from_to[1]]])
                    else:
                        name[work_func]()
                    time.sleep(EVM.randint_([5, 10]))
                return


def main():
    private = wallet()
    inv_log().success(f'Start work {len(private)} wallet')
    while True:
        for key in private:
            address = Account.from_key(key[0]).address
            if checking_last_date(address):
                if cng.CHECK_GWEI:
                    EVM.check_gwei()
                work = WorkAuto(key[0])
                work.work_patch()
            time.sleep(EVM.randint_([10, 15]))
        time.sleep(21600)


if __name__ == '__main__':
    main()
