# Previous imports remain...
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, request, abort
from marshmallow import Schema, fields, ValidationError
from base import Session
from models.balances import Balance
from models.customer import Customer
from datetime import date

session = Session()

app = Flask(__name__)


class TaskParamsSchema(Schema):
    first_name = fields.Str(required=True)
    second_name = fields.Str(required=True)
    nick = fields.Str(required=True)
    join_date = fields.Date(required=True)


@app.route('/me', methods=['GET'])
def get_me():
    # custs = session.query(Customer).filter(Customer.first_name == 'Dmitry')
    custs = session.query(Customer).filter(Customer.id == 7)
    results = [
        {
            "first_name": cust.first_name,
            "second_name": cust.second_name,
            "join_date": cust.join_date
        } for cust in custs]

    return {"count": len(results), "custs": results}


@app.route('/custs', methods=['GET'])
def get_all_custs():
    # custs = session.query(Customer).filter(Customer.first_name == 'Dmitry')
    custs = session.query(Customer)
    results = [
        {
            "first_name": cust.first_name,
            "second_name": cust.second_name,
            "join_date": cust.join_date
        } for cust in custs]

    return {"count": len(results), "custs": results}


@app.route('/add_new_user', methods=['POST'])
def new_customer():
    try:
        params = TaskParamsSchema().loads(request.data.decode("utf-8"))
    except ValidationError:
        return abort(400)

    new_user = Customer(params['first_name'], params['second_name'], params['nick'], params['join_date'])
    new_bal = Balance(new_user, 101, 0, 0)
    new_user.bal = new_bal

    session.add_all([new_user])
    session.commit()

    return {'success': True}


@app.route('/delete_user', methods=['POST'])
def del_cust():
    q = request.data
    new_user = Customer('Postamn', 'postmanov', '@post', date(2020, 10, 11))
    new_bal = Balance(new_user, 0, 0, 0)
    new_user.bal = new_bal

    session.add_all([new_user])
    session.commit()

    return {'success': True}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
