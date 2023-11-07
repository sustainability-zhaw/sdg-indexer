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
            blocked_connection_timeout=settings.MQ_TIMEOUT,
            credentials=pika.PlainCredentials(settings.MQ_USER, settings.MQ_PASS)
        )
    )

    logger.info("init message queue channel")
    channel = connection.channel()
   
    logger.info(f"bind all keys to queue '{settings.MQ_QUEUE}' and '{settings.MQ_QUEUE}'")

    for binding_key in settings.MQ_BINDKEYS:
        channel.queue_bind(
            exchange=settings.MQ_EXCHANGE, 
            queue=settings.MQ_QUEUE, 
            routing_key=binding_key
        )

    # switch message round-robin assignment to ready processes first
    # Force service to handle one message at the time!
    channel.basic_qos(prefetch_count=1) 

    # register consuming function as callback
    channel.basic_consume(
        queue=settings.MQ_QUEUE, 
        # auto_ack=False,
        on_message_callback=consume_handler
    )

    try:
        logger.info("start consuming")
        channel.start_consuming()
    except pika.exceptions.ChannelClosedByBroker as pE:
        logger.info("channel closed by broker")   
        #channel.stop_consuming()
        connection.close()
        raise pE
    except pika.exceptions.ConnectionClosedByBroker as pE:
        logger.info("channel closed by broker")   
        #channel.stop_consuming()
        #connection.close()
        raise pE
    except pika.exceptions.StreamLostError as sE:
        logger.info("channel connection lost")   
        #channel.stop_consuming()
        #connection.close()
        raise sE
    except KeyboardInterrupt as kE:
        logger.info("interactive termination")   
        channel.stop_consuming()
        connection.close()
        raise kE
    
def main():
    logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

    logging.getLogger("pika").setLevel(logging.WARNING)
        
    logger.info(f"init message queue connection to host '{settings.MQ_HOST}'")

    
    while True:
        try:
            init_connection()
        except pika.exceptions.StreamLostError as sE:
            logger.error(f"stream lost error {sE}")
            # reconnect right away
        except pika.exceptions.ChannelClosedByBroker:
            logger.error(f"channel close error {pE}")
            time.sleep(15) # wait for rabbitmq or docker to resettle
        except pika.exceptions.ConnectionClosedByBroker:
            logger.error(f"connection close error {pE}")
            time.sleep(35) # wait for rabbitmq to restart (approx 30 or so seconds)
        except KeyboardInterrupt:
            logger.info("shutdown by user")
            break

        logger.info("exit service")

if __name__ == "__main__":
    main()