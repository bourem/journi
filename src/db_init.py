import sqlite3

def db_init(db_name="journi.db"):
    conn = sqlite3.connect('journi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE entries
                 (
                 id integer primary key,
                 date integer not null, 
                 content text)''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    db_init()
