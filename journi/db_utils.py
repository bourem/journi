"""
journi.db_utils

Module to provide utility methods to manipulate the database. SQLite only.
"""

from contextlib import contextmanager

import sqlite3


@contextmanager
def db_connect(db_name):
    """ With statement context manager for DB Connection """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    yield c
    conn.commit()
    conn.close()


def db_init(db_name="journi.db"):
    """ Initializes the application database.

    Will create a new db with filename db_name if there is no such file
    already.
    Will create a new entries table if does not exist already.
    """
    with db_connect(db_name) as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS entries
                 (
                 id integer primary key,
                 date integer not null,
                 content text)''')


def db_list_entries(db_name="journi.db"):
    """ Prints the list of all database entries to the standard output.

    Used for quick dirty debugging.
    """
    with db_connect(db_name) as cursor:
        cursor.execute('''SELECT * from  entries;''')
        entries = cursor.fetchall()
    print(entries)


#TODO: move the below to test/
if __name__ == "__main__":
    db_init("test.db")
    db_list_entries("test.db")
