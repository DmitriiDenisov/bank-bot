# coding=utf-8

# 1 - imports
from datetime import date

from sqlalchemy_tutorial.models.balances import Balance
from sqlalchemy_tutorial.base import Base, engine, Session
from sqlalchemy_tutorial.models.customer import Customer

# 2 - generate database schema
from sqlalchemy_tutorial.models.transactions import Transaction

Base.metadata.create_all(engine)

# 3 - create a new session
session = Session()

# Add new users, their balances and new transaction
new_user1 = Customer('test', '5', '@test',  date(2002, 10, 11))
new_user2 = Customer('test', '6', '@test',  date(2002, 10, 11))
new_bal1 = Balance(new_user1, 0, 0, 0)
new_bal2 = Balance(new_user2, 0, 0, 0)
# new_user.bal = new_bal
new_trans = Transaction(5, 9, 27, 0, 0)

# 9 - persists data
session.add_all([new_user1, new_user2, new_trans])
# session.add(new_trans)

# 10 - commit and close session
session.commit()
session.close()