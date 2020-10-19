import logging


def init_logger(logger: logging.Logger):
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s\t%(asctime)s\t%(name)s\t%(message)s')
    console_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(console_handler)