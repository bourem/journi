import sqlite3

def db_init(db_name="journi.db"):
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
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''SELECT * from  entries;''')
    entries = c.fetchall()
    conn.commit()
    conn.close()
    print(entries)


if __name__ == "__main__":
    db_init("test.db")
    db_list_entries("test.db")
