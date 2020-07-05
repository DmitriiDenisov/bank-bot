# coding=utf-8

from sqlalchemy import Column, String, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, backref

from sqlalchemy_tutorial.base import Base


class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    # customer = relationship("Customer", foreign_keys=[customer_id])
    usd_bal = Column(Float)
    eur_bal = Column(Float)
    aed_bal = Column(Float)
