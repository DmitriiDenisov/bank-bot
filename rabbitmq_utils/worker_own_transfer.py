import json
from collections import namedtuple

from models.balances import Balance
from rabbitmq_utils.rabbitmq_connection import get_rabbit_connection
from utils.base import session

InputJson = namedtuple('InputJson', ['customer_id', 'from_str', 'to_str', 'amount_subtract', 'amount_add'])

channel = get_rabbit_connection()


def callback(ch, method, properties, body):
    data: InputJson = InputJson(**json.loads(body))
    print(" [x] Received %r" % body)
    # Update user's balance
    session.query(Balance).filter(Balance.customer_id == data.customer_id).update(
        {
            data.from_str: (getattr(Balance, data.from_str) - data.amount_subtract),
            data.to_str: (getattr(Balance, data.to_str) + data.amount_add)
        })
    session.commit()

    ch.basic_ack(
        delivery_tag=method.delivery_tag)  # Answer to RabbitMQ that all is successful => Message is marked as acknowledged


# if next row is commented => even messages are transferred to consumer_1, odd to consumer_2
# This row allows to avoid idle of consumers: once a consumer is free it receives next message
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='own_transaction',  # name of queue
                      # auto_ack=True, # True => if python crashes => do not send message back to queue
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
