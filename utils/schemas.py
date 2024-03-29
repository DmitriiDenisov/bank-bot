from flask import jsonify
from marshmallow import Schema, fields
from wtforms import PasswordField, validators, Form, StringField, DateField, IntegerField, FloatField
from wtforms.fields.html5 import EmailField
import wtforms_json
from wtforms.validators import EqualTo, InputRequired, ValidationError, NumberRange

from models.Password import Password
from models.Customer import Customer
from utils.base import session

wtforms_json.init()


class SignUpSchema(Form):
    # We have also added two methods to this class called validate_email(). When you add any
    # methods that match the pattern validate_<field_name>, WTForms takes those as custom validators and invokes them
    # in addition to the stock validators.
    email = EmailField('email', [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=20)])
    password = PasswordField('password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('confirm')

    # It is better to put all business logic outside (!) wtforms, but in this case it is just for example
    # how custom validators work
    def validate_email(self, email):
        if session.query(Password).filter(Password.user_email == email.data).first():
            raise ValidationError('User alredy exists!')


class AuthSchemaForm(Form):
    email = EmailField('email', [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=20)])
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


class TopUp(Form):
    amount = FloatField('amount', [validators.DataRequired(), NumberRange(min=0, max=10000000)])
    currency = StringField('currency', filters=[lambda x: x.upper()],
                           validators=[validators.DataRequired(), validators.AnyOf(['USD', 'EUR', 'AED'])])


class TransactionSchema(Form):
    customer_id_to = IntegerField('customer_id_to', [validators.DataRequired()])
    currency = StringField('currency', filters=[lambda x: x.upper()],
                           validators=[validators.DataRequired(), validators.AnyOf(['USD', 'EUR', 'AED'])])
    amount = FloatField('amount', [validators.DataRequired(),
                                   NumberRange(min=0)])

    def validate_customer_id_to(self, customer_id_to):
        if not session.query(Customer).filter(Customer.id == customer_id_to.data).first():
            raise ValidationError('User does not exist!')

    # time_created = fields.DateTime(required=True)


class CurrencyChangeSchema(Form):
    # filters - function that is applied before validators are checked
    # here upper() is added to make validators case non sensitive
    curr_from = StringField('curr_from', filters=[lambda x: x.upper()],
                            validators=[validators.DataRequired(), validators.AnyOf(['USD', 'EUR', 'AED'])])
    curr_to = StringField('curr_to', filters=[lambda x: x.upper()],
                          validators=[validators.DataRequired(), validators.AnyOf(['USD', 'EUR', 'AED'])])
    amount = FloatField('amount', [validators.DataRequired(),
                                   NumberRange(min=0, message='Enter amount greater than 0!')])
