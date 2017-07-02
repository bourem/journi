import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QWidget


def get_all_entries():
    """ Return an unsorted array of all entries in the DB."""
    conn = sqlite3.connect('journi.db')
    c = conn.cursor()
    c.execute('''SELECT * from entries''')
    entries = c.fetchall()
    return entries


def add_entry(date, content):
    """ Add an entry to the DB.

    date: string
    content: string
    """
    conn = sqlite3.connect('journi.db')
    c = conn.cursor()
    new_entry = (date, content)
    c.execute('''INSERT INTO entries VALUES (?,?)', new_entry''')


def draw_window():
    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(250,250)
    w.move(300, 300)
    w.setWindowTitle('Journi')
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    print(get_all_entries())
