import sqlite3


if __name__ == "__main__":
    conn = sqlite3.connect('journi.db')
    c = conn.cursor()
    c.execute('''INSERT INTO entries
                 VALUES ('2017-07-02', 'blabliblubleblo')''')
    conn.commit()
    conn.close()

