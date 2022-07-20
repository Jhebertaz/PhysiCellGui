# https://python.hotexamples.com/fr/examples/PyQt4.QtGui/QFileSystemModel/setNameFilters/python-qfilesystemmodel-setnamefilters-method-examples.html

import os
import sys

from PySide6.QtCore import QDir, QItemSelection
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QDialog, QFileDialog, QFileSystemModel, QAbstractItemView, QDialogButtonBox, QHBoxLayout, \
    QListView, QWidget, QVBoxLayout, QSizePolicy

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




class SvgViewer(QDialog, sc):

    def __init__(self, parent=None, option=False):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


        # Horizontal layout for main widget
        self.ui.main_horizontal_layout = QHBoxLayout(self.ui.widget)

        # Left Vertical layout
        self.ui.left_widget = QWidget()
        self.ui.left_vertical_layout = QVBoxLayout()

        self.ui.left_widget.setLayout(self.ui.left_vertical_layout)
        self.ui.main_horizontal_layout.addWidget(self.ui.left_widget)


        # update function to sc class
        sc.browse = self.browse_listview

        # Browse bar
        self.ui.search_box = sc()
        self.ui.left_vertical_layout.addWidget(self.ui.search_box)

        # equivalence
        self._directory_combo_box = self.ui.search_box._directory_combo_box

        # listView
        self.ui.listView = QListView()
        self.ui.left_vertical_layout.addWidget(self.ui.listView)


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


        # initiate with the current directory
        self._directory_combo_box.addItem(QDir.currentPath())
        self._directory_combo_box.currentIndexChanged.connect(self.apply_listview)

        # Insert svg viewer
        self.viewer = QSvgWidget()

        self.ui.main_horizontal_layout.addWidget(self.viewer)

        # Size Policies
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.ui.search_box.setSizePolicy(sizePolicy)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.ui.listView.setSizePolicy(sizePolicy)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.viewer.setSizePolicy(sizePolicy)

        self.ui.main_horizontal_layout.setStretch(0, 0)
        self.ui.main_horizontal_layout.setStretch(1, 10)

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
            if self._directory_combo_box.findText(directory) == -1:
                self._directory_combo_box.addItem(directory)

            self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(directory))
            self.ui.model.setRootPath(directory)
    def apply_listview(self):
        directory = self._directory_combo_box.currentText()

        if directory:
            self.ui.model.setRootPath(directory)
            self.ui.model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
            self.ui.listView.setModel(self.ui.model)
            self.ui.listView.setRootIndex(self.ui.model.index(directory))
    # def set_working_directory(self, path):
    #     self.working_directory = path
    #     self.ui.tree_file_comboBox.addItem(self.working_directory)
    #     self.ui.tree_file_comboBox.setCurrentIndex(self.ui.tree_file_comboBox.findText(self.working_directory))
