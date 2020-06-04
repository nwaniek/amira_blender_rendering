#!/usr/bin/env python

# logging setup

import os
import logging

try:
    from verboselogs import VerboseLogger as getLogger
except ImportError:
    print(
        "FAIL to import verboselogs, consider installing with pip for additional log levels"
    )
    from logging import getLogger

try:
    import coloredlogs
    coloredlogs.DEFAULT_LEVEL_STYLES["notice"]["color"] = 176
    coloredlogs.DEFAULT_LEVEL_STYLES["critical"]["color"] = "white"
    coloredlogs.DEFAULT_LEVEL_STYLES["critical"]["background"] = "red"
except ImportError:
    print("FAIL to import coloredlogs, consider installing with pip")
    coloredlogs = None


# local logger configuration
__logger_name = "amira_blender_rendering"
__logger_logdir = os.path.expandvars("$HOME/.amira_blender_rendering")
__logger_filename = os.path.join(__logger_logdir, f"{__logger_name}.log")
# __logger_loglevel = logging.INFO

__basic_format = "{} {} | {}, {}:{} | {}".format(
    "%(asctime)s",
    "%(levelname)s",
    "%(filename)s",
    "%(funcName)s",
    "%(lineno)d",
    "%(message)s",
)

__colored_format = "%(asctime)s %(filename)s %(lineno)d %(levelname)s %(message)s"

__terminal_format = "[{}] {}:{} | {}".format(
    "%(levelname)s",
    "%(filename)s",
    "%(lineno)d",
    "%(message)s",
)


def get_logger(level="INFO", fmt=None):
    """This function returns a logger instance."""

    # create directory of necessary
    if not os.path.exists(__logger_logdir):
        os.mkdir(__logger_logdir)

    # setup logger once. Note that basicConfig does nothing (as stated in the
    # documentation) if the root logger was already setup. So we can basically
    # re-call it here as often as we want.
    if fmt is None:
        fmt = __basic_format

    logging.basicConfig(
        level=level,
        format=fmt,
        filename=__logger_filename
    )

    if coloredlogs is not None:
        coloredlogs.install(
            level=level,
            datefmt="%H:%M:%S",  # default includes date
            # default format:
            # %(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s
            fmt=__colored_format,
        )

    logger = getLogger(__logger_name)

    return logger


def _get_level_enum(level):
    if isinstance(level, int):
        return level
    else:
        return getattr(logging, level)


def add_stream_handler(logger, level="DEBUG"):
    # logger level can block stream-handler
    stream_logging_level = _get_level_enum(level)
    if logger.level > stream_logging_level:
        logger.setLevel(stream_logging_level)

    stream_handler = logging.StreamHandler()
    set_level(stream_handler, level="debug")

    if coloredlogs is not None:
        fmt = __colored_format
    else:
        fmt = __terminal_format
    stream_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(stream_handler)


def set_level(logger, level="debug"):
    """Set the log level of a logger from a string.

    This is useful in combination with command line arguments."""

    if "debug" == level.lower():
        logger.setLevel(logging.DEBUG)
    elif "info" == level.lower():
        logger.setLevel(logging.INFO)
    elif "warning" == level.lower() or "warn" == level.lower():
        logger.setLevel(logging.WARNING)
    elif "error" == level.lower():
        logger.setLevel(logging.ERROR)
    elif "critical" == level.lower():
        logger.setLevel(logging.CRITICAL)
    elif "disable" == level.lower():
        logger.setLevel(logging.CRITICAL + 1)
    else:
        try:
            logger.setLevel(level)
        except ValueError:
            logger.warning('unsupported level "{}"'.format(level))
