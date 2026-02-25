"""
Logger configuration service.
"""

import logging

from config import paths


def setup_logger(log_dir: str = "~/.sentinel") -> logging.Logger:
    """Configures the background logger for the Sentinel engine.

    Args:
        log_dir (str, optional): The directory for the log file. Defaults to "~/.sentinel".

    Returns:
        logging.Logger: The configured logger instance.
    """
    paths.BASE_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SentinelEngine")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(paths.LOG_FILE)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
