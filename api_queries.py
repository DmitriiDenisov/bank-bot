from flask import Flask, request, abort
from marshmallow import ValidationError

from utils.constants import PUBLIC_KEY, PRIVATE_KEY
from utils.schemas import TaskParamsSchema, AuthSignSchema
from utils.add_user import add_user
from utils.base import session
from crypto_utils.generate_token import get_token
from crypto_utils.hash_password import check_password
from models.Passwords import Password
from models.balances import Balance
from models.customer import Customer
from datetime import date

from utils.token_auth import token_auth

# Define Flask app
app = Flask(__name__)
app.config['PUBLIC_KEY'] = PUBLIC_KEY
app.config['PRIVATE_KEY'] = PRIVATE_KEY


# Get info about me
# token_auth decorator checks that token is valid
@app.route('/me', methods=['GET'])
@token_auth(app.config['PUBLIC_KEY'])
def get_me():
    custs = session.query(Customer).filter(Customer.id == 7)
    results = [
        {
            "first_name": cust.first_name,
            "second_name": cust.second_name,
            "join_date": cust.join_date
        } for cust in custs]

    return {"count": len(results), "custs": results}


# Sign_up method. It receives login-pass, checks that this user does not exist, if exists then add it to DB and create token for him
@app.route('/sign_up', methods=['POST'])
def sign_up():
    try:
        params = AuthSignSchema().loads(request.data.decode("utf-8"))
    except ValidationError:
        return abort(400)

    if session.query(Password).filter(Password.user_email == params['user_email']).first():
        return {'resp': 'User alredy exists!'}
    else:
        add_user(params['user_email'], params['user_pass'])
        token = get_token(params['user_email'])
        return {'resp': token.decode('utf-8')}


# Auth method. Called if previous token has expired. Checks that user exist in DB and password matches and creates new token
@app.route('/auth', methods=['GET'])
def auth():
    try:
        params = AuthSignSchema().loads(request.data.decode("utf-8"))
    except ValidationError:
        return abort(400)

    cust_pass = session.query(Password).filter((Password.user_email == params['user_email'])).first()
    if not cust_pass:
        return {'message': 'Not found such user!'}
    if not check_password(params['user_pass'], cust_pass.user_pass):
        return {'message': 'User password does not match!'}
    return {'token': get_token(cust_pass.user_email)}


# Get info about all customers
@app.route('/custs', methods=['GET'])
@token_auth(app.config['PUBLIC_KEY'])
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


# Add new customer to DB
@app.route('/add_new_user', methods=['POST'])
@token_auth(app.config['PUBLIC_KEY'])
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


# Delete customer from DB
@app.route('/delete_user', methods=['POST'])
@token_auth
def del_cust():
    q = request.data
    new_user = Customer('Postamn', 'postmanov', '@post', date(2020, 10, 11))
    new_bal = Balance(new_user, 0, 0, 0)
    new_user.bal = new_bal

    session.add_all([new_user])
    session.commit()

    return {'success': True}


if __name__ == '__main__':
    # host='0.0.0.0' allows global connections, namely http://<ip_addess>:5001
    # Or for local access: http://172.20.10.2:5001/
    app.run(debug=True, host='0.0.0.0', port=5001)
