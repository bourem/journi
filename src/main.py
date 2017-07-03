import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout


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


class JourniUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Journi')
        
        self.show()

    def show_entries(self, entries): 
        for e in entries:
            lbl = QLabel(self)
            lbl.setGeometry(0,0,20,400)
            lbl.setText(e[0])
            self.layout.addWidget(lbl)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = JourniUI()
    ui.show_entries(get_all_entries())
    print(get_all_entries())
    sys.exit(app.exec_())
