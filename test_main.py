# Examples how to RUN:
# (BEFORE RUNNING TESTS!): Activate source of virtualenv: source venv/bin/activate
# python -m pytest test_main.py
# python -m pytest test_main.py  -v
# python -m pytest test_main.py  -vv
# python -m pytest test_main.py  -v --skipslow
# python -m pytest test_main.py -v --log-cli-level=DEBUG

# "pip install pytest-cov" (This plugin produces coverage reports) for:
#  python -m pytest --cov=. --cov-branch -v test_main.py
# --------------------------------------------------
# ----
import json
from main import app
from environs import Env
import pytest

client = app.test_client()

env = Env()
env.read_env('.env')  # read .env file, if it exists
TEST_TOKEN: str = env("TEST_TOKEN")

@pytest.mark.parametrize(
    "params",
    [
        # This is just an example how to pass parameters inside
        pytest.param([1, 'asd', 3], id="Test get_vertices 1"),
        pytest.param([[1, 23], 'asd', {'key': 23}], id="Test get_vertices 2")
    ],
)
def test_get_trans(capsys, caplog, params):
    print('AAAA')
    print(params)
    print('BBB')
    response = client.get('/get_trans',
                          headers={
                              'key': TEST_TOKEN})
    print(response.data)
    assert response.status_code == 200
    assert isinstance(json.loads(response.data.decode('utf-8'))['results'], list)


@pytest.mark.parametrize(
    "params",
    [
        pytest.param([], id="Test my_bal method")
    ],
)
def test_my_bal(capsys, caplog, params):
    response = client.get('/my_bal',
                          # data=json.dumps({'email': 'dmitryhse@gmail.com', 'password': '12'}),
                          # content_type='multipart/form-data',
                          headers={
                              'key': TEST_TOKEN})
    print(response.data)
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {
        "aed_amt": 30.0,
        "eur_amt": 10.0,
        "usd_amt": 20.0}


@pytest.mark.parametrize(
    "params",
    [
        pytest.param([], id="Test own_transfer method")
    ],
)
def test_own_transfer(capsys, caplog, params):
    response = client.post('/own_transfer',
                           query_string={'curr_from': 'usd',
                                         'curr_to': 'aed', 'amount': 1},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    print(response.data)
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {"message": "Success"}

    # Transfer it back. Important: will work until 1USD=3.67AED
    response = client.post('/own_transfer',
                           query_string={'curr_from': 'aed',
                                         'curr_to': 'usd', 'amount': 3.67},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    print(response.data)
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {"message": "Success"}


@pytest.mark.parametrize(
    "params",
    [
        pytest.param([], id="Test topup and do_transaction methods")
    ],
)
def test_topup_and_transaction(capsys, caplog, params):
    response = client.post('/topup',
                           query_string={'currency': 'aed', 'amount': 10},
                           # content_type='multipart/form-data',
                           headers={
                               'key': TEST_TOKEN})
    print(response.data)
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
    print(response.data)
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')
                      ) == {"message": "Transaction made!"}


@pytest.mark.parametrize(
    "params",
    [
        pytest.param([], id="Test main auth method")
    ],
)
def test_main_new(capsys, caplog, params):
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


@pytest.mark.parametrize(
    "params",
    [
        pytest.param([], id="Test main sign-up method")
    ],
)
def test_main(capsys, caplog, params):
    response = client.post('/',
                           content_type='multipart/form-data',
                           data={'method': 'sign-up', 'email': 'dmitryhse@gmail.com',
                                 'password': 'fake', 'confirm': 'fake'},
                           headers={
                               'key': TEST_TOKEN}
                           )
    assert response.status_code == 400
    assert 'Email: User alredy exists!' in str(response.data)
