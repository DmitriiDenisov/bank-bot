import datetime
from typing import Tuple

from crypto_utils.hash_password import get_hash
from models.Password import Password
from models.Balance import Balance
from models.Customer import Customer
from utils.base import session


def add_user(user_email: str, user_pass: str) -> Tuple[int, str]:
    """
    Add new user to DB
    :param user_email: str, user's email address
    :param user_pass: str, user hashed password
    :return:
    """
    hashed_pass: str = get_hash(user_pass)
    # ADD to DB new customer
    new_cust: Customer = Customer(first_name='New_user', second_name='flask_August', nickname_telegram='@test',
                                  access_type=0,
                                  join_date=datetime.datetime.utcnow())
    # ADD new bal to user
    new_bal: Balance = Balance(customer=new_cust, usd_amt=0, eur_amt=0, aed_amt=0)
    # ADD new password
    new_pass: Password = Password(customer=new_cust, user_email=user_email, user_pass=hashed_pass)
    # add_all is similar to git add ...
    session.add_all([new_cust])
    # flush is similar to git commit ...
    session.flush()
    # commit is similar to git push ...
    session.commit()

    return new_cust.id, hashed_pass
