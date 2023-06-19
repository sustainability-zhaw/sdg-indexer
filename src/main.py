# import time
# from datetime import datetime

import logging
import json
import pika

import settings
import hookup

def consume_handler(ch, method, properties, body):
    """
    Callback for the message queue. 

    This function handles the synchroneous message handling and informs the MQ once a 
    message has been successfully handled. 
    """
    hookup.run(method.routing_key, json.loads(body))
    ch.basic_ack(method.delivery_tag)

def main():
    logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

    logging.getLogger("pika").setLevel(logging.WARNING)

    logger = logging.getLogger("sdgindexer-loop")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.MQ_HOST,
                                  heartbeat=settings.MQ_HEARTBEAT,
                                  blocked_connection_timeout=settings.MQ_TIMEOUT))

    channel = connection.channel()

    channel.exchange_declare(exchange=settings.MQ_EXCHANGE, exchange_type='topic')

    result = channel.queue_declare(settings.MQ_QUEUE, exclusive=False)

    queue_name = result.method.queue
   
    for binding_key in settings.MQ_BINDKEYS:
        channel.queue_bind(
            exchange=settings.MQ_EXCHANGE, 
            queue=queue_name, 
            routing_key=binding_key)

    # switch message round-robin assignment to ready processes first
    # Force service to handle one message at the time!
    channel.basic_qos(prefetch_count=1) 

    # register consuming function as callback
    channel.basic_consume(
        queue=queue_name, 
        on_message_callback=consume_handler)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()

if __name__ == "__main__":
    main()