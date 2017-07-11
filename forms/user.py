import wtforms as form
from flask_wtf import Form
from wtforms import validators
from models.user import User


class UserCreateForm(Form):
    email = form.StringField('email', validators=[
        validators.DataRequired(),
        validators.Email(),
        validators.Length(max=255)
    ])
    first_name = form.StringField('first_name', validators=[
        validators.DataRequired(),
        validators.Length(max=255)
    ])
    last_name = form.StringField('last_name', validators=[
        validators.DataRequired(),
        validators.Length(max=255)
    ])
    avatar = form.StringField('avatar', validators=[
        validators.Length(max=255)
    ])
    password = form.PasswordField('password', validators=[
        validators.DataRequired(),
        validators.Length(min=6, max=16)
    ])

    password_confirm = form.PasswordField('password_confirm')

    def validate_email(self, field):
        user = User.where('email', field.data).first()
        if user:
            raise form.ValidationError(message='User with this email already exist')

    def validate_password(self, field):
            if self.password_confirm.data != field.data:
                raise form.ValidationError(message='Password does not match the confirm password')

