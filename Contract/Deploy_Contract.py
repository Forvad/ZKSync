import random

from Utils.EVMutils import EVM
from eth_abi import encode
import requests


def generate_name():
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(api_url, headers={'X-Api-Key': 'Fy+Q8+jgyEkR5DYAvYJb9A==KxPgXK2WbNlE0zOl'})
    if response.status_code == requests.codes.ok:
        res = response.json()['word'].title() + random.choice(['!', '&', '?', '@', '$'])
        return res
    else:
        raise ValueError(f"Error: {response.status_code}, {response.text}")


def deploy(private_key):
    name = encode(['string'], [generate_name()]).hex()
    data_deploy = '0x9c4d535b0000000000000000000000000000000000000000000000000000000000000000010000934867662b76b' \
                  '5f394b0d7c453e1269cdad5c2fba05efafd64967039e2000000000000000000000000000000000000000000000000' \
                  '00000000000000600000000000000000000000000000000000000000000000000000000000000060' + name
    w3 = EVM.web3("zksync")
    contract = w3.to_checksum_address("0x0000000000000000000000000000000000008006")
    address = w3.eth.account.from_key(private_key).address
    nonce = w3.eth.get_transaction_count(address)
    tx = {
        'from': address,
        'to': contract,
        'nonce': nonce,
        'data': data_deploy,
        'chainId': w3.eth.chain_id,
        'maxFeePerGas': int(w3.eth.gas_price * 1.1),
        'maxPriorityFeePerGas': w3.eth.gas_price
    }
    EVM.sending_tx(w3, tx, 'zksync', private_key, 0, 'Deploy Contract')

if __name__ == '__main__':
    pass