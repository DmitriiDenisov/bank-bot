import psycopg2


conn = psycopg2.connect(host="34.72.212.249", database="bank_bot_db", user="dmitryhse", password="qwertyui")
cur = conn.cursor()
print('PostgreSQL database version:')
cur.execute('SELECT version()')

db_version = cur.fetchone()
print(db_version)
a = cur.execute("SELECT * FROM customers")
print(cur.fetchone())
# print(a)
