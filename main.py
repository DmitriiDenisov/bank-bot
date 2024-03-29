from typing import List

import requests
from flask import Flask, request
from flask import jsonify
from models.Transaction import Transaction
from rabbitmq_utils.rmq_utils import publish_message
from utils.constants import PRIVATE_KEY, HOST_CURR_SERV, PORT_CURR_SERV
from utils.schemas import AuthSchemaForm, SignUpSchema, ForgotPass, ResetPass, TransactionSchema, CurrencyChangeSchema, \
    TopUp
from utils.add_user import add_user
from utils.base import session
from crypto_utils.generate_token import get_token
from crypto_utils.hash_password import check_hash, get_hash
from models.Password import Password
from models.Balance import Balance
from models.Customer import Customer
from flask import url_for, render_template
from utils.token_auth import token_auth, TokenData

# Define Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# app.config['PUBLIC_KEY'] = PUBLIC_KEY
app.config['PRIVATE_KEY']: str = PRIVATE_KEY


# Just ping
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'resp': 'My test 2'}), 200


@app.route('/test', methods=['GET'])
def _test():
    return render_template('dummy.html'), 200


# Get info about me
# token_auth decorator checks that token is valid
@app.route('/me', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def get_me(data: TokenData):
    custs: List[Customer] = session.query(Customer).filter(Customer.id == data.customer_id)
    results = [
        {
            "first_name": cust.first_name,
            "second_name": cust.second_name,
            "join_date": cust.join_date
        } for cust in custs]

    return jsonify({"count": len(results), "custs": results}), 200


@app.route('/topup', methods=['POST'])
@token_auth(app.config['PRIVATE_KEY'])
def topup(data: TokenData):
    params: TopUp = TopUp(request.args)
    if not params.validate():
        return jsonify({'message': 'Not valid arguments!'}), 400
    curr_str: str = f"{params.currency.data.lower()}_amt"
    session.query(Balance).filter(Balance.customer_id == data.customer_id).update(
        {curr_str: (getattr(Balance, curr_str) + params.amount.data)})
    session.flush()
    session.commit()
    return jsonify({'message': 'TopUp successful!'}), 200


def sign_up(form):
    """
    Sign_up method. It receives login-pass, checks that this user does not exist, if exists then add it to DB and
    create token for him
    """
    customer_id, hashed_pass = add_user(form.email.data, form.password.data)
    token = get_token(form.email.data, customer_id, hashed_pass, temp_access=False)
    return jsonify({'resp': token.decode('utf-8')}), 200


def auth(form):
    """
    Auth method. Called if previous token has expired. Checks that user exist in DB and password matches and creates
    new token
    """
    cust_pass: Password = session.query(Password).filter(Password.user_email == form.email.data).join(Customer,
                                                                                                      isouter=True).first()
    if not cust_pass:
        error = 'Invalid Credentials. User not found. Please try again.'
        return render_template('mainpage.html', message=error), 401
    if not check_hash(form.password.data, cust_pass.user_pass):
        error = 'Invalid Credentials. Please try again.'
        return render_template('mainpage.html', message=error), 401

    return jsonify(
        {'token': get_token(cust_pass.user_email, cust_pass.customer_id, form.password.data,
                            cust_pass.customer.access_type,
                            temp_access=False).decode('utf-8')}), 200


def forgot(form):
    """
    Form for Forgot password. It generates one time link to method reset_with_token
    """
    # Check if customer exists in Password table
    cust: Password = session.query(Password).filter(Password.user_email == form.email.data).first()
    if cust:
        token: str = get_token(cust.user_email, cust.customer_id, cust.user_pass, temp_access=True)
        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)
        return jsonify({'recover_link': recover_url}), 200
    else:
        error: str = 'User not found!'
        return render_template('mainpage.html', message=error), 401


# After /forgot is called it redirects to this /reset_with_token to set new password
@app.route('/reset_with_token', methods=['GET', 'POST'])
@token_auth(app.config['PRIVATE_KEY'])
def reset_with_token(data: TokenData):
    if request.method == 'POST':
        form: ResetPass = ResetPass(request.form)
        if not form.validate():
            return jsonify({'message': 'Not valid arguments!'}), 400

        # get hash of new password
        hashed_pass: str = get_hash(form.password1.data)
        # Update user's hash pass in DB
        session.query(Password).filter(Password.customer_id == data.customer_id).update({"user_pass": hashed_pass})
        session.flush()
        session.commit()

        return jsonify({'resp': 'success'}), 200
    return render_template('reset_pass.html'), 200


