from jwt import InvalidTokenError
from flask_jwt import JWT, JWTError

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
