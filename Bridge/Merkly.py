import json
import math
import time

from web3 import Web3
from eth_abi import encode

from Contract.Bridge_Contract import OpenContract
from Log.Loging import log, inv_log
from Utils.EVMutils import EVM
from Contract.L0_ID import LAYERZERO_CHAINS_ID
from config import RETRY


class MerklyBridge:
    not_chain = ['base', 'kava']
    def __init__(self, privat_key, from_chain, to_chain, amount, retry=0):
        self.retry = retry
        self.privat_key = privat_key
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.amount = amount

    @staticmethod
    def get_adapterParams(gaslimit: int, amount: int):
        return Web3.to_hex(encode(["uint16", "uint64", "uint256"], [2, gaslimit, amount])[30:])

    @staticmethod
    def check_merkly_fees():
        log().info("Начаниаем обновлять данные по Fee")

        def round_to(num, digits=3):
            try:
                if num == 0:
                    return 0
                scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
                if scale < digits:
                    scale = digits
                return round(num, scale)
            except:
                return num

        def call_json(results, outfile):
            with open(f"{outfile}.json", "w") as file:
                json.dump(results, file, indent=4, ensure_ascii=False)

        wallet = '0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5'  # рандомный кошелек
        result = {}

        def fee_tx(from_chain):
            result.update({from_chain: []})
            w3, contract = OpenContract.Merkly(from_chain)
            adapterParams = MerklyBridge.get_adapterParams(250000, int(0.00002 * 1e18)) + wallet[2:].lower()
            for to_chain in LAYERZERO_CHAINS_ID.items():
                to_chain = to_chain[0]

                if from_chain != to_chain:

                    try:
                        send_value = contract.functions.estimateSendFee(LAYERZERO_CHAINS_ID[to_chain],
                                                                        '0x', adapterParams).call()
                        send_value = EVM.DecimalTO(send_value[0], 18)
                        send_value = round_to(send_value * EVM.prices_network(from_chain))
                        if send_value < 0.2 and to_chain not in MerklyBridge.not_chain:
                            result[from_chain].append(to_chain)
                    except Exception:
                        pass
        fee_tx('zksync')

        path = 'merkly_refuel'
        call_json(result, path)
        log().success(f'Результаты {path}.json обновлены')

    def bridge(self, numb=None):
        try:
            web3, contract = OpenContract.Merkly(self.from_chain)
            wallet = web3.eth.account.from_key(self.privat_key).address
            module_str = f'MERKLY | {wallet} | {self.from_chain} | {self.to_chain}'
            self.amount = EVM.DecimalFrom(self.amount, 18)
            to_cain_id = LAYERZERO_CHAINS_ID[self.to_chain]
            adapterParams = MerklyBridge.get_adapterParams(250000, self.amount) + wallet[2:].lower()
            value = contract.functions.estimateSendFee(LAYERZERO_CHAINS_ID[self.to_chain], '0x',
                                                       adapterParams).call()[0]
            value = int(value * 1.2) + self.amount
            inv_log().info(f"{self.from_chain, self.to_chain, value / 1e18}")
            value_ = EVM.DecimalTO(value, 18) * EVM.prices_network(self.from_chain)
            if value_ > 0.6:
                log().info(f"value hard  < 0.6, {value_}")
                inv_log().info("value hard  < 0.6")
                return
            contract_txn = contract.functions.bridgeGas(
                to_cain_id,
                wallet,
                adapterParams
            ).build_transaction(
                {
                    "from": wallet,
                    "value": value,
                    "nonce": web3.eth.get_transaction_count(wallet),
                    'gasPrice': web3.eth.gas_price,
                    'gas': 0,
                }
            )
            contract_txn = EVM.sending_tx(web3, contract_txn, self.from_chain, self.privat_key, self.retry, module_str)
            # contract_txn = EVM.add_gas(web3, contract_txn)
            if not contract_txn:
                inv_log().error(f'not contract_txn -> {to_cain_id, wallet, adapterParams}')
                if self.retry < RETRY:
                    self.retry += 1
                    log().info(f'try again | {wallet}')
                    time.sleep(30)
                    return self.bridge()
            # total_fee = int(contract_txn['gas'] * contract_txn['gasPrice'] + value)
            # if CHECK_GASS:
            #     is_fee = EVM.checker_total_fee(self.from_chain, total_fee)
            #     if not is_fee:
            #         return self.bridge()
            #     else:
            #         contract_txn = EVM.add_gas(web3, contract_txn)
            # tx_hash = EVM.sign_tx(web3, contract_txn, self.privat_key)
            # status = EVM.check_status_tx(self.from_chain, tx_hash)
            # tx_link = f'{RPC[self.from_chain]["scan"]}/{tx_hash}'
            # if status == 1:
            #     log(numb).info(module_str)
            #     log().success(tx_link)
            #
            # elif status == 2:
            #     log().info('Нет ответа, думаем что прошло')
            #     log().info(module_str)
            # else:
            #     log().error(f'{module_str} | tx is failed')
            #     inv_log().error(f'status 0 -> {to_cain_id, wallet, adapterParams}')
            #
            #     self.retry += 1
            #     if self.retry < RETRY:
            #         log().info(f'try again | {wallet}')
            #         return self.bridge()

        except Exception as error:
            log().error(f'MERKLY | {self.from_chain} | {self.to_chain} | error')
            inv_log().error(f'error module {error}')
            if self.retry < RETRY:
                log().info(f'try again in 10 sec.')
                time.sleep(30)
                self.retry += 1
                return self.bridge()


if __name__ == '__main__':
    pass
