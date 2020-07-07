# coding=utf-8

# 1 - imports

from sqlalchemy_tutorial.models.balances import Balance
from sqlalchemy_tutorial.base import Base, engine, Session

# 2 - generate database schema
Base.metadata.create_all(engine)

# 3 - create a new session
session = Session()

session.query(Balance).filter(Balance.customer_id == 28).update(
    {"aed_bal": (Balance.aed_bal + 1), "eur_bal": (Balance.eur_bal + 2)})
# session.commit()


# 10 - commit and close session
session.commit()
session.close()
