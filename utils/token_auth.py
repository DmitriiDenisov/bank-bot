from collections import namedtuple
from functools import wraps
from jwt.exceptions import ExpiredSignatureError
import jwt
from flask import request, jsonify

from crypto_utils.hash_password import check_password, get_hashed_password
from models.Passwords import Password
from utils.base import session

TokenData = namedtuple('TokenData', ['user_email', 'customer_id', 'exp', 'iat', 'temp_access', 'salt'])


def token_auth(pub_key):
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
                return jsonify({'message': 'a valid token is missing'})
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
                data = jwt.decode(token, pub_key)
            except ExpiredSignatureError:
                return jsonify({'message': 'Signature has expired! Try auth method'})
            except:
                return jsonify({'message': 'token is invalid'})

            # Transfer payload to namedtuple
            data = TokenData(**data)

            # This is check only for temporary tokens for Forgot Password. Once password is changed => hash of salt
            # will change We check that 'salt' parameter in payload matches with hash(customer_id + user_pass_hash +
            # creation_date + token_uuid) Source:
            # https://security.stackexchange.com/questions/153746/one-time-jwt-token-with-jwt-id-claim
            # TODO: think
            #  about removing "if data.temp_access" because all tokens should be revoked once password is changed
            if data.temp_access:
                cust: Password = session.query(Password).filter(Password.customer_id == data.customer_id).first()
                token_uuid = jwt.get_unverified_header(token)['kid']
                if not check_password(str(data.customer_id) + cust.user_pass + str(data.iat) + token_uuid, data.salt):
                    return jsonify({'message': 'Token is invalid as you changed password'})

            if f.__name__ != 'reset_with_token' and data.temp_access:
                return jsonify({'message': 'Token does not have access to this method!'})
            return f(data, *args, **kwargs)

        return decorator

    return token_auth
