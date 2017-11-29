"""
Monolytic qt5 app
"""

import sqlite3
import sys
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QListView, QVBoxLayout,
        QPushButton, QStackedWidget, QMainWindow, QLabel, QPlainTextEdit,
        QAction, QFileDialog, QInputDialog)
from PyQt5.QtCore import (QAbstractListModel, QVariant, Qt, pyqtSignal,
        QModelIndex, QIdentityProxyModel)

from db_utils import db_init, db_connect


class JourniData(object):
    """ Class to serve and set Journi data stored in SQLite db """

    def __init__(self, db_name="journi.db"):
        self.db_name = db_name
        self.refresh_all_data()

    def count(self):
        """ Returns the number of entries currently loaded.

        This is not necessarily equal to the number of entries in the db
        """
        return len(self.data)

    def get_item_at(self, index):
        return self.data[index][1:]

    def set_item_at(self, index, new_content):
        data = self.data[index]
        data = (data[0],data[1], new_content)
        self.data[index] = data
        with db_connect(self.db_name) as cursor:
            cursor.execute(
                    '''UPDATE entries SET content=? WHERE ID=?''',
                    (data[2], data[0]))

    def add_entry(self, date=time.time(), content=""):
        """ Adds an entry to the DB.

        date: string
        content: string
        """
        with db_connect(self.db_name) as cursor:
            new_entry = (date, content)
            cursor.execute('''INSERT INTO entries(date, content)
                                     VALUES (?,?)''', new_entry)
            new_index = cursor.lastrowid
        self.data.append((new_index, date, content))

    def refresh_all_data(self):
        """ Replace data by current data in db."""
        with db_connect(self.db_name) as cursor:
            cursor.execute('''SELECT * from entries''')
            entries = cursor.fetchall()
        self.data = entries

    def insert_rows(self, start_index, count):
        """ Add a number of rows with default values """
        with db_connect(self.db_name) as cursor:
            new_entries = [(time.time(), "") for i in range(count)]
            cursor.executemany('''INSERT INTO entries(date, content)
                                         VALUES (?,?)''', new_entries)
        self.refresh_all_data()

    def set_data_source(self, new_data_source):
        """ Sets up a new sqlite db as data source.

        new_data_source: string - relative path to the db, including filename.
        """
        new_db_name = new_data_source
        if new_db_name == self.db_name:
            return False
        else:
            self.db_name = new_db_name
            self.refresh_all_data()
            return True


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

    def setData(self, model_index, new_content):
        self.data_source.set_item_at(model_index.row(), new_content)
        self.dataChanged.emit(model_index, model_index)
        return True

    def addData(self, date, content):
        self.data_source.addData(date, content)
        self.dataChanged.emit()
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row+count-1)
        self.data_source.insert_rows(row, count)
        self.endInsertRows()
        return True

    def append_new_row(self):
        new_index = self.rowCount(QModelIndex())
        self.beginInsertRows(QModelIndex(), new_index, new_index)
        self.data_source.add_entry(int(time.time()))
        self.endInsertRows()
        return True

    def set_data_source(self, new_data_source):
        self.beginResetModel()
        data_source_changed = self.data_source.set_data_source(new_data_source)
        if data_source_changed:
            self.endResetModel()
        return data_source_changed


class JourniListProxyModel(QIdentityProxyModel):

    def __init__(self):
        super(JourniListProxyModel, self).__init__()

    def format_entry_time(self, timestamp):
        return time.strftime("%Y-%m-%d", time.localtime(timestamp))

    def format_entry_abstract(self, entry_content):
        if len(entry_content) > 20:
            return entry_content[:20] + "…"
        return entry_content[:20]

    def data(self, model_index, role):
        if role != Qt.DisplayRole:
            return self.sourceModel().data(model_index, role)

        data = list(self.sourceModel().data(model_index, role))
        data[0] = self.format_entry_time(data[0])
        data[1] = self.format_entry_abstract(data[1])
        return "{0[0]} - {0[1]}".format(data)

    def append_new_row(self):
        return self.sourceModel().append_new_row()


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
        # Entry select button
        button = QPushButton("&Go")
        button.clicked.connect(self.emit_entryselect_event)
        layout.addWidget(button)
        # Entry add button
        button = QPushButton("&New")
        button.clicked.connect(self.add_new_entry)
        layout.addWidget(button)

        self.setLayout(layout)
        self.view = view

    def emit_entryselect_event(self):
        """
        Emit event selecting currently selected QModelIndex
        """
        indexes = self.view.selectedIndexes()
        if len(indexes) == 0:
            print("No entries selected")
        else:
            index = indexes[0]
            self.entryselect_signal.emit(index)

    def add_new_entry(self):
        """
        """
        last_row_index = self.view.model().rowCount(QModelIndex())
        self.view.model().append_new_row()

        self.view.setCurrentIndex(
                self.view.model().index(last_row_index, 0, QModelIndex()))


