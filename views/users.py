from flask import Blueprint, request, jsonify, g
from forms.user import UserCreateForm
from models.user import User
from app import jwt
from libraries.authentification import login_required
from .chat import connected_users
from underscore import _

user_view = Blueprint('user_view', __name__)


@user_view.route('/user', methods=['POST'])
def create():
    form = UserCreateForm.from_json(request.get_json())

    if not form.validate():
        return jsonify(form.errors), 400

    user = User()
    user.email = form.data.get('email')
    user.first_name = form.data.get('first_name')
    user.last_name = form.data.get('last_name')
    user.avatar = form.data.get('avatar', None)
    user.password = User.make_password(form.data.get('password'))
    user.save()

    access_token = jwt.jwt_encode_callback(user)

    return jsonify({'user': user.serialize(), 'access_token': access_token.decode('utf-8')}), 200


@user_view.route('/user/list', methods=['GET'])
@login_required()
def list():
    users = User.where('id', '!=', g.user['id']).get().serialize()

    for user in users:
        client = _.findWhere(connected_users, {'id': user['id']})
        user['online'] = True if client else False


    return jsonify(users), 200


@user_view.route('/user/<int:id>', methods=['GET'])
@login_required()
def user(id):
    user = User.find(id)
    if not user:
        return jsonify({}), 404

    return jsonify(user.serialize()), 200
