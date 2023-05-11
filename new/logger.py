from datetime import datetime, timezone
import logging
from tzlocal import get_localzone
import multiprocessing


def gen_log(name='test'):
    # Set up logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # handle the time zone
    # utc_dt = datetime.now(timezone.utc)
    # + "." + utc_dt.astimezone(get_localzone()).strftime('%Y-%m-%d %H-%M-%S') +
    handler = logging.FileHandler(name + ".log")

    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # FIXME platforms... Options...

    return logger


def error_logger(logger, error):
    logger.error(error)


def info_logger(logger, info):
    logger.info(info)