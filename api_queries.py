from flask import Flask, request, abort, url_for
from flask import jsonify, make_response

from models.transactions import Transaction
from utils.constants import PRIVATE_KEY
from utils.schemas import TaskParamsSchema, AuthSchemaForm, SignUpSchema, ForgotPass
from utils.add_user import add_user
from utils.base import session
from crypto_utils.generate_token import get_token
from crypto_utils.hash_password import check_password
from models.Passwords import Password
from models.balances import Balance
from models.customer import Customer
from datetime import date
from flask import redirect, url_for, render_template
from utils.token_auth import token_auth, TokenData

# Define Flask app
app = Flask(__name__, template_folder='templates')
# app.config['PUBLIC_KEY'] = PUBLIC_KEY
app.config['PRIVATE_KEY'] = PRIVATE_KEY


@app.route('/reset', methods=['GET'])
def reset():
    form = ForgotPass.from_json(request.json)
    if not form.validate():
        return abort(400)

    cust: Password = session.query(Password).filter(Password.user_email == form.username.data).first()
    if cust:
        token = get_token(cust.user_email, cust.customer_id, temp_access=True)
        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)
        return jsonify({'recover_link': recover_url})
    else:
        return jsonify({'message': 'User not found!'})


@app.route('/reset_with_token', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def reset_with_token(data: TokenData):
    return jsonify({'success': True})


@app.route('/')
def home():
    return "Hello, World!"  # return a string


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


@app.route('/login_test', methods=['GET', 'POST'])
# Route for handling the login page logic
def login_test():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    # return render_template('register.html', error=error)
    return render_template('login.html', title='Register', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html', title='Register')

# Get info about me
# token_auth decorator checks that token is valid
@app.route('/me', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def get_me(data: TokenData):
    custs = session.query(Customer).filter(Customer.id == data.customer_id)
    results = [
        {
            "first_name": cust.first_name,
            "second_name": cust.second_name,
            "join_date": cust.join_date
        } for cust in custs]

    return jsonify({"count": len(results), "custs": results})


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
        customer_id = add_user(form.username.data, form.password.data)
        token = get_token(form.username.data, customer_id, temp_access=False)
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
    return jsonify({'token': get_token(cust_pass.user_email, cust_pass.customer_id, temp_access=False).decode('utf-8')})


# Get info about all customers
@app.route('/custs', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def get_all_custs(data: TokenData):
    # custs = session.query(Customer).filter(Customer.first_name == 'Dmitry')
    custs = session.query(Customer)
    results = [
        {
            "first_name": cust.first_name,
            "second_name": cust.second_name,
            "join_date": cust.join_date
        } for cust in custs]

    return {"count": len(results), "custs": results}


# Get my all transactions
@app.route('/get_trans', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def get_trans(data: TokenData):
    transactions = session.query(Transaction).filter(
        (Transaction.customer_id_to == data.customer_id) | (Transaction.customer_id_from == data.customer_id)).all()
    results = [
        {'customer_id_from': trans.customer_id_from,
         'customer_id_to': trans.customer_id_to,
         'usd_amt': trans.usd_amt,
         'eur_amt': trans.eur_amt,
         'aed_amt': trans.aed_amt
         }
        for trans in transactions]
    return jsonify({'results': results})


# Delete customer from DB
@app.route('/delete_user', methods=['POST'])
@token_auth(app.config['PRIVATE_KEY'])
def del_cust(data: TokenData):
    return jsonify({'success': False})


if __name__ == '__main__':
    # host='0.0.0.0' allows global connections, namely http://<ip_addess>:5001
    # Or for local access: http://172.20.10.2:5001/
    app.run(debug=True, host='0.0.0.0', port=5001)
