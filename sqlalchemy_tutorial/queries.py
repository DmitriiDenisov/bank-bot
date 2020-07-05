# coding=utf-8

# 1 - imports
import pandas as pd
# from sqlalchemy_tutorial.actor import Actor
from sqlalchemy_tutorial.base import Session
# from sqlalchemy_tutorial.contact_details import ContactDetails
# from sqlalchemy_tutorial.movie import Movie
from sqlalchemy_tutorial.customer import Customer
from sqlalchemy_tutorial.balances import Balance
from sqlalchemy_tutorial.transactions import Transaction

# 2 - extract a session
session = Session()

# 3 - extract all movies

# If we don't have Foreign Keys in tables
customers = session.query(Customer, Balance).outerjoin(Balance, Customer.id == Balance.customer_id)
# movies = session.query(Movie).all()
joined = session.query(Customer).join(Balance).all()
all_bal = session.query(Balance)
all_trans = session.query(Transaction).all()

for trans in all_trans:
    pass

for bal in all_bal:
    pass

# 4 - print movies' details
print('\n### All customers:')
for customer, balance in customers:
    # print(customer.usd_bal)
    # customer.
    print(
        f'{customer.id}, {customer.first_name}, {customer.second_name}, {customer.nickname_telegram}, {customer.join_date}')
print('')

# df = pd.read_sql(Customer, query.session.bind)
# df = pd.read_sql(session.query(Customer).filter((Customer.id >= 5) & (Customer.first_name == 'Dmitry')).statement, session.bind)
df = pd.read_sql(session.query(Customer, Balance).outerjoin(Balance, Customer.id == Balance.customer_id).statement,
                 session.bind)

print(df)
