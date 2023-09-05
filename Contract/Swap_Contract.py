from web3 import Web3
from Utils.EVMutils import EVM
from Abi.abi import ABI
from Contract.Bridge_Contract import OpenContract


class ContractSync(OpenContract):
    @staticmethod
    def sync_router():
        return ContractSync.add_contract('zksync', '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
                                         ABI['abi_SyncSwap_router'])

    @staticmethod
    def sync_pool(address: str):
        return ContractSync.add_contract('zksync', address, ABI['abi_SyncSwap_pool'])

    @staticmethod
    def geet_pool():
        return ContractSync.add_contract('zksync', '0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb',
                                         ABI['abi_Get_pool'])

    @staticmethod
    def mute():
        return ContractSync.add_contract('zksync', '0x8B791913eB07C32779a16750e3868aA8495F5964',
                                         ABI['abi_MuteSwap'])

    @staticmethod
    def token(address):
        return ContractSync.add_contract('zksync', address, ABI['abi_ERC20'])

    @staticmethod
    def spacefi():
        return ContractSync.add_contract('zksync', '0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d',
                                         ABI['abi_SpaceFi'])

    @staticmethod
    def zkswap():
        return ContractSync.add_contract('zksync', '0x18381c0f738146Fb694DE18D1106BdE2BE040Fa4',
                                         ABI['abi_SpaceFi'])

    @staticmethod
    def zizumi():
        return ContractSync.add_contract('zksync', '0x943ac2310D9BC703d6AB5e5e76876e212100f894',
                                         ABI['abi_izumi'])

