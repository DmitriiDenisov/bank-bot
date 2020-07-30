import datetime
import uuid
import jwt

from models.Token import Token
from utils.base import session
from utils.constants import PRIVATE_KEY, ALG


def get_token(user_email: str, customer_id: int, temp_access: bool):
    """
    Function generates jwt token. Payload - user_email, creation date of token and exp date
    Header - uuid of Token
    Signature - encoded with private key signature
    :param user_email: email of customer/user
    :return: token
    """
    creation_date = datetime.datetime.utcnow()
    exp_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    token_uuid = uuid.uuid4().hex

    token = jwt.encode(payload={'user_email': user_email, 'customer_id': customer_id, 'temp_access': temp_access,
                                'exp': exp_date,
                                'iat': creation_date}, headers={'kid': token_uuid},
                       key=PRIVATE_KEY,
                       algorithm=ALG)
    # Add token to DB
    new_token = Token(customer_id, token_uuid, creation_date, exp_date)
    session.add_all([new_token])
    session.flush()
    session.commit()
    return token
