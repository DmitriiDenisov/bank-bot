# coding=utf-8

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
# from models.customer import Customer
from utils.base import Base


class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    # Relationship means that python object will have separate field which is connected to value from another table
    # backref means that in Customer
    customer = relationship("Customer", backref=backref("bal", uselist=False))
    usd_bal = Column(Float)
    eur_bal = Column(Float)
    aed_bal = Column(Float)

    def __init__(self, customer, usd_bal, eur_bal, aed_bal):
        self.customer = customer
        self.usd_bal = usd_bal
        self.eur_bal = eur_bal
        self.aed_bal = aed_bal
