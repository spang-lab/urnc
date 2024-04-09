"""Logging functionality for URNC"""

import logging
import os
import sys
from typing import NoReturn

GREY = "\x1b[38;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # log_fmt = "%(asctime)s %(levelname)s: %(message)s" # introduce with separate issue
        log_fmt = "%(levelname)s - %(message)s"
        formats = {
            logging.DEBUG: f"{GREY}{log_fmt}{RESET}",
            logging.INFO: f"{GREY}{log_fmt}{RESET}",
            logging.WARNING: f"{YELLOW}{log_fmt}{RESET}",
            logging.ERROR: f"{RED}{log_fmt}{RESET}",
            logging.CRITICAL: f"{BOLD_RED}{log_fmt}{RESET}",
        }
        log_fmt = formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def get_handler():
    try:
        log_file = "/var/log/urnc.log"
        h = logging.FileHandler(log_file)
        print(f"Logging to {log_file}")
        return h
    except Exception:
        pass
    try:
        log_file = os.path.expanduser("~/.urnc.log")
        h = logging.FileHandler(log_file)
        print(f"Logging to {log_file}")
        return h
    except Exception:
        pass
    return None


def setup_logger(use_file: bool = True, verbose: bool = False) -> None:
    """
    Sets up a logger with a custom handler and formatter.

    Parameters:
        use_file: If True, a file handler is added to the logger.
        verbose: If True, the logger's level is set to DEBUG. Otherwise, to INFO.

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if use_file:
        handler = get_handler()
        if handler is not None:
            logger.addHandler(handler)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(CustomFormatter())
    logger.addHandler(stdout_handler)


def dbg(msg):
    logger = logging.getLogger(__name__)
    logger.debug(msg)


def log(msg):
    logger = logging.getLogger(__name__)
    logger.info(msg)


def warn(msg):
    logger = logging.getLogger(__name__)
    logger.warning(msg)


def error(msg):
    logger = logging.getLogger(__name__)
    logger.error(msg)


def critical(msg) -> NoReturn:
    logger = logging.getLogger(__name__)
    logger.critical(msg)
    raise Exception(msg)
