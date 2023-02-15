import time
import logging
import settings
import hookup

from datetime import datetime

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("sdgindexer-loop")

next = 0
useemtpy = 1

# next chunk determines whether a full index rebuild or only keyword updates should be considered. 
nextChunk = datetime.fromtimestamp(0)
chunkTime = nextChunk

while True:
    logger.info("start iteration")

    if next == 0 and useemtpy == 1: 
        nextChunk = datetime.now()

        # twice a day we run a full index rebuild, to include new publications
        # FIXME replace this logic with an update indexer that uses the recent objects smartly
        if nextChunk.hour < 2 or nextChunk.hour == 12:
            nextChunk = datetime.fromtimestamp(0)

    try:
        next = hookup.run(next, useemtpy, chunkTime)
    except:
        logger.exception('Unhandled exception')
    
    if next == 0: 
        useemtpy = -1 * useemtpy + 1
        if useemtpy == 1:
            chunkTime = nextChunk

    # implicit timing    
    logger.info("finish iteration") 
    time.sleep(settings.BATCH_INTERVAL)
