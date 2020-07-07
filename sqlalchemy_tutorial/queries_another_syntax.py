from sqlalchemy import create_engine, and_

engine = create_engine('...', echo=False)

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

metadata = MetaData()

users = Table('customers', metadata,
              Column('id', Integer, primary_key=True),
              Column('first_name', String(50)),
              Column('second_name', String(50)),
              Column('nickname_telegram', String(50)),
              Column('join_date', Date),
              )

metadata.create_all(engine)

conn = engine.connect()

from sqlalchemy.sql import select

s = select([users]).where(and_(users.c.id >= 5, users.c.first_name == 'Dmitry'))
result = conn.execute(s)

for row in result:
    print(row)
