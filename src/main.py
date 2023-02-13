import time
import logging
import settings
import hookup

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("sdgindexer-loop")

next = 0
useemtpy = 1

while True:
    logger.info("start iteration")
    try:
        next = hookup.run(next, useemtpy)
    except:
        logger.exception('Unhandled exception')
    
    if next == 0: 
        useemtpy = -1 * useemtpy + 1

    # implicit timing    
    logger.info("finish iteration") 
    time.sleep(settings.BATCH_INTERVAL)
