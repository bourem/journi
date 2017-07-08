import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListView, QVBoxLayout
from PyQt5.QtCore import QAbstractListModel, QVariant, Qt

def get_all_entries():
        """ Return an unsorted array of all entries in the DB."""
        conn = sqlite3.connect('journi.db')
        c = conn.cursor()
        c.execute('''SELECT * from entries''')
        entries = c.fetchall()
        return entries


class JourniData(object):

    def __init__(self):
        self.data = get_all_entries()

    def count(self):
        return len(self.data)

    def get_item_at(self, index):
        return str(self.data[index])

    def add_entry(date, content):
        """ Add an entry to the DB.

        date: string
        content: string
        """
        conn = sqlite3.connect('journi.db')
        c = conn.cursor()
        new_entry = (date, content)
        c.execute('''INSERT INTO entries VALUES (?,?)', new_entry''')


class JourniModel(QAbstractListModel):

    def __init__(self, data_source, parent=None):
        super().__init__()
        self.data_source = data_source

    def rowCount(self, model_index):
        return self.data_source.count()

    def data(self, model_index, role):
        if model_index.isValid() and role == Qt.DisplayRole:
            return self.data_source.get_item_at(model_index.row())
        return QVariant()


class JourniUI(QWidget):
    
    def __init__(self):
        super().__init__()

    def init_ui(self):
        self.setWindowTitle('Journi')
        self.setMinimumSize(400, 100)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def show_all_entries_view(self):
        data = JourniData()
        model = JourniModel(data)
        view = QListView()
        view.setModel(model)
        self.layout.addWidget(view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = JourniUI()
    ui.init_ui()
    ui.show_all_entries_view()
    
    ui.show()

    sys.exit(app.exec_())
