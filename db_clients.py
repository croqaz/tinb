
import os, sqlite3

# This file is created in the current directory.
con = sqlite3.connect('database/database.db')

# Delete tables !!!
con.execute("DROP TABLE tranzactions")
con.execute("DROP TABLE clients")
# Re-create tables.
con.execute('CREATE TABLE tranzactions (id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, price INTEGER, client TEXT)')
con.execute('CREATE TABLE clients (id INTEGER PRIMARY KEY, name TEXT NOT NULL)')

# A few categories.
con.execute("INSERT INTO tranzactions (id,item_id,quantity,price,client) VALUES (101,1001,1,0,10)")
con.execute("INSERT INTO tranzactions (id,item_id,quantity,price,client) VALUES (101,1001,1,0,10)")
con.execute("INSERT INTO tranzactions (id,item_id,quantity,price,client) VALUES (101,1001,1,0,10)")

# A few labels.
con.execute("INSERT INTO clients (id,name) VALUES (10,'Ana Mititica')")
con.execute("INSERT INTO clients (name) VALUES ('Client test 01')")
con.execute("INSERT INTO clients (name) VALUES ('Client test 02')")
con.execute("INSERT INTO clients (name) VALUES ('Client test 03')")

con.commit()

print('Done!')
os.system('pause')
