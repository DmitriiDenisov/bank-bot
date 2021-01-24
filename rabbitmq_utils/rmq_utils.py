import json

import pika

from utils.constants import USER_RABBIT, PASSWORD_RABBIT, HOST_RABBIT, PORT_RABBIT

credentials = pika.PlainCredentials(USER_RABBIT, PASSWORD_RABBIT)  # login + pass

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=HOST_RABBIT,  # host, in Google Cloud Internal IP
    port=PORT_RABBIT,  # port, usually 5672 or 15672
    credentials=credentials  # login + pass))
))
channel = connection.channel()


def publish_message(json_body, queue):
    channel.basic_publish(exchange='',
                          routing_key=queue,  # name of queue
                          body=json.dumps(json_body),  # message to be sent
                          properties=pika.BasicProperties(
                              delivery_mode=2,
                              # make message persistent, i.e. if RabbitMQ crashes this message is saved
                          ))
