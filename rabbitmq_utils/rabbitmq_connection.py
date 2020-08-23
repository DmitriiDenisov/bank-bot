import pika


def get_rabbit_connection():
    credentials = pika.PlainCredentials('publisher', 'qwerty')  # login + pass

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='35.223.179.96',  # host, in Google Cloud Internal IP
        port=5672,  # port, usually 5672 or 15672
        credentials=credentials  # login + pass))
    ))
    channel = connection.channel()

    return channel
