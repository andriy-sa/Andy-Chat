from flask import jsonify, g
from jwt import InvalidTokenError
from flask_jwt import JWT, JWTError
from functools import wraps

jwt = JWT()


def get_jwt_user():
    try:
        token = jwt.request_callback()
        payload = jwt.jwt_decode_callback(token)
        user = jwt.identity_callback(payload)
    except InvalidTokenError:
        user = None
    except JWTError:
        user = None

    return user


def login_required():
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if g.user is None or not g.user['is_active']:
                return jsonify({'message': "Forbidden"}), 403

            return func(*args, **kwargs)

        return decorated_view

    return decorator
