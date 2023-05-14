"""
Init the logger
"""

import logging

import colorlog

from config import config

conf = config.conf

STATUS = 25

def init_logger():
    logging.addLevelName(STATUS, "STATUS")
    handler = logging.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(message)s",
        log_colors={
            "DEBUG": "white",
            "INFO": "cyan,bold",
            "STATUS": "green,bold",
            "WARNING": "yellow,bold",
            "ERROR": "red,bold",
            "CRITICAL": "white,bg_red,bold"
        }
    ))
    logger = logging.getLogger("StructuraImproved")
    logger.addHandler(handler)
    logger.setLevel({
        "debug": 10,
        "info": 20,
        "status": 25,
        "warning": 30,
        "error": 40,
        "critical": 50
    }.get(conf["log_level"].lower(), 20))

if __name__ == "__main__":
    init_logger()
