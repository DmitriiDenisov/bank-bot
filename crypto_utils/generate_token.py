import datetime
import uuid
import jwt
from utils.constants import PRIVATE_KEY


def get_token(user_email: str):
    """
    Function generates jwt token. Payload - user_email, creation date of token and exp date
    Header - uuid of Token
    Signature - encoded with private key signature
    :param user_email: email of customer/user
    :return: token
    """
    token = jwt.encode({'user_email': user_email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
                        'iat': datetime.datetime.utcnow()}, headers={'kid': uuid.uuid4().hex},
                       key=PRIVATE_KEY,
                       algorithm='RS256')
    # TODO: save token to DB - tokens
    return token
