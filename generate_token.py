import datetime
import uuid
from base import session
import jwt

from hash_password import get_hashed_password
from models.Passwords import Password
from models.balances import Balance
from models.customer import Customer

with open('credentials/private_key') as f:
    private_key = ''.join(f.readlines())

with open('credentials/public_key') as f:
    public_key = f.readline()


def add_user(user_email, user_pass):
    hashed_pass = get_hashed_password(user_pass)
    # ADD to DB new customer
    new_cut = Customer('New_user', 'flask', '@test', datetime.date(2020, 7, 19))
    # ADD new bal to user
    new_bal = Balance(new_cut, 0, 0, 0)
    # ADD new password
    new_pass = Password(new_cut, user_email, hashed_pass)
    # SAVE token with uuid into DB
    session.add_all([new_cut])
    session.flush()
    session.commit()


def get_token(user_email):
    token = jwt.encode({'user_email': user_email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
                        'iat': datetime.datetime.utcnow()}, headers={'kid': uuid.uuid4().hex},
                       key=private_key,
                       algorithm='RS256')
    return token
