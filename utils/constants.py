import os
from environs import Env

env = Env()
env.read_env('.env')  # read .env file, if it exists
# required variables
URL_DB: str = env("URL_DB")
HOST_RABBIT: str = env("HOST_RABBIT")
PORT_RABBIT: int = env.int("PORT_RABBIT")
USER_RABBIT: str = env("USER_RABBIT")
PASSWORD_RABBIT: str = env("PASSWORD_RABBIT")
HOST_CURR_SERV: str = env("HOST_CURR_SERV")
PORT_CURR_SERV: int = env.int("PORT_CURR_SERV")

PROJECT_PATH: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLIC_EXPONENT: int = 65537  # only for generation private_key_RS256/public_key_RS256
KEY_SIZE: int = 2048  # only for generation private_key_RS256/public_key_RS256
ALG: str = 'HS256'  # definition of which algo we are using for encrypt.
# Either HS256 (uses one private key) or RS256 (uses pair of private/public keys).

if ALG == 'HS256':
    PRIVATE_KEY: str = env("KEY_HS256")
else:
    # Better not to remove it into env file because private key is too long
    with open(os.path.join(PROJECT_PATH, 'credentials', 'public_key_RS256')) as f:
        PUBLIC_KEY: str = f.readline()

    with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_RS256')) as f:
        PRIVATE_KEY: str = ''.join(f.readlines())
