import logging

from app.core.config import settings


def setup_logging():
    """
    Configures the application-wide logger.
    """
    logging.basicConfig(level=settings.log_level.upper(), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return logging.getLogger("taskhub")


logger = setup_logging()
