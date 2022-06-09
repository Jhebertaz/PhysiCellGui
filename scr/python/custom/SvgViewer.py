import os

from PySide6.QtCore import QDir, QItemSelection
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QDialog, QFileDialog, QFileSystemModel, QAbstractItemView

# os.system("pyside6-uic scr\ui\SvgViewer.ui -o scr\python\custom\ui_SvgViewer.py")
from custom.ui_SvgViewer import Ui_Dialog

class SvgViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # For the listview
        dir_path = "."
        self.ui.model = QFileSystemModel()
        self.ui.model.setRootPath(dir_path)
        self.ui.model.setFilter(QDir.NoDotAndDotDot | QDir.Files)

        self.ui.listView.setModel(self.ui.model)
        self.ui.listView.setRootIndex(self.ui.model.index(dir_path))

        self.ui.listView.doubleClicked.connect(self.listview_doubleClicked)
        self.ui.listView.selectionModel().selectionChanged.connect(self.listview_doubleClicked)
        self.ui.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # listview supplementary widgets
        self.ui.tree_file_browse_button.clicked.connect(self.browse_listview)

        # initiate with the current directory
        self.ui.tree_file_comboBox.addItem(QDir.currentPath())
        self.ui.tree_file_comboBox.currentIndexChanged.connect(self.apply_listview)

        # Insert svg viewer
        self.viewer = QSvgWidget()
        self.ui.svg_vertical_layout.addWidget(self.viewer)

        self.setWindowTitle("SVG Viewer")

    def listview_doubleClicked(self, index):
        if type(index) == type(QItemSelection()):
            idx = index.indexes()[0]
            path = self.ui.model.filePath(idx)

            if os.path.isfile(path):
                # Display
                self.viewer.load(path)
    def browse_listview(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", QDir.currentPath())

        if directory:
            if self.ui.tree_file_comboBox.findText(directory) == -1:
                self.ui.tree_file_comboBox.addItem(directory)

            self.ui.tree_file_comboBox.setCurrentIndex(self.ui.tree_file_comboBox.findText(directory))
            self.ui.model.setRootPath(directory)
    def apply_listview(self):
        directory = self.ui.tree_file_comboBox.currentText()

        if directory:
            self.ui.model.setRootPath(directory)
            self.ui.model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
            self.ui.listView.setModel(self.ui.model)
            self.ui.listView.setRootIndex(self.ui.model.index(directory))

