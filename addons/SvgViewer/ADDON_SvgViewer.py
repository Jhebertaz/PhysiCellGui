# https://python.hotexamples.com/fr/examples/PyQt4.QtGui/QFileSystemModel/setNameFilters/python-qfilesystemmodel-setnamefilters-method-examples.html

import os
import sys

from PySide6.QtCore import QDir, QItemSelection
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QDialog, QFileDialog, QFileSystemModel, QAbstractItemView, QDialogButtonBox



# basic info
filename = 'ADDON_SvgViewer.py'
path = os.path.realpath(__file__).strip(filename)

# Change directory for the script one
os.chdir(path)


# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic SvgViewer.ui > ui_SvgViewer.py")

elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic SvgViewer.ui -o ui_SvgViewer.py")

from ui_SvgViewer import Ui_Dialog

sys.path.insert(1,path+"/../../scr/python/custom")
from SearchComboBox import SearchComboBox as sc


class SvgViewer(QDialog):

    def __init__(self, parent=None, option=False):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        sc.browse = self.browse_listview
        self.ui.search_box = sc()

        self.ui.tree_file_comboBox = self.ui.search_box._directory_combo_box


        self.ui.verticalLayout_2.addWidget(self.ui.search_box)

        # For the listview
        self.working_directory = QDir.currentPath()
        self.ui.model = QFileSystemModel()
        self.ui.model.setRootPath(self.working_directory)

        # To only display svg file
        self.ui.model.setNameFilters(["*.svg"])
        self.ui.model.setNameFilterDisables(False)
        self.ui.model.setFilter(QDir.NoDotAndDotDot | QDir.Files)

        self.ui.listView.setModel(self.ui.model)
        self.ui.listView.setRootIndex(self.ui.model.index(self.working_directory))

        self.ui.listView.doubleClicked.connect(self.listview_doubleClicked)
        self.ui.listView.selectionModel().selectionChanged.connect(self.listview_doubleClicked)
        self.ui.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # listview supplementary widgets
        # self.ui.tree_file_browse_button.clicked.connect(self.browse_listview)

        # initiate with the current directory
        self.ui.tree_file_comboBox.addItem(QDir.currentPath())
        self.ui.tree_file_comboBox.currentIndexChanged.connect(self.apply_listview)

        # Insert svg viewer
        self.viewer = QSvgWidget()

        self.ui.svg_vertical_layout.addWidget(self.viewer)

        if option==None:
            # Button box
            self.ui.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
            self.ui.verticalLayout.addWidget(self.ui.buttonBox)

            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("SVG Viewer")

    def listview_doubleClicked(self, index):
        if type(index) == type(QItemSelection()):
            try:
                idx = index.indexes()[0]
            except IndexError:
                return

            path = self.ui.model.filePath(idx)

            # Verify it is a file
            if os.path.isfile(path):
                # Display
                self.viewer.load(path)

    def browse_listview(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", self.working_directory)

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
    # def set_working_directory(self, path):
    #     self.working_directory = path
    #     self.ui.tree_file_comboBox.addItem(self.working_directory)
    #     self.ui.tree_file_comboBox.setCurrentIndex(self.ui.tree_file_comboBox.findText(self.working_directory))
