from orator import Model
from app import bcrypt


class User(Model):
    __fillable__ = ['first_name', 'last_name', 'email', 'avatar', 'is_active']
    __hidden__ = ['password']

    @staticmethod
    def make_password(password):
        hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return hash

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


def identity(payload):
    user_id = payload['identity']
    user = User.find(user_id)
    if user:
        return user.serialize()

    return None


def authenticate(email, password):
    user = User.where('email', email).first()
    if user and user.check_password(password):
        return user
    return False
