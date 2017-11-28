"""
journi.db_populate_dummy

Module used exclusively to populate a database 'test.db' already containing
a table 'entries', with a couple dummy entries.

TODO: move to tests.
"""

if __name__ == "__main__":
    import sqlite3

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    dummy_values = [
            ("2017-01-01", "auienrstiuenrstaiunrset"),
            ("2017-01-02", "bbbb b bb b bbbb bbbbb")
            ]
    c.executemany('''INSERT INTO entries(date, content)
                 VALUES (?, ?)''',
                 dummy_values)
    conn.commit()
    conn.close()

