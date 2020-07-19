import datetime
from crypto_utils.hash_password import get_hashed_password
from models.Passwords import Password
from models.balances import Balance
from models.customer import Customer
from utils.base import session


def add_user(user_email, user_pass):
    hashed_pass = get_hashed_password(user_pass)
    # ADD to DB new customer
    new_cut = Customer('New_user', 'flask', '@test', datetime.date(2020, 7, 19))
    # ADD new bal to user
    new_bal = Balance(new_cut, 0, 0, 0)
    # ADD new password
    new_pass = Password(new_cut, user_email, hashed_pass)
    # add_all is similar to git add ...
    session.add_all([new_cut])
    # flush is similar to git commit ...
    session.flush()
    # commit is similar to git push ...
    session.commit()
