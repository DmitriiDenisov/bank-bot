# test main.py
import json
from main import app
from environs import Env
import unittest

client = app.test_client()

env = Env()
env.read_env('.env')  # read .env file, if it exists
TEST_TOKEN = env("TEST_TOKEN")


def test_get_trans():
    response = client.get('/get_trans',
                          headers={
                              'key': TEST_TOKEN})
    assert response.status_code == 200
    assert type(json.loads(response.data.decode('utf-8'))
                ['results']) == type(list())


def test_my_bal():
    response = client.get('/my_bal',
                          # data=json.dumps({'email': 'dmitryhse@gmail.com', 'password': '12'}),
                          # content_type='multipart/form-data',
                          headers={
                              'key': TEST_TOKEN})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {
        "aed_amt": 30.0,
        "eur_amt": 10.0,
        "usd_amt": 20.0}


def test_own_transfer():
    response = client.post('/own_transfer',
                           query_string={'curr_from': 'usd',
                                         'curr_to': 'aed', 'amount': 1},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {"message": "Success"}

    # Transfer it back. Important: will work until 1USD=3.67AED
    response = client.post('/own_transfer',
                           query_string={'curr_from': 'aed',
                                         'curr_to': 'usd', 'amount': 3.67},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {"message": "Success"}


def test_topup_and_transaction():
    response = client.post('/topup',
                           query_string={'currency': 'aed', 'amount': 10},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')
                      ) == {"message": "TopUp successful!"}

    # Also transact this amount to another test account just to revert TopUp back so other tests will run successfully
    response = client.post('/do_transaction',
                           query_string={'customer_id_to': 33,
                                         'amount': 10, 'currency': 'aed'},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')
                      ) == {"message": "Transaction made!"}


def test_main_new():
    response = client.post('/',
                           content_type='multipart/form-data',
                           data={'method': 'auth', 'email': 'dmitryhse@gmail.com',
                                 'password': 'it_is_fake_password'},
                           headers={
                               'key': TEST_TOKEN}
                           )
    # resp['method'] == 'auth'
    assert response.status_code == 401
    assert 'Invalid Credentials. Please try again.' in str(response.data)


def test_main():
    response = client.post('/',
                           content_type='multipart/form-data',
                           data={'method': 'sign-up', 'email': 'dmitryhse@gmail.com',
                                 'password': 'fake', 'confirm': 'fake'},
                           headers={
                               'key': TEST_TOKEN}
                           )
    assert response.status_code == 400
    assert 'Email: User alredy exists!' in str(response.data)
