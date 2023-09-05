import random

from eth_abi import encode
from web3 import Web3
from Utils.EVMutils import EVM
from Contract.Deploy_Contract import generate_name
from config import RETRY


# https://app.zkns.domains/

def mint_name(private_key, retry=0):
    name = generate_name() + str(random.randint(111, 999))
    web3 = EVM.web3("zksync")
    address = web3.eth.account.from_key(private_key).address

    data = "0x9caf2b97" + Web3.to_hex(
        encode(["string", "address", "uint256", "string", "address", "address", "bytes32"],
               [name, address, 31536000, "zk",
                "0x135A32C16765cEF67dEC3aE53b03F8c21FEeC0d8", address,
                bytes(0x0000000000000000000000000000000000000000000000000000000000000000)
                ]))[2:]
    tx = {
        'from': address,
        'to': Web3.to_checksum_address("0xAE23B6E7f91DDeBD3B70d74d20583E3e674Bd94f"),
        'nonce': web3.eth.get_transaction_count(address),
        'value': EVM.DecimalFrom(0.0027838, 18),
        'data': data,
        'chainId': web3.eth.chain_id,
        'maxFeePerGas': int(web3.eth.gas_price * 1.1),
        'maxPriorityFeePerGas': web3.eth.gas_price
    }
    tx_bool = EVM.sending_tx(web3, tx, 'zksync', private_key, 0, "", sell_add=False)
    if not tx_bool:
        if retry < RETRY:
            return mint_name(private_key, retry+1)


# def domain_use():
#     # "0xfd74537f" +
#     web3 = EVM.web3("zksync")
#     prv = "0x9e4d9a51604a7a5a5fddb8be258732c4df9d2e7650014beb804fa19a82d3ef3c"
#     address = web3.eth.account.from_key(prv).address
#     data = Web3.to_hex(
#         encode(["string"], ["test20222"]))[2:]
#     print(data)


if __name__ == "__main__":
   pass
