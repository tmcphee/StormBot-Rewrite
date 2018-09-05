import sqlite3
from os import path


def init_tables(cursor, connect):
    cursor.execute("""CREATE TABLE Presets
                              (NoVoice integer , NoMessages integer, GuestRole text, ActiveRole text, InactiveRole text, 
                              BeginDate text, StombotChannel text)
                           """)
    connect.commit()
    cursor.execute("""INSERT INTO Presets VALUES (?,?,?,?,?,?,?)""", (120, 10, "381911719901134850",
                                                                      "[TEST]Discord Active", "[TEST]Discord Inactive",
                                                                      '2018-08-05 20:59:08', '2018-08-05 20:59:08'))
    connect.commit()
    cursor.execute("""CREATE TABLE Fun
                                  (joke text , insult text)
                               """)
    connect.commit()
    cursor.execute("""INSERT INTO Fun VALUES (?,?)""", ('on', 'on'))
    connect.commit()


SQL = path.exists("db/internalsqlite.db")  # Resumes or creates Database file
if SQL is True:
    print("SQL INTERNAL SERVER -- DATABASE RESUMING TO SAVED STATE")
    connect = sqlite3.connect('db/internalsqlite.db')
    cursor = connect.cursor()
else:
    print("WARNING -- INTERNAL DATABASE FAILED TO RESUME TO SAVED STATE")
    print("        -- SYSTEM CREATING DATABASE WITH NEW TABLE(s)")
    connect = sqlite3.connect('db/internalsqlite.db')
    cursor = connect.cursor()
    init_tables(cursor, connect)


class insql:

    def update(self, query, *params):
        global cursor, connect
        cursor.execute(query, *params)
        connect.commit()

    def select(self, query, *params):
        global cursor, connect
        cursor.execute(query, *params)
        return cursor


