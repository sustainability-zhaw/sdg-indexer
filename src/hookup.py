import settings
import logging

# logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level='DEBUG')

logger = logging.getLogger("sdgindexer")

def run():
    logger.debug("run service function")
    logger.debug(f"DB_HOST: {settings.DB_HOST}")
    logger.debug(f"Batch Size: {settings.BATCH_SIZE}")
    logger.debug(f"Batch Interval: {settings.BATCH_INTERVAL}")
    logger.debug(f"Log Level: {settings.LOG_LEVEL}")
