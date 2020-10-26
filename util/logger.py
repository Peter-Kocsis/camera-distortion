"""Module for handling the logger"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = ["MIT License"]
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Released"

import logging


def init_logger(logger: logging.Logger):
    """
    Initialize the logger
    :param logger: The logger to be initialized
    """
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(levelname)s\t%(asctime)s\t%(name)s\t%(message)s")
    console_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(console_handler)
