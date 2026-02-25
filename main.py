import logging
import sys

from config import paths
from monitor.app import run_application


def setup_main_logging():
    """Configures global logging for the Sentinel process."""
    paths.BASE_DIR.mkdir(parents=True, exist_ok=True)
    log_file = paths.BASE_DIR / "sentinel_main.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("SentinelMain")


def main():
    """
    Sentinel - Adaptive Streaming Multivariate Statistical Monitoring System
    Main Entry Point
    """
    logger = setup_main_logging()
    logger.info("==================================================")
    logger.info("Starting Sentinel Application Pipeline...")
    logger.info("==================================================")

    try:
        run_application()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt. Shutting down gracefully.")
    except Exception as e:
        logger.error(f"Sentinel encountered a fatal crash: {e}", exc_info=True)
    finally:
        logger.info("Sentinel process terminated.")


if __name__ == "__main__":
    main()
