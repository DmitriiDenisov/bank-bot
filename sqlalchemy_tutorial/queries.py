# coding=utf-8

# 1 - imports
import pandas as pd
# from sqlalchemy_tutorial.actor import Actor
from sqlalchemy_tutorial.base import Session
# from sqlalchemy_tutorial.contact_details import ContactDetails
# from sqlalchemy_tutorial.movie import Movie
from sqlalchemy_tutorial.customer import Customer
from sqlalchemy_tutorial.balances import Balance
from sqlalchemy_tutorial.transactions import Transaction
from sqlalchemy import case
from sqlalchemy import func

# 2. Extract a session
session = Session()


# 3. Simple Select *
all_bal = session.query(Balance)
all_trans = session.query(Transaction).all()
for trans in all_trans:
    pass

for bal in all_bal:
    pass

# 4. Simple Joins

# If we don't have Foreign Keys in tables
# .all() gets list of values. Without .all() it is generator
customers_joined = session.query(Customer, Balance).join(Balance, Customer.id == Balance.customer_id).all()
transactions = session.query(Customer, Transaction).join(Transaction, Customer.id == Transaction.customer_id_from).all()
# If we have Foreign Keys:
joined = session.query(Customer, Balance).join(Balance,
                                               isouter=True).all()  # isouter=True for LEFT not INNER. Same behavior for .outerjoin()
joined2 = session.query(Balance, Customer).join(Customer).all()
# In this case we have Foreign key, but they are two
joined3 = session.query(Customer, Transaction).join(Transaction, Customer.id == Transaction.customer_id_from).all()

# Summary:
# 1. ForeignKey is for making like this session.query(Balance).join(Customer).all()
# 2. relationship is for making available parameters inside objects

print('\n### All customers:')
for customer, balance in customers_joined:
    print(
        f'{customer.id}, {customer.first_name}, {customer.second_name}, {customer.nickname_telegram}, {customer.join_date}')
print('')

# 4.1 Filter + Group by
filter_ex = session.query(Customer).filter(
    (Customer.first_name.like('%Dmi%')) & (Customer.second_name.startswith('De'))).all()
group_ex = session.query(Transaction.customer_id_to.label("customer_id_to"),
                         func.count(Transaction.customer_id_to).label("count_*"),
                         func.sum(Transaction.usd_amt).label("sum_usd"), func.sum(Transaction.eur_amt).label("sum_eur"),
                         func.max(Transaction.usd_amt).label("max_usd")).group_by(
    Transaction.customer_id_to)
group_ex_all = group_ex.all()
df = pd.read_sql(group_ex.statement, session.bind)

# 4.2 Order by + if-else

if_ex = session.query(Transaction,
                      case([(Transaction.aed_amt == 0, 0), ((Transaction.aed_amt < 10) & (Transaction.aed_amt > 0), 1)],
                           else_=2)).order_by(Transaction.eur_amt.desc())
if_ex_all = if_ex.all()
df_if_else = pd.read_sql(if_ex.statement, session.bind)

# 5. Pandas example
# df = pd.read_sql(Customer, query.session.bind)
# df = pd.read_sql(session.query(Customer).filter((Customer.id >= 5) & (Customer.first_name == 'Dmitry')).statement, session.bind)
df = pd.read_sql(session.query(Customer, Balance).join(Balance).statement, session.bind)

print(df)

df = pd.read_sql(session.query(Customer, Balance).join(Balance, isouter=True).statement, session.bind)
print(df)
