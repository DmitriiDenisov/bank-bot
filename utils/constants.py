import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLIC_EXPONENT = 65537
KEY_SIZE = 2048

with open(os.path.join(PROJECT_PATH, 'credentials', 'public_key')) as f:
    PUBLIC_KEY = f.readline()

with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key')) as f:
    PRIVATE_KEY = ''.join(f.readlines())

with open(os.path.join(PROJECT_PATH, 'credentials', 'credentials_db')) as cred:
    URL_DB = cred.readline()
