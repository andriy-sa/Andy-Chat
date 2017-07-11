from flask import Blueprint, request, jsonify
from forms.user import UserCreateForm
from models.user import User

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

    return jsonify(user.serialize()), 200
