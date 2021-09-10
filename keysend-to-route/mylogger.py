import logging

def get_my_logger():
    logger = logging.getLogger('keysend-to-route')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('keysend-to-route.log')
    fh.setLevel('DEBUG')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

