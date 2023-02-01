import time
import logging
import settings
import hookup

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("sdgindexer-loop")

while True:
    logger.info("start iteration")
    try:
        hookup.run()
    except:
        logger.exception('Unhandled exception')
    # implicit timing
    logger.info("finish iteration") 
    time.sleep(settings.BATCH_INTERVAL)
