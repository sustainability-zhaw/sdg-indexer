import settings
import logging

def run():
    logger.debug("run service function")
    logger.debug(f"DB_HOST: {settings.DB_HOST}")
    logger.debug(f"Batch Size: {settings.BATCH_SIZE}")
    logger.debug(f"Batch Interval: {settings.BATCH_INTERVAL}")
