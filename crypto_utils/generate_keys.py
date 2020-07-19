import os

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from utils.constants import PUBLIC_EXPONENT, KEY_SIZE

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

key = rsa.generate_private_key(
    backend=crypto_default_backend(),
    public_exponent=PUBLIC_EXPONENT,
    key_size=KEY_SIZE
)
private_key = key.private_bytes(
    crypto_serialization.Encoding.PEM,
    crypto_serialization.PrivateFormat.PKCS8,
    crypto_serialization.NoEncryption())
public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH
)

with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key'), "wb") as f:
    f.write(private_key)

with open(os.path.join(PROJECT_PATH, 'credentials', 'public_key'), "wb") as f:
    f.write(public_key)
