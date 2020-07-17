import time
import uuid

import jwt
import datetime

with open('../credentials/private_key') as f:
    private_key = ''.join(f.readlines())

with open('../credentials/public_key') as f:
    public_key = f.readline()

token = jwt.encode({'user_email': 'xsw3@bk.ru', 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
                    'iat': datetime.datetime.utcnow()}, headers={'kid': uuid.uuid4().hex},
                   key=private_key,
                   algorithm='RS256')

# Comment in order to successfully encode and decode Token
time.sleep(4)

# Get header from token:
header = jwt.get_unverified_header(token)

# Get payload from token:
decoded = jwt.decode(token, public_key, algorithms='RS256')