from typing import List

import requests
from flask import Flask, request, abort, url_for
from flask import jsonify, make_response
from sqlalchemy import case

from models.transactions import Transaction
from utils.constants import PRIVATE_KEY
from utils.schemas import AuthSchemaForm, SignUpSchema, ForgotPass, ResetPass, TransactionSchema, CurrencyChangeSchema
from utils.add_user import add_user
from utils.base import session
from crypto_utils.generate_token import get_token
from crypto_utils.hash_password import check_password, get_hashed_password
from models.Passwords import Password
from models.balances import Balance
from models.customer import Customer
from flask import redirect, url_for, render_template
from utils.token_auth import token_auth, TokenData

# Define Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
# app.config['PUBLIC_KEY'] = PUBLIC_KEY
app.config['PRIVATE_KEY'] = PRIVATE_KEY


# Sign_up method. It receives login-pass, checks that this user does not exist, if exists then add it to DB and
# create token for him
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        form = SignUpSchema(request.form)
        if not form.validate():
            if form.errors.get('password'):
                return jsonify({'resp': form.errors.get('password')[0]})
            elif form.errors.get('email'):
                return jsonify({'resp': form.errors.get('email')[0]})
            else:
                return jsonify({'resp': form.errors.get('email')[0]})
                # return abort(400)

        customer_id = add_user(form.email.data, form.password.data)
        token = get_token(form.email.data, customer_id, form.password.data, temp_access=False)
        return jsonify({'resp': token.decode('utf-8')})
    return render_template('register.html', title='Register')


# Auth method. Called if previous token has expired. Checks that user exist in DB and password matches and creates
# new token
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    error = None
    if request.method == 'POST':
        form = AuthSchemaForm(request.form)
        if not form.validate():
            # return abort(400)
            error = 'Username does not match email pattern'
            return render_template('login.html', error=error)
        cust_pass = session.query(Password).filter(Password.user_email == form.username.data).join(Customer,
                                                                                                   isouter=True).first()
        if not cust_pass:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
            # return make_response('Not found such user!', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
        if not check_password(form.password.data, cust_pass.user_pass):
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
            # return make_response('User password does not match!', 401,
            #                     {'WWW.Authentication': 'Basic realm: "login required"'})
        return jsonify(
            {'token': get_token(cust_pass.user_email, cust_pass.customer_id, form.password.data,
                                cust_pass.customer.access_type,
                                temp_access=False).decode('utf-8')})
    return render_template('login.html', error=error)


# Form for Forgot password. It generates one time link to method reset_with_token
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        form = ForgotPass(request.form)
        if not form.validate():
            return jsonify({'message': 'Not valid email!'})

        # Check if customer exists in Password table
        cust: Password = session.query(Password).filter(Password.user_email == form.email.data).first()
        if cust:
            token = get_token(cust.user_email, cust.customer_id, cust.user_pass, temp_access=True)
            recover_url = url_for(
                'reset_with_token',
                token=token,
                _external=True)
            return jsonify({'recover_link': recover_url})
        else:
            return jsonify({'message': 'User not found!'})
    else:
        return render_template('forgot_pass.html')


# After /forgot is called it redirects to this /reset_with_token to set new password
@app.route('/reset_with_token', methods=['GET', 'POST'])
@token_auth(app.config['PRIVATE_KEY'])
def reset_with_token(data: TokenData):
    if request.method == 'POST':
        form = ResetPass(request.form)
        if not form.validate():
            return jsonify({'resp': form.errors.get('password1')[0]})

        # get hash of new password
        hashed_pass = get_hashed_password(form.password1.data)
        # Update user's hash pass in DB
        session.query(Password).filter(Password.customer_id == data.customer_id).update({"user_pass": hashed_pass})
        session.flush()
        session.commit()

        return jsonify({'resp': 'success'})
    return render_template('reset_pass.html')


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


