import logging
from logging.config import dictConfig

LOG_LEVEL = logging.DEBUG


def init_logging() -> None:
    level = logging.getLevelName(LOG_LEVEL)
    log_format = "%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s"
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": log_format,
                }
            },
            "handlers": {
                "wsgi": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout", "formatter": "default"}
            },
            "root": {"level": level, "handlers": ["wsgi"]},
        }
    )
