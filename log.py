import logging
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()


def setup_custom_logger(name):
    """
    Setup custom logger
    """
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    return logger
