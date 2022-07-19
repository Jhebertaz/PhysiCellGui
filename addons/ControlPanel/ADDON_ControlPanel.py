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
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.ui.widget.sizePolicy().hasHeightForWidth())

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

        # File combo box browser
        # self.ui.search_combo_box = SearchComboBox()
        # self.ui.verticalLayout.addWidget(self.ui.search_combo_box)

        # Button box
        if option == True:
            self.ui.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.ui.verticalLayout.addWidget(self.ui.buttonBox)

            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)

    def set_working_directory(self, path):
        self.working_directory = path
        self.ui.svgViewer.set_working_directory(path=self.working_directory)
        # self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(path))

    def specific_export_output(self):
        source = str(QFileDialog.getExistingDirectory(self, "Select Directory Source"))
        destination = self.save_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory Destination"))
        project_name, ok = QInputDialog.getText(self, 'Name form', 'Project Name:')
        dest_fold = f"{destination}/{project_name}"
        dest_fold += QDateTime.currentDateTime().toString(Qt.ISODate).replace(":","_")

        # progress  = flp()
        # progress.copyFolder(src=source, dst=destination)
        # progress.exec()




        # if "save_folder" in self.__dict__.keys():
        #
        #     # confirm source folder
        #     msgBox = QMessageBox()
        #     msgBox.setText(f"Save folder set to {self.working_directory}")
        #     msgBox.setInformativeText("Do you want to change the save folder?")
        #     msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
        #
        #     result = msgBox.exec()
        #
        #     if result == QMessageBox.Yes:
        #         # do yes-action
        #         source = str(QFileDialog.getExistingDirectory(self, "Select Source Destination"))
        #     else:
        #         # do no-action
        #         source = self.working_directory
        #
        #     # confirm save folder
        #     msgBox = QMessageBox()
        #     msgBox.setText(f"Save folder set to {self.save_folder}")
        #     msgBox.setInformativeText("Do you want to change the save folder?")
        #     msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
        #
        #     result = msgBox.exec()
        #
        #     if result == QMessageBox.Yes:
        #         # do yes-action
        #         destination = self.save_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory Destination"))
        #     else:
        #         # do no-action
        #         destination = self.save_folder
        #
        # else:
        #     source = str(QFileDialog.getExistingDirectory(self, "Select Directory Source"))
        #     destination = self.save_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory Destination"))
        #
        #
        #
        # project_name, ok = QInputDialog.getText(self, 'Name form', 'Project Name:')
        #
        # # Incomplete
        # if not ok and QDir.exists(QDir(source)) and QDir.exists(QDir(destination)):
        #     msgBox = QMessageBox()
        #     msgBox.setText("Failed to export data")
        #     msgBox.exec()
        #     return
        #
        # dest_fold = f"{destination}/{project_name}"
        # dest_fold += QDateTime.currentDateTime().toString(Qt.ISODate).replace(":","_")


        # Copy data should be in seprate thread
        # shutil.copytree(source, dest_fold)

        # if QDir.exists(QDir(dest_fold)):
        # QDate.currentDate().getDate()
        # date = '_'.join(list(map(str, list(QDateTime.currentDateTime().date()))))
        # time = '_'.join(list(map(str, list(QDateTime.currentDateTime().time()))))


