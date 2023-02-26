import time
import logging
import settings
import hookup

import pika

from datetime import datetime

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("sdgindexer-loop")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.MQ_HOST,
                              heartbeat=settings.MQ_HEARTBEAT,
                              blocked_connection_timeout=settings.MQ_TIMEOUT))

channel = connection.channel()

channel.exchange_declare(exchange=settings.MQ_EXCHANGE, exchange_type='topic')

result = channel.queue_declare(settings.MQ_QUEUE, exclusive=False)
queue_name = result.method.queue

binding_keys = settings.MQ_BINDKEYS

for binding_key in binding_keys:
    channel.queue_bind(
        exchange=settings.MQ_EXCHANGE, 
        queue=queue_name, 
        routing_key=binding_key)

channel.basic_qos(prefetch_count=1) # switch off message round robin assignment to ready processes first

channel.basic_consume(
    queue=queue_name, on_message_callback=hookup.handler, auto_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

connection.close()
