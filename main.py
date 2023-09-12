import time

from Strategies.ROUTE import main, wallet, search_balance
import config as cng
from Utils.EVMutils import EVM
from multiprocessing.dummy import Pool


def zksync_tx():
    data = wallet()
    value = 0
    for private, address_to in data:
        if cng.CHECK_GWEI:
            EVM.check_gwei()
        value = main(private, address_to, value)
        time.sleep(EVM.randint_([60, 120]))
        search_balance(value)


if __name__ == '__main__':
    zksync_tx()
