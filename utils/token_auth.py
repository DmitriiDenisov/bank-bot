from functools import wraps
from jwt.exceptions import ExpiredSignatureError
import jwt
from flask import request, jsonify


def token_auth(pub_key):
    def token_auth(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            # check if token is in headers
            if 'key' in request.headers:
                token = request.headers['key']
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
                data = jwt.decode(token, pub_key)
            except ExpiredSignatureError:
                return jsonify({'message': 'Signature has expired! Try auth method'})
            except:
                return jsonify({'message': 'token is invalid'})
            return f(data, *args, **kwargs)

        return decorator
    return token_auth
