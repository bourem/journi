"""
journi.db_utils

Module to provide utility methods to  manipulate the database. SQLite only.
"""


import sqlite3


def db_init(db_name="journi.db"):
    """ Initializes the application database.

    Will create a new db with filename db_name if there is no such file
    already.
    Will create a new entries table if does not exist already.
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (
                 id integer primary key,
                 date integer not null,
                 content text)''')
    conn.commit()
    conn.close()


def db_list_entries(db_name="journi.db"):
    """ Prints the list of all database entries to the standard output.
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''SELECT * from  entries;''')
    entries = c.fetchall()
    conn.commit()
    conn.close()
    print(entries)


#TODO: move the below to tests/
if __name__ == "__main__":
    db_init("test.db")
    db_list_entries("test.db")
