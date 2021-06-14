# coding=utf-8

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from utils.base import Base


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    customer_id_from = Column(Integer, ForeignKey('customers.id'))
    customer_id_to = Column(Integer, ForeignKey('customers.id'))

    customer_from = relationship("Customer", foreign_keys=[customer_id_from], backref="trans_from")
    customer_to = relationship("Customer", foreign_keys=[customer_id_to], backref="trans_to")

    usd_amt = Column(Float)
    eur_amt = Column(Float)
    aed_amt = Column(Float)

