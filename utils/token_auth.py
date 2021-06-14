from collections import namedtuple
from typing import NamedTuple
from functools import wraps
from jwt.exceptions import ExpiredSignatureError
import jwt
from flask import request, jsonify

from crypto_utils.hash_password import check_hash
from models.Password import Password
from utils.base import session
from utils.constants import ALG


class TokenData(NamedTuple):
    user_email: str
    customer_id: int
    access_type: int
    exp: int
    iat: int
    temp_access: bool
    signature: str


def token_auth(pub_key):
    """
    Decorator for authentication method
    :param pub_key: str, public key (in case of RS256) or private key in case HS256
    :return: func
    """

    def token_auth(f):
        @wraps(f)
        def decorator(*args, **kwargs):

            # hash_pass = session.query(Password).filter(Password.user_email == data).first()

            token = None
            # check if token is in headers
            if 'key' in request.headers:
                token = request.headers['key']
            elif f.__name__ == 'reset_with_token' and 'token' in request.args:
                token = request.args['token']
            if not token:
                return jsonify({'message': 'a valid token is missing'}), 401
            # Try to decode token (only get payload, header and verify signature)
            # How does Electronic signature work:
            # 1. We have message X
            # 2. We calculate hash(x) which is called control sum
            # 3. We encrypt control sum with private key RSA, i.e. encode(hash(X))
            # 4. Receiver gets X + control sum
            # 5. Receiver decodes control sum: decode(encode(hash(X)))=hash(X)
            # 6. Receiver calculates hash(X), where X is received message
            # 7. Compare result from 6 and 7. If equal => legitimate
            try:
                # Get Payload
                data = jwt.decode(token, pub_key, algorithms=[ALG])  # options={"verify_exp": False}
            except ExpiredSignatureError:
                return jsonify({'message': 'Signature has expired! Try auth method'}), 401
            except:
                return jsonify({'message': 'token is invalid'}), 401

            # Transfer payload to namedtuple
            data = TokenData(**data)

            # This is check only for temporary tokens for Forgot Password. Once password is changed => hash of signature
            # will change. We check that 'signature' parameter in payload matches with hash(customer_id + user_pass_hash +
            # creation_date + token_uuid) Source:
            # https://security.stackexchange.com/questions/153746/one-time-jwt-token-with-jwt-id-claim
            if data.temp_access:
                cust: Password = session.query(Password).filter(Password.customer_id == data.customer_id).first()
                token_uuid = jwt.get_unverified_header(token)['kid']
                if not check_hash(str(data.customer_id) + cust.user_pass + str(data.iat) + token_uuid, data.signature):
                    return jsonify({'message': 'Token is invalid as you changed password'}), 401

            if f.__name__ != 'reset_with_token' and data.temp_access:
                return jsonify({'message': 'Token does not have access to this method!'}), 401
            return f(data, *args, **kwargs)

        return decorator

    return token_auth
