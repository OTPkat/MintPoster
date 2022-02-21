import logging


def create_logger() -> logging.Logger:

    """
    Creates logger with a stdout handler and a file handler

    :param service_name: name of the application, use to name archive_logger.log file.

    :return: the configured logger
    """

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Set formatter
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
