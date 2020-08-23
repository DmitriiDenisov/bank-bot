import json
from collections import namedtuple

from sqlalchemy import case

from models.balances import Balance
from models.transactions import Transaction
from rabbitmq_utils.rabbitmq_connection import get_rabbit_connection
from utils.base import session

InputJson = namedtuple('InputJson', ['customer_id', 'customer_id_to', 'amount', 'currency'])

channel = get_rabbit_connection()


def callback(ch, method, properties, body):
    data: InputJson = InputJson(**json.loads(body))
    print(" [x] Received %r" % body)
    # Update balances of customers, on average below code takes 0.46 sec
    # Source: https://stackoverflow.com/questions/54365873/sqlalchemy-update-multiple-rows-in-one-transaction
    bal_ = getattr(Balance, data.currency)
    session.query(Balance).filter(Balance.customer_id.in_([data.customer_id, data.customer_id_to])).update({
        bal_: case(
            {
                data.customer_id: bal_ - data.amount,  # getattr(Balance, data.currency)
                data.customer_id_to: bal_ + data.amount
            },
            value=Balance.customer_id)
    },
        synchronize_session=False)
    # Commented another method which first of all does Select and then inside Python changes values and then updates
    # values. On average below code takes 0.76 sec
    """
    new_bal: List[Balance] = session.query(Balance).filter(
        (Balance.customer_id == data.customer_id) | (Balance.customer_id == customer_id_to)).all()
    for bal in new_bal:
        if bal.customer_id == data.customer_id:
            setattr(bal, currency, getattr(bal, currency) - amount)
        else:
            setattr(bal, currency, getattr(bal, currency) + amount)
    """

    # Create transaction and add it to Transactions table
    new_transaction = Transaction(data.customer_id, data.customer_id_to, **{data.currency: data.amount})
    session.add_all([new_transaction])
    session.commit()

    ch.basic_ack(
        delivery_tag=method.delivery_tag)  # Answer to RabbitMQ that all is successful => Message is marked as acknowledged


# if next row is commented => even messages are transferred to consumer_1, odd to consumer_2
# This row allows to avoid idle of consumers: once a consumer is free it receives next message
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='transactions',  # name of queue
                      # auto_ack=True, # True => if python crashes => do not send message back to queue
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
