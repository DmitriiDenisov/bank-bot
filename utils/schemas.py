from flask import jsonify
from wtforms import PasswordField, validators, Form, StringField, DateField
from wtforms.fields.html5 import EmailField
import wtforms_json
from wtforms.validators import EqualTo, InputRequired, ValidationError

from models.Passwords import Password
from models.customer import Customer
from utils.base import session

wtforms_json.init()


class SignUpSchema(Form):
    # We have also added two methods to this class called validate_email(). When you add any
    # methods that match the pattern validate_<field_name>, WTForms takes those as custom validators and invokes them
    # in addition to the stock validators.
    email = EmailField('email', [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=20)])
    password = PasswordField('password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('confirm')

    def validate_email(self, email):
        if session.query(Password).filter(Password.user_email == email.data).first():
            raise ValidationError('User alredy exists!')


class AuthSchemaForm(Form):
    username = EmailField('username', [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=20)])
    password = PasswordField('password', [validators.DataRequired()])


class TaskParamsSchema(Form):
    first_name = StringField('first_name', [validators.DataRequired()])
    second_name = StringField('second_name', [validators.DataRequired()])
    nick = StringField('nick', [validators.DataRequired()])
    join_date = DateField('join_date', [validators.DataRequired()])
    token = StringField('token')


class ForgotPass(Form):
    email = EmailField('email', [validators.DataRequired()])


class ResetPass(Form):
    password1 = PasswordField('password1', [InputRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('password2')