@app.route('/do_transaction', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def do_transaction(data: TokenData):
    params = TransactionSchema(request.args)
    if not params.validate():
        if params.errors.get('customer_id_to'):
            return abort(400, params.errors.get('customer_id_to')[0])
        abort(400, 'Not valid arguments!')
    # params = TransactionSchema().load(request.args)

    # Get parameters from args
    customer_id_to = params.customer_id_to.data
    amount = params.amount.data
    currency = f'{params.currency.data}_amt'

    # Check if customer has enough balance
    balance = session.query(Balance).filter(Balance.customer_id == data.customer_id).first()
    if getattr(balance, currency) < amount:
        return jsonify({'message': 'Not enough money on your balance!'})

    # Update balances of customers, on average below code takes 0.46 sec
    # Source: https://stackoverflow.com/questions/54365873/sqlalchemy-update-multiple-rows-in-one-transaction
    session.query(Balance).filter(Balance.customer_id.in_([data.customer_id, customer_id_to])).update({
        Balance.usd_amt: case(
            {
                data.customer_id: Balance.usd_amt - amount,
                customer_id_to: Balance.usd_amt + amount
            },
            value=Balance.customer_id)
    },
        synchronize_session=False)
    # Commented another method which first of all does Select and then inside Python changes values and then updates
    # values. On average below code takes 0.76 sec
    """
    new_bal: List[Balance] = session.query(Balance).filter(
        (Balance.customer_id == data.customer_id) | (Balance.customer_id == customer_id_to)).all()
    for bal in new_bal:
        if bal.customer_id == data.customer_id:
            setattr(bal, currency, getattr(bal, currency) - amount)
        else:
            setattr(bal, currency, getattr(bal, currency) + amount)
    """

    # Create transaction and add it to Transactions table
    new_transaction = Transaction(data.customer_id, customer_id_to, **{currency: amount})
    session.add_all([new_transaction])
    session.commit()
    return jsonify({'message': 'Transaction made!'})


@app.route('/own_transfer', methods=['GET'])
@token_auth(app.config['PRIVATE_KEY'])
def own_transfer(data: TokenData):
    # Get params
    params = CurrencyChangeSchema(request.args)
    if not params.validate():
        return abort(400, 'Wrong parameters!')

    # Get rate for given pair of currencies
    response = requests.get('http://localhost:5000/get_rates',
                            params={'from': params.curr_from.data.upper(), 'to': params.curr_to.data.upper()})
    if response.status_code == 404:
        return False
    rate = response.json()['rate']
    add = round(params.amount.data * rate, 2)
    from_str = f"{params.curr_from.data.lower()}_amt"
    to_str = f"{params.curr_to.data.lower()}_amt"

    # Check if user has enough money on his balance
    cust: Balance = session.query(Balance).filter(Balance.customer_id == data.customer_id).first()
    if getattr(cust, from_str) < params.amount.data:
        return jsonify({'resp': 'Not enough money!'})

    # Update user's balance
    session.query(Balance).filter(Balance.customer_id == data.customer_id).update(
        {from_str: (getattr(Balance, from_str) - params.amount.data), to_str: (getattr(Balance, to_str) + add)})
    session.commit()
    return jsonify({'resp': 'success'})


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
@app.route('/delete_user', methods=['GET', 'POST'])
@token_auth(app.config['PRIVATE_KEY'])
def delete_user(data: TokenData):
    if not request.args.get('customer_id', type=int):
        return jsonify({'message': 'Not valid request!'})
    if data.access_type != 1:
        return jsonify({'resp': "You don't have rights for this!"})
    customer_id = request.args.get('customer_id')
    rowcount = session.query(Customer).filter(Customer.id == customer_id).delete()
    session.commit()
    if rowcount > 0:
        return jsonify({'resp': 'User removed!'})
    else:
        return jsonify({'resp': 'Not found such user!'})


if __name__ == '__main__':
    # host='0.0.0.0' allows global connections, namely http://<ip_addess>:5001
    # Or for local access: http://172.20.10.2:5001/
    app.run(debug=True, host='0.0.0.0', port=5001)
