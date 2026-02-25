import logging

from config import paths


def setup_logger(log_dir: str = "~/.sentinel") -> logging.Logger:
    """Configures the background logger for the Sentinel engine."""
    paths.BASE_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SentinelEngine")
    logger.setLevel(logging.INFO)

    # Prevent adding duplicate handlers if re-initialized
    if not logger.handlers:
        file_handler = logging.FileHandler(paths.LOG_FILE)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
