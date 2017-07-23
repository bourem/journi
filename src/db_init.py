import sqlite3


if __name__ == "__main__":
    conn = sqlite3.connect('journi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE entries
                 (
                 id integer primary key autoincrement,
                 date text not null, 
                 content text)''')
    conn.commit()
    conn.close()

