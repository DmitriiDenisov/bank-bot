# coding=utf-8

from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import relationship

from sqlalchemy_tutorial.base import Base


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    second_name = Column(String)
    nickname_telegram = Column(String)
    join_date = Column(Date)

    # balance = relationship("Balance", backref="customer", uselist=False)
    # trans = relationship("Transaction", uselist=True)
