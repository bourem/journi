import sqlite3


if __name__ == "__main__":
    conn = sqlite3.connect('journi.db')
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

