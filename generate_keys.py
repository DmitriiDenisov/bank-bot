import datetime
import time
import jwt
import uuid
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

key = rsa.generate_private_key(
    backend=crypto_default_backend(),
    public_exponent=65537,
    key_size=2048
)
private_key = key.private_bytes(
    crypto_serialization.Encoding.PEM,
    crypto_serialization.PrivateFormat.PKCS8,
    crypto_serialization.NoEncryption())
public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH
)

with open("credentials/private_key", "wb") as f:
    f.write(private_key)

with open("credentials/public_key", "wb") as f:
    f.write(public_key)


token = jwt.encode({'some': 'payload', 'user_id': 1, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
                    'iat': datetime.datetime.utcnow()}, headers={'kid': uuid.uuid4().hex},
                   key=private_key,
                   algorithm='RS256')

time.sleep(4)

# Get header from token:
header = jwt.get_unverified_header(token)

# Get payload from token:
decoded = jwt.decode(token, public_key, algorithms='RS256')
