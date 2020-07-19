from marshmallow import Schema, fields, ValidationError


# Schemas for Flask API, it allows to automatically check if required parameters are passed and they have correct type

class TaskParamsSchema(Schema):
    first_name = fields.Str(required=True)
    second_name = fields.Str(required=True)
    nick = fields.Str(required=True)
    join_date = fields.Date(required=True)
    token = fields.Str(required=True)


class AuthSignSchema(Schema):
    user_email = fields.Str(required=True)
    user_pass = fields.Str(required=True)
