import datetime
import random
import time


from multiprocessing.dummy import current_process
from web3 import Web3
from Contract.RPC import RPC
from requests import get
from config import MAX_GAS_CHARGE, GWEI, RETRY, CHECK_GASS
from Log.Loging import log, inv_log
from Abi.abi import ABI
from DateBase.Data import DateBase


class AddFee:
    def __init__(self):
        self.balance_from = 0
        self.balance_to = 0
        self.trade_buy = 0
        self.trade_sell = 0

    def fee_print(self):
        if self.trade_buy:
            # Когда эфир приходит на баланс
            return round(EVM.DecimalTO(self.balance_from - (self.balance_to - self.trade_buy), 18) \
                   * EVM.prices_network('zksync'), 3)
        elif self.trade_sell:
            # Когда эфир уходит с баланса
            return round(EVM.DecimalTO(self.balance_from - (self.trade_sell + self.balance_to), 18)\
                   * EVM.prices_network('zksync'), 3)
        else:
            return round(EVM.DecimalTO(self.balance_from - self.balance_to, 18) * EVM.prices_network('zksync'), 3)


class EVM:
    @staticmethod
    def web3(chain: str) -> Web3:
        """Opening RPC in Web3"""
        rpc = RPC[chain]['rpc']
        web3 = Web3(Web3.HTTPProvider(rpc))
        return web3

    @staticmethod
    def DecimalTO(value: (float, int), decimal: int) -> int | float:
        """Subtract decimal"""
        if not isinstance(value, (int, float)) and not isinstance(decimal, int):
            inv_log().info(f'vaule = {value}, decimal = {decimal}')
            raise ValueError('decimal or value are not correct')
        return value / 10 ** decimal

    @staticmethod
    def DecimalFrom(value: (float, int), decimal: int) -> int:
        """Adding decimal"""
        if not isinstance(value, (int, float)) and not isinstance(decimal, int):
            inv_log().info(f'vaule = {value}, decimal = {decimal}')
            raise ValueError('decimal or value are not correct')
        return int(value * 10 ** decimal)

    @staticmethod
    def prices_network(chain: str) -> float:
        """Find out the price of the coin"""
        try:
            symbol = RPC[chain]['token']
            response = get(url=f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT')
            check = 'binance'
            if response.status_code == 400:
                result = response.json()
                if result["msg"] == "Invalid symbol.":
                    response = get(url=f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT')
                    check = 'cryptocompare'
            if response.status_code != 200:
                log().info('Limit on the number of requests, we sleep for 30 seconds')
                log().info(f"status_code = {response.status_code}, text = {response.text}")
                time.sleep(30)
                return EVM.prices_network(chain)
            if check == 'binance':
                result = response.json()
                price = round(float(result['price']), 4)
            else:
                result = [response.json()]
                price = float(result[0]['USDT'])
            return price
        except BaseException as error:
            log().error(f"chain: {chain}, error: {error}")
            time.sleep(5)
            EVM.prices_network(chain)

    @staticmethod
    def add_gas(web3: Web3, contract_txn: dict) -> dict | bool:
        """Adding gas to the transaction"""
        try:
            pluser = [1.05, 1.07]
            gasLimit = web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
            return contract_txn
        except BaseException as error:
            log().error(f'{error}')
            return False

    @staticmethod
    def checker_total_fee(chain: str, gas: float) -> bool:
        """Checking the gas limit"""
        PRICES_NATIVE = EVM.prices_network(chain)
        gas = EVM.DecimalTO(gas, 18) * PRICES_NATIVE
        if gas > MAX_GAS_CHARGE[chain]:
            log().info(f'gas is too high : {gas}$ > {MAX_GAS_CHARGE[chain]}$. sleep and try again')
            time.sleep(15)
            return False
        else:
            return True

    @staticmethod
    def sign_tx(web3: Web3, contract_txn: dict, private_key: str) -> str | bool:
        """transaction signature"""
        try:
            signed_tx = web3.eth.account.sign_transaction(contract_txn, private_key)
            raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx_hash)
            return tx_hash
        except BaseException as error:
            log().error(f'{error}')
            return False

    @staticmethod
    def check_status_tx(chain: str, tx_hash: str) -> int:
        """Checking the transaction for patency"""
        start_time_stamp = int(time.time())
        while True:
            try:
                if not tx_hash:
                    return 0
                time.sleep(3)
                web3 = EVM.web3(chain)
                status_ = web3.eth.get_transaction_receipt(tx_hash)
                status = status_["status"]

                if status in [0, 1]:
                    return status
            except BaseException:
                time_stamp = int(time.time())
                if time_stamp - start_time_stamp > 100:
                    return 2
                time.sleep(1)

    @staticmethod
    def decimal_token(chain: str, token_address: str) -> int:
        web3 = EVM.web3(chain)
        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ABI['abi_ERC20'])
        decimals = token_contract.functions.decimals().call()
        return decimals, token_contract

    @staticmethod
    def check_balance(private_key: str, chain: str, address_contract: str) -> (int, int):
        """Information about the coin balance"""
        try:
            web3 = EVM.web3(chain)
            try:
                wallet = web3.eth.account.from_key(private_key).address
            except BaseException:
                wallet = private_key
            if address_contract == '':  # eth
                balance = web3.eth.get_balance(web3.to_checksum_address(wallet))
                decimal = 18
            else:
                decimal, contract = EVM.decimal_token(chain, address_contract)
                balance = contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()

            return int(balance), decimal

        except Exception as error_:
            log().error(f"{error_}")
            time.sleep(1)
            EVM.check_balance(private_key, chain, address_contract)

    @staticmethod
    def randint_(amount: list) -> int:
        return random.randint(amount[0], amount[1])

    @staticmethod
    def uniform_(amount: list) -> float:
        return random.uniform(amount[0], amount[1])

    @staticmethod
    def delay_start() -> None:
        """Delay in streaming mode"""
        if 'MainThread' in str(current_process()):
            pass
        else:
            try:
                x = lambda a: int(str(a).split('Thread-')[1].split(',')[0])
                sleep_ = 15 * x(current_process())
                time.sleep(sleep_)
            except ValueError:
                x = lambda a: int(str(a).split('Thread-')[1].split()[0])
                sleep_ = 15 * x(current_process())
                time.sleep(sleep_)

    @staticmethod
    def check_gwei() -> None:
        """Checking GWEI"""
        w3 = EVM.web3('ethereum')
        gas_price = w3.eth.gas_price
        gwei_gas_price = w3.from_wei(gas_price, 'gwei')
        while gwei_gas_price > GWEI:
            log().info(f'GWEI {gwei_gas_price} > {GWEI}')
            gas_price = w3.eth.gas_price
            gwei_gas_price = w3.from_wei(gas_price, 'gwei')
            time.sleep(10)

    @staticmethod
    def sending_tx(web3: Web3, contract_txn: dict, chain: str, private_key: str,  retry: int, module_str: str,
                   add_buy=0, sell_add=0, numb=None):
        wallet = contract_txn["from"]
        contract_txn = EVM.add_gas(web3, contract_txn)
        if not contract_txn:
            if retry < RETRY:
                log().info(f'try again | {wallet}')
                return False
        if 'gasPrice' in contract_txn:
            total_fee = int(contract_txn['gas'] * contract_txn['gasPrice'])
        else:
            total_fee = int(contract_txn['gas'] * contract_txn['maxFeePerGas'])
        if CHECK_GASS:
            is_fee = EVM.checker_total_fee(chain, total_fee)
            if not is_fee:
                return False
            else:
                contract_txn = EVM.add_gas(web3, contract_txn)
        tx_hash = EVM.sign_tx(web3, contract_txn, private_key)
        status = EVM.check_status_tx(chain, tx_hash)
        tx_link = f'{RPC[chain]["scan"]}/{tx_hash}'
        if status == 1:
            log(numb).info(module_str)
            log().success(tx_link)
            time.sleep(2)
            return True

        elif status == 2:
            log().info('Нет ответа, думаем что прошло')
            log().info(module_str)
            log().success(tx_link)
            return True
        else:
            log().error(f'{module_str} | tx is failed')
            # inv_log().error(f'status 0 -> {to_cain_id, wallet, adapterParams}')

            retry += 1
            if retry < RETRY:
                log().info(f'try again | {wallet}')
                return False

    @staticmethod
    def approve(amount, private_key, chain, token_address, spender, retry=0):
        try:
            web3 = EVM.web3(chain)
            spender = Web3.to_checksum_address(spender)
            wallet = web3.eth.account.from_key(private_key).address
            contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ABI['abi_ERC20'])
            allowance_amount = contract.functions.allowance(wallet, spender).call()
            # contract, decimals, symbol = EVMUtils.check_data_token(chain, token_address)

            # module_str = f'approve : {symbol}'

            if amount > allowance_amount:
                contract_txn = contract.functions.approve(
                    spender,
                    115792089237316195423570985008687907853269984665640564039457584007913129639935
                ).build_transaction(
                    {
                        "chainId": web3.eth.chain_id,
                        "from": wallet,
                        "nonce": web3.eth.get_transaction_count(wallet),
                        'gasPrice': web3.eth.gas_price,
                        'gas': 0,
                        "value": 0
                    }
                )

                contract_txn = EVM.add_gas(web3, contract_txn)
                if not contract_txn:
                    if RETRY < retry:
                        return EVM.approve(amount, private_key, chain, token_address, spender, retry+1)

                tx_hash = EVM.sign_tx(web3, contract_txn, private_key)
                # tx_link = f'{RPC[chain]["scan"]}/{tx_hash}'

                status = EVM.check_status_tx(chain, tx_hash)

                if status == 1:
                    allowance_amount = contract.functions.allowance(wallet, spender).call()
                    while amount > allowance_amount:
                        time.sleep(5)
                        allowance_amount = contract.functions.allowance(wallet, spender).call()

                else:
                    if retry < RETRY:
                        log().info(f"try again in 15 sec.")
                        time.sleep(15)
                        EVM.approve(amount, private_key, chain, token_address, spender, retry + 1)
        except Exception as error:
            log().error(f'{error}')
            if retry < 3:
                log().info(f"try again in 15 sec.")
                time.sleep(15)
                EVM.approve(amount, private_key, chain, token_address, spender, retry + 1)

    @staticmethod
    def open_private():
        with open('wallet.txt', 'r') as file:
            file = file.read().splitlines()
            return file

    @staticmethod
    def waiting_coin(private_key: str, chain: str, address_coin: str, value: (int, float)) -> None:
        """Waiting for a token on the account"""
        coins_value, decimal = EVM.check_balance(private_key, chain, address_coin)
        value = EVM.DecimalFrom(value * 0.8, decimal)
        while coins_value < value:
            time.sleep(15)
            try:
                coins_value, decimal = EVM.check_balance(private_key, chain, address_coin)
            except BaseException:
                inv_log().error(f'Eror waiting_coin {chain, address_coin, value}')
                coins_value = 0
                time.sleep(10)