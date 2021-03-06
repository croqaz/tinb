
import os, sqlite3

# This file is created in the current directory.
con = sqlite3.connect('database/database.db')

# Delete tables !!!
try:
    #con.execute("DROP TABLE categories")
    #con.execute("DROP TABLE labels")
    pass
except:
    pass
# Re-create tables.
con.execute('CREATE TABLE categories (id TEXT PRIMARY KEY, name TEXT NOT NULL)')
con.execute('CREATE TABLE labels (id INTEGER PRIMARY KEY, name TEXT NOT NULL)')

# A few categories.
con.execute("INSERT INTO categories (id,name) VALUES ('C0','Colier')")
con.execute("INSERT INTO categories (id,name) VALUES ('C2','Cercei')")
con.execute("INSERT INTO categories (id,name) VALUES ('B','Bratara')")
con.execute("INSERT INTO categories (id,name) VALUES ('P','Pandantiv')")
con.execute("INSERT INTO categories (id,name) VALUES ('I','Inel')")
con.execute("INSERT INTO categories (id,name) VALUES ('BO','Brosa')")
con.execute("INSERT INTO categories (id,name) VALUES ('BC','Bratara+Cercei')")
con.execute("INSERT INTO categories (id,name) VALUES ('CC','Colier+Cercei')")

# A few labels.
con.execute("INSERT INTO labels (id,name) VALUES (10,'negru')")
con.execute("INSERT INTO labels (name) VALUES ('alb')")
con.execute("INSERT INTO labels (name) VALUES ('cenusiu')")
con.execute("INSERT INTO labels (name) VALUES ('gri')")
con.execute("INSERT INTO labels (name) VALUES ('argintiu')")
con.execute("INSERT INTO labels (name) VALUES ('rosu')")
con.execute("INSERT INTO labels (name) VALUES ('roz')")
con.execute("INSERT INTO labels (name) VALUES ('lila')")
con.execute("INSERT INTO labels (name) VALUES ('galben')")
con.execute("INSERT INTO labels (name) VALUES ('auriu')")
con.execute("INSERT INTO labels (name) VALUES ('albastru')")
con.execute("INSERT INTO labels (name) VALUES ('portocaliu')")
con.execute("INSERT INTO labels (name) VALUES ('violet')")
con.execute("INSERT INTO labels (name) VALUES ('verde')")
con.execute("INSERT INTO labels (name) VALUES ('maron')")
con.execute("INSERT INTO labels (name) VALUES ('sarma')")
con.execute("INSERT INTO labels (name) VALUES ('lant')")
con.execute("INSERT INTO labels (name) VALUES ('argint')")
con.execute("INSERT INTO labels (name) VALUES ('plastic')")
con.execute("INSERT INTO labels (name) VALUES ('lemn')")
con.execute("INSERT INTO labels (name) VALUES ('sticla')")
con.execute("INSERT INTO labels (name) VALUES ('ceramica')")
con.execute("INSERT INTO labels (name) VALUES ('cristal')")
con.execute("INSERT INTO labels (name) VALUES ('swarovski')")
con.execute("INSERT INTO labels (name) VALUES ('cips')")
con.execute("INSERT INTO labels (name) VALUES ('melc')")

con.execute("INSERT INTO labels (name) VALUES ('ametist')")
con.execute("INSERT INTO labels (name) VALUES ('aquamarin')")
con.execute("INSERT INTO labels (name) VALUES ('citrin')")
con.execute("INSERT INTO labels (name) VALUES ('coral')")
con.execute("INSERT INTO labels (name) VALUES ('cuart')")
con.execute("INSERT INTO labels (name) VALUES ('granat')")
con.execute("INSERT INTO labels (name) VALUES ('hematit')")
con.execute("INSERT INTO labels (name) VALUES ('jad')")
con.execute("INSERT INTO labels (name) VALUES ('jasp')")
con.execute("INSERT INTO labels (name) VALUES ('lapis lazuli')")
con.execute("INSERT INTO labels (name) VALUES ('malachit')")
con.execute("INSERT INTO labels (name) VALUES ('onix')")
con.execute("INSERT INTO labels (name) VALUES ('obsidian')")
con.execute("INSERT INTO labels (name) VALUES ('ochi de pisica')")
con.execute("INSERT INTO labels (name) VALUES ('peridot')")
con.execute("INSERT INTO labels (name) VALUES ('piatra lunii')")
con.execute("INSERT INTO labels (name) VALUES ('piatra soarelui')")
con.execute("INSERT INTO labels (name) VALUES ('rodonit')")
con.execute("INSERT INTO labels (name) VALUES ('sodalit')")
con.execute("INSERT INTO labels (name) VALUES ('turcoaz')")
con.execute("INSERT INTO labels (name) VALUES ('turmalina')")

con.commit()

print('Done!')
os.system('pause')
