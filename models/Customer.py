# coding=utf-8

from sqlalchemy import Column, String, Integer, Date, DateTime

from utils.base import Base


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    second_name = Column(String)
    nickname_telegram = Column(String)
    access_type = Column(Integer)
    join_date = Column(DateTime)

    # balance = relationship("Balance", backref="customer", uselist=False)
    # trans = relationship("Transaction", uselist=True)