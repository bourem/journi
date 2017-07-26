import sqlite3
import sys
from contextlib import contextmanager

from PyQt5.QtWidgets import (QApplication, QWidget, QListView, QVBoxLayout, 
        QPushButton, QStackedWidget, QMainWindow, QLabel, QPlainTextEdit)
from PyQt5.QtCore import (QAbstractListModel, QVariant, Qt, pyqtSignal, 
        QModelIndex, QIdentityProxyModel)


@contextmanager
def db_connect(db_name):
    """ With statement context manager for DB Connection """
    conn = sqlite3.connect(db_name)
    yield conn
    conn.commit()
    conn.close()


class JourniData(object):
    """ Class to serve and set Journi data stored in SQLite db """

    db_name_default = "journi.db"

    def __init__(self, db_name=None):
        self.db_name = db_name if db_name else self.db_name_default
        self.refresh_all_data()

    def count(self):
        return len(self.data)

    def get_item_at(self, index):
        return self.data[index][1:]

    def set_item_at(self, index, new_value):
        data = (self.data[index][0],) + new_value
        self.data[index] = data
        with db_connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(
                    '''UPDATE entries SET date=?, content=? WHERE ID=?''',
                    (data[1], data[2], data[0]))

    def add_entry(self, date, content):
        """ Add an entry to the DB.

        date: string
        content: string
        """
        with db_connect(self.db_name) as conn:
            c = conn.cursor()
            new_entry = (date, content)
            c.execute('''INSERT INTO entries VALUES (?,?)''', new_entry)

    def refresh_all_data(self):
        """ Replace data by current data in db."""
        with db_connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''SELECT * from entries''')
            entries = c.fetchall()
            self.data = entries


class JourniModel(QAbstractListModel):

    def __init__(self, data_source, parent=None):
        super().__init__()
        self.data_source = data_source

    def rowCount(self, model_index):
        return self.data_source.count()

    def data(self, model_index, role):
        if not model_index.isValid():
            return QVariant()
        if role in [Qt.DisplayRole, Qt.EditRole]:
            return self.data_source.get_item_at(model_index.row())
        return QVariant()

    def setData(self, model_index, new_value):
        self.data_source.set_item_at(model_index.row(), new_value)
        self.dataChanged.emit(model_index, model_index)
        return True

    def addData(self, date, content):
        self.data_source.addData(date, content)
        self.dataChanged.emit()
        return True


class JourniListProxyModel(QIdentityProxyModel):

    def __init__(self):
        super(JourniListProxyModel, self).__init__()
    
    def data(self, model_index, role):
        if role != Qt.DisplayRole:
            return self.sourceModel().data(model_index, role)

        data = list(self.sourceModel().data(model_index, role))
        if len(data[1]) > 20:
            data[1] = data[1][:20] + "…"
        return "{0[0]} - {0[1]}".format(data)



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


class JourniEntryWidget(QWidget):
    """
    Widget displaying one entry, with editable text field.
    """

    closeentry_signal = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setMinimumSize(400, 100)
        layout = QVBoxLayout()
        self.date = QLabel()
        layout.addWidget(self.date)
        self.content = QPlainTextEdit()
        layout.addWidget(self.content)
        button = QPushButton("&Back")
        button.clicked.connect(self.closeentry_signal)
        layout.addWidget(button)
        button = QPushButton("&Save")
        button.clicked.connect(self.save_entry)
        layout.addWidget(button)
        self.setLayout(layout)
        self.current_model_index = None
        
    def set_entry(self, model_index):
        data = self.model.data(model_index, Qt.EditRole)
        self.date.setText(data[0])
        self.content.setDocumentTitle(data[0])
        self.content.setPlainText(data[1])
        self.current_model_index = model_index
    
    def save_entry(self):
        self.model.setData(
                self.current_model_index,
                (self.date.text(), self.content.toPlainText()))

    def unset_entry(self):
        self.current_model_index = None
        pass


class JourniUI(QMainWindow):
    """
    Main app window.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()

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
       
        # All entries view
        list_proxy_model = JourniListProxyModel()
        list_proxy_model.setSourceModel(self.model)
        widget = JourniListWidget(list_proxy_model)
        widget.entryselect_signal.connect(self.show_one_entry_view)
        index = stacked.addWidget(widget)
        self.widgets["entries_list"] = widget

        #One entry view
        widget = JourniEntryWidget(self.model)
        widget.closeentry_signal.connect(self.show_all_entries_view)
        index = stacked.addWidget(widget)
        self.widgets["entry_details"] = widget

    def show_one_entry_view(self, index):
        self.widgets["entry_details"].set_entry(index)
        self.stacked.setCurrentWidget(self.widgets["entry_details"])

    def show_all_entries_view(self):
        self.stacked.setCurrentWidget(self.widgets["entries_list"])

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
    
    ui.show()

    sys.exit(app.exec_())
