import logging
from logger import get_logger


def test_logger_creation():
    logger = get_logger("test")
    assert logger.name == "test"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert (
        logger.handlers[0].formatter._fmt
        == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
