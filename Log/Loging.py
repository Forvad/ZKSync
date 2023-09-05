from sys import stderr
from loguru import logger
from multiprocessing.dummy import current_process


def log(numb=None):
    if 'MainThread' in str(current_process()):
        try:
            logger.remove()
            if not numb:
                logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                          ' | <level>{level: <2}</level>'
                                          ' | <level>{message}</level>')
            else:
                logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                          ' | <level>{level: <2}</level>'
                                          f' | <level>{numb[0]}/{numb[1]}</level>'
                                          ' | <level>{message}</level>')
            logger.add('./Log/Main.log')
            return logger
        except BaseException:
            return logger
    else:
        try:
            x = lambda a: int(str(a).split('Thread-')[1].split(',')[0])
            proc = x(current_process())
        except ValueError:
            x = lambda a: int(str(a).split('Thread-')[1].split()[0])
            proc = x(current_process())
        try:
            logger.remove()
            if not numb:
                logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                          f' | <level>Thread-{proc}</level>'
                                          ' | <level>{level: <2}</level>'
                                          ' | <level>{message}</level>')
            else:
                logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                          f' | <level>Thread-{proc}</level>'
                                          ' | <level>{level: <2}</level>'
                                          f' | <level>{numb[0]}/{numb[1]}</level>'
                                          ' | <level>{message}</level>')
        except:
            pass
        logger.add(f'./Log/Thread-{x(current_process())}.log')
    return logger


def inv_log():
    if 'MainThread' in str(current_process()):
        try:
            logger.remove()
            logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                      ' | <level>{level: <2}</level>'
                                      ' | <level>{message}</level>')
            logger.remove(handler_id=None)
            logger.add('./Log/Main.log')
            return logger
        except BaseException:
            return logger
    else:
        try:
            x = lambda a: int(str(a).split('Thread-')[1].split(',')[0])
            proc = x(current_process())
        except ValueError:
            x = lambda a: int(str(a).split('Thread-')[1].split()[0])
            proc = x(current_process())
        try:
            logger.remove()
            logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                      f' | <level>Thread-{proc}</level>'
                                      ' | <level>{level: <2}</level>'
                                      ' | <level>{message}</level>')
        except:
            pass
        logger.remove(handler_id=None)
        logger.add(f'./Log/Thread-{x(current_process())}.log')
    return logger

if __name__ == '__main__':
    pass
