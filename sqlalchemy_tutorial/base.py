# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

with open("../credentials") as cred:
    url = cred.readline()


engine = create_engine(url)
Session = sessionmaker(bind=engine)

Base = declarative_base()
