import datetime
import uuid
from calendar import timegm

import jwt

from crypto_utils.hash_password import get_hash
from models.Token import Token
from utils.base import session
from utils.constants import PRIVATE_KEY, ALG


def get_token(user_email: str, customer_id: int, hashed_pass: str, access_type: int = 0,
              temp_access: bool = False) -> str:
    """
    Function generates jwt token. Payload - user_email, creation date of token and exp date
    Header - uuid of Token
    Signature - encoded with private key signature
    :param access_type: int, 0 - normal access, 1 - admin
    :param customer_id: int, customer unique identifier in DB
    :param hashed_pass: str, hashed password of customer
    :param temp_access: bool, either it is token for reset or not
    :param user_email: str, email of customer/user
    :return: token: str, generated token
    """
    creation_date: datetime = datetime.datetime.utcnow()
    exp_date: datetime = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    token_uuid: str = uuid.uuid4().hex

    # 'signature' is parameter in payload equals to hash(customer_id + user_pass_hash + creation_date + token_uuid)
    # The purpose of signature is: once user changes password => hash changes and signature won't match => all tokens will be revoked
    # Source: https://security.stackexchange.com/questions/153746/one-time-jwt-token-with-jwt-id-claim
    signature: str = get_hash(str(customer_id) + hashed_pass + str(timegm(creation_date.utctimetuple())) + token_uuid)

    # 'temp_access' parameter for forgot password
    token = jwt.encode(payload={'user_email': user_email, 'customer_id': customer_id, 'access_type': access_type,
                                'temp_access': temp_access,
                                'exp': exp_date,
                                'iat': creation_date, 'signature': signature}, headers={'kid': token_uuid},
                       key=PRIVATE_KEY,
                       algorithm=ALG)
    # Add token to DB
    new_token: Token = Token(customer_id=customer_id, token_uuid=token_uuid, creation_date=creation_date,
                             exp_date=exp_date)
    session.add_all([new_token])
    session.flush()
    session.commit()
    return token
