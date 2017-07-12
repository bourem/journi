import sqlite3
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QListView, QVBoxLayout, 
        QPushButton, QStackedWidget, QMainWindow)
from PyQt5.QtCore import QAbstractListModel, QVariant, Qt, pyqtSignal, QModelIndex

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


class JourniListWidget(QWidget):
    """
    Widget displaying the list of all entries, with a select button.
    """
    
    # Needs to be a class member
    entryselect_signal = pyqtSignal([QModelIndex])

    def __init__(self, model):
        super().__init__()
        self.setMinimumSize(400, 100)
        layout = QVBoxLayout()
        view = QListView()
        view.setModel(model)
        layout.addWidget(view)
        button = QPushButton("&Go")
        button.clicked.connect(self.emit_entryselect_event)
        layout.addWidget(button)
        self.setLayout(layout)
        self.view = view

    def emit_entryselect_event(self):
        """
        Emit event containing currently selected QModelIndex
        """
        indexes = self.view.selectedIndexes()
        if len(indexes) == 0:
            print("No entries selected")
        else:
            index = indexes[0]
            self.entryselect_signal.emit(index)


class JourniUI(QMainWindow):
    """
    Main app window.
    """
    
    def __init__(self):
        super().__init__()

    def init_ui(self):
        self.setWindowTitle('Journi')
        self.setMinimumSize(400, 100)
        self.widgets = {}
        self.setup_model()
        self.setup_views()

    def setup_model(self):
        data = JourniData()
        self.model = JourniModel(data)

    def setup_views(self):
        # Use QStackedWidget to 'easily' switch between views
        stacked = QStackedWidget()
        self.stacked = stacked
        self.setCentralWidget(stacked)
        
        widget = JourniListWidget(self.model)
        widget.entryselect_signal.connect(self.show_one_entry_view)
        
        index = stacked.addWidget(widget)
        self.widgets["entries_list"] = widget

    def show_one_entry_view(self, index):
        print(index.data())
        pass

    def select_entry(self):
        indexes = self.view.selectedIndexes()
        if len(indexes) == 0:
            print("No entries selected")
        else:
            index = indexes[0]
            self.show_one_entry_view(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = JourniUI()
    ui.init_ui()
    #ui.show_all_entries_view()
    
    ui.show()

    sys.exit(app.exec_())
