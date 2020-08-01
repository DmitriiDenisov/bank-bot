from flask import Flask, request, abort, url_for
from flask import jsonify, make_response

from models.transactions import Transaction
from utils.constants import PRIVATE_KEY
from utils.schemas import TaskParamsSchema, AuthSchemaForm, SignUpSchema, ForgotPass, ResetPass
from utils.add_user import add_user
from utils.base import session
from crypto_utils.generate_token import get_token
from crypto_utils.hash_password import check_password, get_hashed_password
from models.Passwords import Password
from models.balances import Balance
from models.customer import Customer
from datetime import date
from flask import redirect, url_for, render_template
from utils.token_auth import token_auth, TokenData

# Define Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
# app.config['PUBLIC_KEY'] = PUBLIC_KEY
app.config['PRIVATE_KEY'] = PRIVATE_KEY


# Sign_up method. It receives login-pass, checks that this user does not exist, if exists then add it to DB and create token for him
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        form = SignUpSchema(request.form)
        # form.password
        if not form.validate():
            if form.errors.get('password'):
                return jsonify({'resp': form.errors.get('password')[0]})
            else:
                return jsonify({'resp': form.errors.get('email')[0]})
                # return abort(400)

        if session.query(Password).filter(Password.user_email == form.email.data).first():
            return jsonify({'resp': 'User alredy exists!'})
        else:
            customer_id = add_user(form.email.data, form.password.data)
            token = get_token(form.email.data, customer_id, form.password.data, temp_access=False)
            return jsonify({'resp': token.decode('utf-8')})
    return render_template('register.html', title='Register')


# Auth method. Called if previous token has expired. Checks that user exist in DB and password matches and creates new token
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    error = None
    if request.method == 'POST':
        form = AuthSchemaForm(request.form)
        if not form.validate():
            # return abort(400)
            error = 'Username does not match email pattern'
            return render_template('login.html', error=error)
        cust_pass = session.query(Password).filter((Password.user_email == form.username.data)).first()
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
                                temp_access=False).decode('utf-8')})
    return render_template('login.html', error=error)


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        form = ForgotPass(request.form)
        if not form.validate():
            return jsonify({'message': 'Not valid email!'})

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


@app.route('/reset_with_token', methods=['GET', 'POST'])
@token_auth(app.config['PRIVATE_KEY'])
def reset_with_token(data: TokenData):
    if request.method == 'POST':
        form = ResetPass(request.form)
        if not form.validate():
            return jsonify({'resp': form.errors.get('password1')[0]})

        hashed_pass = get_hashed_password(form.password1.data)
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
