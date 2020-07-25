from flask import Flask, request, abort
from flask import jsonify, make_response

from utils.constants import PUBLIC_KEY, PRIVATE_KEY
from utils.schemas import TaskParamsSchema, AuthSchemaForm, SignUpSchema
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
    form = SignUpSchema(request.headers)
    # form.password
    if not form.validate():
        return abort(400)

    if session.query(Password).filter(Password.user_email == form.username.data).first():
        return jsonify({'resp': 'User alredy exists!'})
    else:
        add_user(form.username.data, form.password.data)
        token = get_token(form.username.data)
        return jsonify({'resp': token.decode('utf-8')})


# Auth method. Called if previous token has expired. Checks that user exist in DB and password matches and creates new token
@app.route('/auth', methods=['GET'])
def auth():
    params = AuthSchemaForm(request.headers)
    if not params.validate():
        return abort(400)

    cust_pass = session.query(Password).filter((Password.user_email == params.username.data)).first()
    if not cust_pass:
        return make_response('Not found such user!', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    if not check_password(params.password.data, cust_pass.user_pass):
        return make_response('User password does not match!', 401,
                             {'WWW.Authentication': 'Basic realm: "login required"'})
    return jsonify({'token': get_token(cust_pass.user_email).decode('utf-8')})


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
    params = TaskParamsSchema.from_json(request.json)
    if not params.validate():
        return abort(400)

    new_user = Customer(params.first_name.data, params.second_name.data, params.nick.data, params.join_date.data)
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
