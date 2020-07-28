import time
import uuid

import jwt
import datetime
import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_HS256')) as f:
    private_key = ''.join(f.readlines())

token = jwt.encode({'user_email': 'xsw3@bk.ru', 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
                    'iat': datetime.datetime.utcnow()}, headers={'kid': uuid.uuid4().hex},
                   key=private_key,
                   algorithm='HS256')

# Comment in order to successfully encode and decode Token
# time.sleep(4)

# Get header from token:
header = jwt.get_unverified_header(token)

# Get payload from token:
decoded = jwt.decode(token, private_key, algorithms='HS256')

print(decoded)