class JourniEntryWidget(QWidget):
    """
    Widget displaying one entry for editing, with editable text field.
    """

    closeentry_signal = pyqtSignal()

    def __init__(self, model):
        super().__init__()

        # General
        self.set_model(model)
        self.setMinimumSize(400, 100)
        layout = QVBoxLayout()

        # Data
        self.date = QLabel()
        layout.addWidget(self.date)
        self.content = QPlainTextEdit()
        layout.addWidget(self.content)

        # Buttons
        button = QPushButton("&Back")
        button.clicked.connect(self.closeentry_signal)
        layout.addWidget(button)
        button = QPushButton("&Save")
        button.clicked.connect(self.save_entry)
        layout.addWidget(button)
        self.setLayout(layout)

    def set_model(self, model):
        self.model = model
        self.current_model_index = None

    def set_entry(self, model_index):
        data = self.model.data(model_index, Qt.EditRole)
        date_string = time.strftime("%Y-%m-%d (%a)", time.localtime(data[0]))
        self.date.setText(date_string)
        self.content.setDocumentTitle(date_string)
        self.content.setPlainText(data[1])
        self.current_model_index = model_index

    def save_entry(self):
        self.model.setData(
                self.current_model_index,
                self.content.toPlainText())

    def unset_entry(self):
        self.current_model_index = None
        pass


class JourniUI(QMainWindow):
    """
    Main app window.
    """

    def __init__(self):
        super().__init__()
        self.setup_model()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Journi')
        self.setMinimumSize(400, 100)
        self.widgets = {}
        self.setup_views()

    def setup_model(self):
        data = JourniData()
        self.model = JourniModel(data)

    def setup_menus(self):
        self.statusBar().showMessage("Hi there!")
        # MainMenu
        exit_menu = self.menuBar().addMenu("Main&Menu")
        exit_action = QAction("&Quit", self)
        exit_action.setStatusTip("Quit this program without saving!")
        exit_action.triggered.connect(self.close)
        exit_menu.addAction(exit_action)
        # DB Menu
        db_menu = self.menuBar().addMenu("&Database")
        db_select_action = QAction("&Select", self)
        db_select_action.setStatusTip("Select DB")
        db_select_action.triggered.connect(self.db_select_menu)
        db_menu.addAction(db_select_action)
        db_create_action = QAction("&Create DB", self)
        db_create_action.setStatusTip("Create new DB")
        db_create_action.triggered.connect(self.db_create_menu)
        db_menu.addAction(db_create_action)

    def db_select_menu(self):
        filename = QFileDialog.getOpenFileName(
                self,
                "Please select a working database",
                "",
                "SQlite files (*.db)")
        if filename[0] != "":
            self.model.set_data_source(filename[0])
            self.statusBar().showMessage("Changed active DB to: " + filename[0])
        else:
            self.statusBar().showMessage("Didn't change the active DB")

    def db_create_menu(self):
        value = QInputDialog.getText(
                self,
                "New database name",
                "Type the new DB name (without file extension):")
        if value[1] and value[0]!="":
            new_db_name = value[0] + ".db"
            db_init(new_db_name)
            self.model.set_data_source(new_db_name, "SQLite")
            self.statusBar().showMessage("Created new DB: " + new_db_name)

    def setup_views(self):
        self.setup_menus()

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


def main():
    app = QApplication(sys.argv)

    # Temporary. Create 'entries' table in 'journi.db' DB
    # (no-op if already exists)
    db_init()

    ui = JourniUI()
    ui.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
