import os
import shutil
import sys
from script.extra_function import functions as fct


from PySide6.QtCore import Qt, QDir, QDate, QDateTime
from PySide6.QtWidgets import QDialog, QScrollArea, QVBoxLayout, QWidget, QLabel, QPushButton, QSizePolicy, \
    QDialogButtonBox, QFileDialog, QInputDialog, QLineEdit, QMessageBox

# basic info
filename = 'ADDON_ControlPanel.py'
path = os.path.realpath(__file__).strip(filename)

# Change directory for the script one
os.chdir("C"+path)


# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic controlPanel.ui > controlPanelUi.py")
elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic controlPanel.ui -o controlPanelUi.py")

from controlPanelUi import Ui_Dialog

sys.path.insert(1, 'C'+path+"../SvgViewer")
from ADDON_SvgViewer import SvgViewer as svg



sys.path.insert(1,"C"+path+"/../../scr/python/custom")
from FileCopyProgress import QFileCopyProgress as sc


class ControlPanel(QDialog):

    def __init__(self, parent=None, option=False):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Control Panel GBM")
        self.ui.label.setText('Control Panel GBM')

        self.working_directory = QDir.currentPath()

        self.ui.formLayout = QVBoxLayout()

        # Setting up for the widget
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.ui.groupBox = QWidget()
        self.ui.groupBox.setSizePolicy(sizePolicy)

        self.label = {}
        self.button = {}

        # Put button on screen
        fct["specific_export_output"] = lambda:self.specific_export_output()
        for key, value in fct.items():
            self.label[key] = QLabel(key)
            self.button[key] = QPushButton(key)
            self.button[key].clicked.connect(value)
            self.ui.formLayout.addWidget(self.button[key]) #, self.button[key])


        self.ui.groupBox.setLayout(self.ui.formLayout)
        self.ui.scroll = QScrollArea()

        self.ui.horizontalLayout_2.addWidget(self.ui.scroll)

        self.ui.scroll.setWidget(self.ui.groupBox)
        self.ui.scroll.setWidgetResizable(True)
        self.ui.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.ui.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.ui.svgViewer = svg(option=False) # No dialog button

        self.ui.horizontalLayout_2.addWidget(self.ui.svgViewer)
        self.ui.horizontalLayout_2.setStretch(1, 10)


        # Button box
        if option == True:
            self.ui.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.ui.verticalLayout.addWidget(self.ui.buttonBox)

            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.verticalLayout.setSpacing(0)
        self.ui.verticalLayout.setContentsMargins(0,0,0,0)

    def set_working_directory(self, path):
        self.working_directory = path
        self.ui.svgViewer.set_working_directory(path=self.working_directory)
        # self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(path))

    def specific_export_output(self):

        source = QFileDialog.getExistingDirectory(self, "Select Directory Source")
        destination = QFileDialog.getExistingDirectory(self, "Select Directory Destination")
        project_name, ok3 = QInputDialog.getText(self, 'Name form', 'Project Name:')


        if ok3 and source and destination:
            dest_fold = f"{destination}/{project_name}"
            dest_fold += QDateTime.currentDateTime().toString(Qt.ISODate).replace(":","_")

            insta = sc(parent=self)
            insta.copy_files(scr=source, dest=dest_fold)



