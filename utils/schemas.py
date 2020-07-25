from wtforms import PasswordField, validators, Form, StringField, DateField
from wtforms.fields.html5 import EmailField
import wtforms_json

wtforms_json.init()


class SignUpSchema(Form):
    username = EmailField('username', [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=20)])
    password = PasswordField('password', [validators.DataRequired()])


class AuthSchemaForm(Form):
    username = EmailField('username', [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=20)])
    password = PasswordField('password', [validators.DataRequired()])


class TaskParamsSchema(Form):
    first_name = StringField('first_name', [validators.DataRequired()])
    second_name = StringField('second_name', [validators.DataRequired()])
    nick = StringField('nick', [validators.DataRequired()])
    join_date = DateField('join_date', [validators.DataRequired()])
    token = StringField('token')
