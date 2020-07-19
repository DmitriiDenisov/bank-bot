from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.constants import URL_DB

# Create engine and session:
engine = create_engine(URL_DB)
Session = sessionmaker(bind=engine)

session = Session()
Base = declarative_base()
