from functools import wraps

import jwt
from flask import request, jsonify


def token_auth(pub_key):
    def token_auth(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            if 'key' in request.headers:
                token = request.headers['key']
            if not token:
                return jsonify({'message': 'a valid token is missing'})
            try:
                data = jwt.decode(token, pub_key)
            except:
                return jsonify({'message': 'token is invalid'})
            return f(*args, **kwargs)

        return decorator
    return token_auth