@app.route('/', methods=['GET', 'POST'])
def _main():
    if request.method == 'POST':
        resp = request.form
        if resp['method'] == 'auth':
            form: AuthSchemaForm = AuthSchemaForm(request.form)
            if not form.validate():
                error: str = 'Username does not match email pattern'
                return render_template('mainpage.html', message=error), 400
            return auth(form)
        elif resp['method'] == 'sign-up':
            form: SignUpSchema = SignUpSchema(request.form)
            if not form.validate():
                if form.errors.get('password'):
                    error: str = f'Password(s): {form.errors.get("password")[0]}'
                    return render_template('mainpage.html', message=error), 400
                elif form.errors.get('email'):
                    error: str = f'Email: {form.errors.get("email")[0]}'
                    return render_template('mainpage.html', message=error), 400
                else:
                    error: str = f'Email: {form.errors.get("email")[0]}'
                    return render_template('mainpage.html', message=error), 400
            return sign_up(form)
        else:
            form: ForgotPass = ForgotPass(request.form)
            if not form.validate():
                error: str = 'Not valid email!'
                return render_template('mainpage.html', message=error), 400
            return forgot(form)
    return render_template('mainpage.html', message=''), 200


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

    return jsonify({"count": len(results), "custs": results}), 200


@app.route('/do_transaction', methods=['POST'])
@token_auth(app.config['PRIVATE_KEY'])
def do_transaction(data: TokenData):
    params: TransactionSchema = TransactionSchema(request.args)
    if not params.validate():
        return jsonify({'message': 'Not valid arguments!'}), 400

    # Get parameters from args
    amount: float = params.amount.data
    currency: str = f'{params.currency.data.lower()}_amt'

    # Check if customer has enough balance
    balance: Balance = session.query(Balance).filter(Balance.customer_id == data.customer_id).first()
    if getattr(balance, currency) < amount:
        return jsonify({'message': 'Not enough money on your balance!'}), 400

    # Publish message to RabbitMQ:
    publish_message({'customer_id': data.customer_id,
                     'customer_id_to': params.customer_id_to.data,
                     'amount': amount,
                     'currency': currency}, queue='transactions')

    return jsonify({'message': 'Transaction made!'}), 200


@app.route('/own_transfer', methods=['POST'])
@token_auth(app.config['PRIVATE_KEY'])
def own_transfer(data: TokenData):
    # Get params
    params: CurrencyChangeSchema = CurrencyChangeSchema(request.args)
    if not params.validate():
        return jsonify({'message': 'Not valid arguments!'}), 400

    # Get rate for given pair of currencies
    response = requests.get(f'http://{HOST_CURR_SERV}:{PORT_CURR_SERV}/get_rates',
                            params={'curr_from': params.curr_from.data.upper(), 'curr_to': params.curr_to.data.upper()})
    if response.status_code == 404:
        return jsonify({'message': 'Internal currency service is down'}), 500
    rate: float = response.json()['rate']
    add: float = round(params.amount.data * rate, 2)
    from_str: str = f"{params.curr_from.data.lower()}_amt"
    to_str: str = f"{params.curr_to.data.lower()}_amt"

    # Check if user has enough money on his balance
    cust: Balance = session.query(Balance).filter(Balance.customer_id == data.customer_id).first()
    if getattr(cust, from_str) < params.amount.data:
        return jsonify({'message': 'Not enough money!'}), 400

    publish_message(json_body={'customer_id': data.customer_id,
                               'from_str': from_str,
                               'amount_subtract': params.amount.data,
                               'to_str': to_str,
                               'amount_add': add}, queue='own_transaction')

    return jsonify({'message': 'Success'}), 200


# Get my all transactions
@app.route('/get_trans', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def get_trans(data: TokenData):
    transactions: List[Transaction] = session.query(Transaction).filter(
        (Transaction.customer_id_to == data.customer_id) | (Transaction.customer_id_from == data.customer_id)).all()
    results = [
        {'customer_id_from': trans.customer_id_from,
         'customer_id_to': trans.customer_id_to,
         'usd_amt': trans.usd_amt,
         'eur_amt': trans.eur_amt,
         'aed_amt': trans.aed_amt
         }
        for trans in transactions]
    return jsonify({'results': results}), 200


# Get my balance
@app.route('/my_bal', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def my_bal(data: TokenData):
    balance: Balance = session.query(Balance).filter(Balance.customer_id == data.customer_id).first()
    results: dict = {'aed_amt': balance.aed_amt, 'usd_amt': balance.usd_amt, 'eur_amt': balance.eur_amt}
    return jsonify(results), 200


# Delete customer from DB
@app.route('/delete_user', methods=['DELETE'])
@token_auth(app.config['PRIVATE_KEY'])
def delete_user(data: TokenData):
    if not request.args.get('customer_id', type=int):
        return jsonify({'message': 'Not valid request!'}), 400
    if data.access_type != 1:
        return jsonify({'resp': "You don't have rights for this!"}), 400
    customer_id: int = request.args.get('customer_id')
    rowcount = session.query(Customer).filter(Customer.id == customer_id).delete()
    session.commit()
    if rowcount > 0:
        return jsonify({'resp': 'User removed!'}), 200
    else:
        return jsonify({'resp': 'Not found such user!'}), 400


@app.route('/docs', methods=['GET'])
def get_docs():
    return render_template('swaggerui.html'), 200


if __name__ == '__main__':
    # host='0.0.0.0' allows global connections, namely http://<ip_addess>:5001
    # Or for local access: http://172.20.10.2:5001/
    app.run(debug=True, host='0.0.0.0', port=80)
