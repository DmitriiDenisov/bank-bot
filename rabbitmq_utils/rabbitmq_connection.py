import pika
from environs import Env

env = Env()
env.read_env('.env')  # read .env file, if it exists

# required variables
HOST = env("HOST_RABBIT")
USER = env("USER_RABBIT")
PASSWORD = env("PASSWORD_RABBIT")
PORT = env.int("PORT_RABBIT")
# providing a default value
enable_login = env.bool("ENABLE_LOGIN", False)  # => True


def get_rabbit_connection():
    credentials = pika.PlainCredentials(USER, PASSWORD)  # login + pass

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=HOST,  # host, in Google Cloud Internal IP
        port=PORT,  # port, usually 5672 or 15672
        credentials=credentials  # login + pass))
    ))
    channel = connection.channel()

    return channel
