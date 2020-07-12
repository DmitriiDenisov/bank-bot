# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    with open("credentials/credentials_db") as cred:
        url = cred.readline()
except:
    pass

engine = create_engine(url)
Session = sessionmaker(bind=engine)
# 2. Extract a session
session = Session()
Base = declarative_base()
