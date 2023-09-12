from web3 import Web3
from Utils.EVMutils import EVM
from Abi.abi import ABI


class OpenContract:
    @staticmethod
    def add_contract(chain: str, address: str, abi: str) -> (Web3, Web3):
        web3 = EVM.web3(chain)
        address_contract = web3.to_checksum_address(address)
        contract = web3.eth.contract(address=address_contract, abi=abi)
        return web3, contract

    @staticmethod
    def Merkly(chain: str) -> (Web3, Web3):
        MERKLY_CONTRACTS = {
                'optimism': '0x9C5df4caA9734eE5Eb15Ef56cdB7d430d8943f29',
                'bsc': '0xa6e9cE15F4e1BFf513AC568E3121551C8007f841',
                'arbitrum': '0xa0Ad7f84fbD75E75f668022b267D292dE684ad33',
                'polygon': '0xa6e9cE15F4e1BFf513AC568E3121551C8007f841',
                'zksync': '0x06092ebA6e014D3eF3802Fe1bc843056F640656A',
                'avalanche': '0xBD5E9e4b0f7C8548C9B1D7BE1a0b3455cff1c4Ab',
                'gnosis': '0x3179b1a941494f2C6d6f0eC4DE60e450BB97b2f0',
                'fantom': '0x6bf98654205B1AC38645880Ae20fc00B0bB9FFCA',
                'nova': '0xac1d58924CB939F28198210370f05222BE1a222e',
                'coredao': '0xac1d58924CB939F28198210370f05222BE1a222e',
                'celo': '0xA07f2e99eAa338aCF66337Baf99551BDCFd3AB00',
                'moonbeam': '0xe83B1384C6D6E617581a9A8c2BBf8F32D5cbb802',
                'moonriver': '0xDa2620Bc8dC9ecAf45f4c5BF6878f3e98663C53E',
                "kava": "0x3179b1a941494f2C6d6f0eC4DE60e450BB97b2f0",
                "tenet": "0x64107d42C812BCC3153cd52da0926bc8f4Ce7B57",
                "harmony": "0x79DB0f1A83f8e743550EeB5DD5B0B83334F2F083",
                'metis': '0x59c0A752c641345bbc7426Dfb0111E62579aa310',
                'fuse': '0x2936343dfa0f9cDDf4aE78CC7aA83f02c5FfAcd6',
                "okx": "0xeFDcba9D2dB7D78fc064242E99b968Ec1734DeBE"
            }
        return OpenContract.add_contract(chain, MERKLY_CONTRACTS[chain], ABI['abi_Merkly'])

    @staticmethod
    def ZkBridge(chain):
        contract_address = {"ethereum": "0x32400084C286CF3E17e7B677ea9583e60a000324"}
        return OpenContract.add_contract(chain, contract_address[chain], ABI['abi_ZKbridge'])

    @staticmethod
    def acrossbridge():
        return OpenContract.add_contract('zksync', '0xE0B015E54d54fc84a6cB9B666099c46adE9335FF', ABI['abi_Across'])
