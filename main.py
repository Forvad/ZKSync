import time

from Strategies.ROUTE import main, wallet, search_balance
import config as cng
from Utils.EVMutils import EVM
from multiprocessing.dummy import Pool
from Log.Loging import log


def zksync_tx():
    data = wallet()
    value = 0
    for private, address_to in data:
        if cng.CHECK_GWEI:
            EVM.check_gwei()
        value = main(private, address_to, value)
        time.sleep(EVM.randint_([60, 120]))
        search_balance(value)


def zksync_tx_():
    private = wallet()
    if cng.CHECK_GWEI:
        EVM.check_gwei()

    def work(private_key, address_to):
        EVM.delay_start()
        main(private_key, address_to)
    try:
        with Pool(cng.THREAD) as pols:
            pols.map(lambda func: work(func[0], func[1]), private)
    except BaseException as error:
        log().error(error)


if __name__ == '__main__':
    print("""
                 1 - Очередь
                 2 - Потоки
    """)
    works = input('Какой модуль крутим: ')
    funcs = {1: zksync_tx, 2: zksync_tx_}
    funcs[int(works)]()
