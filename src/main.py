import time
import logging
import settings
import hookup

import pika

from datetime import datetime

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("sdgindexer-loop")

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
    queue=queue_name, on_message_callback=hookup.handler, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

connection.close()
