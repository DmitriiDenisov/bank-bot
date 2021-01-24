import os
from environs import Env

env = Env()
env.read_env('.env')  # read .env file, if it exists
# required variables
URL_DB = env("URL_DB")
HOST_RABBIT = env("HOST_RABBIT")
PORT_RABBIT = env.int("PORT_RABBIT")
USER_RABBIT = env("USER_RABBIT")
PASSWORD_RABBIT = env("PASSWORD_RABBIT")
HOST_CURR_SERV = env("HOST_CURR_SERV")
PORT_CURR_SERV = env.int("PORT_CURR_SERV")

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLIC_EXPONENT = 65537  # only for generation private_key_RS256/public_key_RS256
KEY_SIZE = 2048  # only for generation private_key_RS256/public_key_RS256
ALG = 'HS256'  # definition of which algo we are using for encrypt.
# Either HS256 (uses one private key) or RS256 (uses pair of private/public keys).

if ALG == 'HS256':
    # with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_HS256')) as f:
    #    PRIVATE_KEY = ''.join(f.readlines())
    PRIVATE_KEY = env("KEY_HS256")
else:
    with open(os.path.join(PROJECT_PATH, 'credentials', 'public_key_RS256')) as f:
        PUBLIC_KEY = f.readline()

    with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_RS256')) as f:
        PRIVATE_KEY = ''.join(f.readlines())

# with open(os.path.join(PROJECT_PATH, 'credentials', 'credentials_db')) as cred:
#    URL_DB = cred.readline()
