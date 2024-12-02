import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a logger with the given name and level.
    Creates a console handler and sets the formatter to the logger.

    Args:
        name (str): Logger name
        level (int, optional): Logging Level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Returns the logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
