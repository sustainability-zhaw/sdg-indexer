# import time
# from datetime import datetime

import logging
import json
import pika

import settings
import hookup
import time

logger = logging.getLogger("sdgindexer-loop")

def consume_handler(ch, method, properties, body):
    """
    Callback for the message queue. 

    This function handles the synchroneous message handling and informs the MQ once a 
    message has been successfully handled. 
    """
    logger.info("received message")
    hookup.run(method.routing_key, json.loads(body))
    logger.info("message handled, acknowledge!")
    ch.basic_ack(method.delivery_tag)

def init_connection():
    """
    set up the connection to the message queue and register the consume handler
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.MQ_HOST,
            heartbeat=settings.MQ_HEARTBEAT,
            blocked_connection_timeout=settings.MQ_TIMEOUT
        )
    )

    logger.info("init message queue channel")
    channel = connection.channel()

    channel.exchange_declare(
        exchange=settings.MQ_EXCHANGE, 
        exchange_type='topic',
        durable=False
    )

    result = channel.queue_declare(
        settings.MQ_QUEUE, 
        exclusive=False
    )

    queue_name = result.method.queue
   
    logger.info(f"bind all keys to queue '{settings.MQ_QUEUE}' and '{queue_name}'")

    for binding_key in settings.MQ_BINDKEYS:
        channel.queue_bind(
            exchange=settings.MQ_EXCHANGE, 
            queue=queue_name, 
            routing_key=binding_key
        )

    # switch message round-robin assignment to ready processes first
    # Force service to handle one message at the time!
    channel.basic_qos(prefetch_count=1) 

    # register consuming function as callback
    channel.basic_consume(
        queue=queue_name, 
        # auto_ack=False,
        on_message_callback=consume_handler
    )

    try:
        logger.info("start consuming")
        channel.start_consuming()
    except pika.exceptions.ChannelClosedByBroker as kE:
        logger.info("channel closed by broker")   
        channel.stop_consuming()
        connection.close()
        raise pE
    except pika.exceptions.ConnectionClosedByBroker as pE:
        logger.info("challel closed by broker")   
        channel.stop_consuming()
        connection.close()
        raise pE
    except KeyboardInterrupt as pE:
        logger.info("interactive termination")   
        channel.stop_consuming()
        connection.close()
        raise pE
    
def main():
    logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

    logging.getLogger("pika").setLevel(logging.WARNING)
        
    logger.info(f"init message queue connection to host '{settings.MQ_HOST}'")

    
    while True:
        try:
            init_connection()
        except pika.exceptions.ChannelClosedByBroker:
            time.sleep(15) # wait for rabbitmq or docker to resettle
        except pika.exceptions.ConnectionClosedByBroker:
            time.sleep(35) # wait for rabbitmq to restart (approx 30 or so seconds)
        except KeyboardInterrupt:
            logger.exception("shutdown by user")
            break

        logger.info("exit service")

if __name__ == "__main__":
    main()