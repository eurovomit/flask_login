import sqlite3

con = sqlite3.connect('test.db')
cur = con.cursor()
a = cur.execute('SELECT * FROM user WHERE id = 1')

