import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLIC_EXPONENT = 65537
KEY_SIZE = 2048
ALG = 'HS256'

if ALG == 'HS256':
    with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_HS256')) as f:
        PRIVATE_KEY = ''.join(f.readlines())
else:
    with open(os.path.join(PROJECT_PATH, 'credentials', 'public_key_RS256')) as f:
        PUBLIC_KEY = f.readline()

    with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_RS256')) as f:
        PRIVATE_KEY = ''.join(f.readlines())

with open(os.path.join(PROJECT_PATH, 'credentials', 'credentials_db')) as cred:
    URL_DB = cred.readline()
