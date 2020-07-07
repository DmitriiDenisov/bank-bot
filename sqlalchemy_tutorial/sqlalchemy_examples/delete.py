# coding=utf-8

# 1 - imports

from sqlalchemy_tutorial.base import Base, engine, Session
from sqlalchemy_tutorial.models.customer import Customer

# 2 - generate database schema

Base.metadata.create_all(engine)

# 3 - create a new session
session = Session()

session.query(Customer).filter((Customer.id >= 12) | (Customer.second_name == 'Alchemy2')).delete()

# 10 - commit and close session
session.commit()
session.close()





