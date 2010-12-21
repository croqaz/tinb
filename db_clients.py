
import os, sqlite3

# This file is created in the current directory.
con = sqlite3.connect('database/database.db')

# Try to DELETE tables !!!
try:
    con.execute("DROP TABLE tranzactions")
    con.execute("DROP TABLE clients")
except:
    pass
# Re-create tables.
con.execute('CREATE TABLE tranzactions (id INTEGER PRIMARY KEY, tranz TEXT, quantity INTEGER NOT NULL, price INTEGER NOT NULL)')
con.execute('CREATE TABLE clients (id INTEGER PRIMARY KEY, name TEXT NOT NULL)')

# One tranzaction contains:
# item ID
# quantity
# price
# client ID

# A few tranzactions.
con.execute("INSERT INTO tranzactions (id,tranz,quantity,price) VALUES (101,'{}',2,30)")
con.execute("INSERT INTO tranzactions (tranz,quantity,price)    VALUES ('{}',4,40)")
con.execute("INSERT INTO tranzactions (tranz,quantity,price)    VALUES ('{}',5,50)")

# A few clients.
con.execute("INSERT INTO clients (id,name) VALUES (10,'Ana Mititichi')")
con.execute("INSERT INTO clients (name) VALUES    ('Mama (rodica)')")
con.execute("INSERT INTO clients (name) VALUES    ('Corina (super cori)')")
con.execute("INSERT INTO clients (name) VALUES    ('Bogdana')")
con.execute("INSERT INTO clients (name) VALUES    ('Dana Popa')")
con.execute("INSERT INTO clients (name) VALUES    ('Alina (vodafone)')")
con.execute("INSERT INTO clients (name) VALUES    ('Antonia (vodafone)')")
con.execute("INSERT INTO clients (name) VALUES    ('Flori (vodafone)')")

con.commit()

print('Done!')
os.system('pause')
