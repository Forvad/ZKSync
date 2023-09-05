from Strategies.ROUTE import main, wallet
import config as cng
from Utils.EVMutils import EVM
from multiprocessing.dummy import Pool


def zksync_tx():
    private = wallet()
    if cng.CHECK_GWEI:
        EVM.check_gwei()

    def work(private_key, address_to):
        EVM.delay_start()
        main(private_key, address_to)
    # try:
    with Pool(cng.THREAD) as pols:
        pols.map(lambda func: work(func[0], func[1]), private)
    # except BaseException as error:
    #     log().error(error)


if __name__ == '__main__':
    zksync_tx()
