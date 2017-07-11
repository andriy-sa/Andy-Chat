from flask import Blueprint, request, jsonify, current_app, g
from app import jwt

auth_view = Blueprint('auth_view', __name__)


@auth_view.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get(current_app.config.get('JWT_AUTH_USERNAME_KEY'), None)
    password = data.get(current_app.config.get('JWT_AUTH_PASSWORD_KEY'), None)
    criterion = [username, password, len(data) == 2]

    if not all(criterion):
        return jsonify({'message': 'Invalid credentials'}), 401

    user = jwt.authentication_callback(username, password)
    if user:
        if not user.is_active:
            return jsonify({'message': 'InActive User'}), 401

        access_token = jwt.jwt_encode_callback(user)

        return jsonify({'user': user.serialize(), 'access_token': access_token.decode('utf-8')}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@auth_view.route('/me', methods=['GET'])
def me():
    if g.user is None:
        return jsonify({'message': 'User does not exist'}), 401

    return jsonify(g.user), 200
