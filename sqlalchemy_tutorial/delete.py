# coding=utf-8

# 1 - imports
from datetime import date

from sqlalchemy_tutorial.balances import Balance
from sqlalchemy_tutorial.base import Base, engine, Session
from sqlalchemy_tutorial.customer import Customer

# 2 - generate database schema
from sqlalchemy_tutorial.transactions import Transaction

Base.metadata.create_all(engine)

# 3 - create a new session
session = Session()

session.query(Customer).filter((Customer.id >= 12) | (Customer.second_name == 'Alchemy2')).delete()

# 10 - commit and close session
session.commit()
session.close()





