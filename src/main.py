import time
import logging
import settings
import hookup

import pika
import json

from datetime import datetime

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("sdgindexer-loop")

nextChunk = datetime.fromtimestamp(0)

def indexEveryThing(nextChunk):
    next = 0
    useemtpy = 1

    # next chunk determines whether a full index rebuild or only keyword updates should be considered. 
    while True:
        logger.info("start iteration")

        chunkTime = nextChunk

        if next == 0 and useemtpy == 1: 
            nextChunk = datetime.now()

        try:
            next = hookup.run(next, useemtpy, chunkTime)
        except:
            logger.exception('Unhandled exception')
        
        if next == 0: 
            useemtpy = -1 * useemtpy + 1
            if useemtpy == 1:
                return nextChunk

        # implicit timing    
        logger.info("finish iteration") 
        time.sleep(settings.BATCH_INTERVAL)


def mqCallback(ch, method, properties, body):
    mqKey = method.routing_key
    mqPayload = json.loads(body)
    
    logger.info(f"changed indices at {body}")

    nextChunk = indexEveryThing(nextChunk)

# The main codeblock

# should we run a full index on first start?
# nextChunk = indexEveryThing(nextChunk)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.MQ_HOST))

channel = connection.channel()

channel.exchange_declare(exchange=settings.MQ_EXCHANGE, exchange_type='topic')

result = channel.queue_declare('indexerqueue', exclusive=False)
queue_name = result.method.queue

binding_keys = settings.MQ_BINDKEYS

for binding_key in binding_keys:
    channel.queue_bind(
        exchange=settings.MQ_EXCHANGE, 
        queue=queue_name, 
        routing_key=binding_key)

channel.basic_consume(
    queue=queue_name, on_message_callback=mqCallback, auto_ack=True)

channel.start_consuming()
