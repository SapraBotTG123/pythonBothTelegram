import sqlite3
from main import *
connect = sqlite3.connect('base.db')
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS "users" ("id" Integer not null, "tg_id" Integer not null, primary key("id" AUTOINCREMENT));''')
connect.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS "categories" ("id" Integer not null, "name" Text not null, primary key("id" AUTOINCREMENT));''')
connect.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS "sub" ("user_id" Integer not null, "cate_id" Integer not null);''')
connect.commit()


