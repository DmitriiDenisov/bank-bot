# coding=utf-8

from sqlalchemy import Column, String, Integer, Date

from utils.base import Base


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    second_name = Column(String)
    nickname_telegram = Column(String)
    join_date = Column(Date)

    # balance = relationship("Balance", backref="customer", uselist=False)
    # trans = relationship("Transaction", uselist=True)
    def __init__(self, first_name, second_name, nickname_telegram, join_date):
        self.first_name = first_name
        self.second_name = second_name
        self.nickname_telegram = nickname_telegram
        self.join_date = join_date
