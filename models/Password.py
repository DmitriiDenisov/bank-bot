# coding=utf-8

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.base import Base


class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    user_email = Column(String)
    user_pass = Column(String)
    customer = relationship("Customer", backref=backref("passwd", uselist=False))
