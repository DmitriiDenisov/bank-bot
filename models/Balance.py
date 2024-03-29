# coding=utf-8

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.Customer import Customer
from utils.base import Base


class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    # Relationship means that python object will have separate field which is connected to value from another table
    # backref means that in Customer
    customer = relationship("Customer", backref=backref("bal", uselist=False), foreign_keys=[customer_id])
    usd_amt = Column(Float)
    eur_amt = Column(Float)
    aed_amt = Column(Float)