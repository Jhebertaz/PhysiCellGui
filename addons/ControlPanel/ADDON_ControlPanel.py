import os
import sys

from PySide6.QtCore import Qt, QDir, QDateTime
from PySide6.QtWidgets import QDialog, QScrollArea, QVBoxLayout, QWidget, QLabel, QPushButton, QSizePolicy, \
    QDialogButtonBox, QFileDialog, QInputDialog, QHBoxLayout

from script.extra_function import *

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


class ControlPanel(QDialog):

    def __init__(self, parent=None, option=False):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Control Panel GBM")

        # Horizontal layout for main widget
        self.ui.main_horizontal_layout = QHBoxLayout(self.ui.widget)

        # 
        self.working_directory = QDir.currentPath()
        
        # For button
        self.ui.formLayout = QVBoxLayout()
        
        # Left 
        self.ui.groupBox = QWidget()
        
        # Setting up for the widget
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.ui.groupBox.setSizePolicy(sizePolicy)
        self.ui.groupBox.setLayout(self.ui.formLayout)

        self.label = {}
        self.button = {}

        # Put button on screen
        functions["specific_export_output"] = lambda: specific_export_output(parent=self,source=r"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output", destination=r"C:\Users\Julien\Documents\test\normal", project_name="GBM")
        functions["progress_bar"] = lambda:self.simulation()

        for key, value in functions.items():
            self.label[key] = QLabel(key)
            self.button[key] = QPushButton(key)
            self.button[key].clicked.connect(value)
            self.ui.formLayout.addWidget(self.button[key]) #, self.button[key])

        self.ui.scroll = QScrollArea()
        self.ui.main_horizontal_layout.addWidget(self.ui.scroll)

        self.ui.scroll.setWidget(self.ui.groupBox)
        self.ui.scroll.setWidgetResizable(True)
        self.ui.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.ui.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.ui.svgViewer = svg(option=False) # No dialog button

        self.ui.main_horizontal_layout.addWidget(self.ui.svgViewer)
        self.ui.main_horizontal_layout.setStretch(1, 10)


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

    # def specific_export_output(self,source=None,destination=None,project_name=None):
    #     if not source:
    #         source = QFileDialog.getExistingDirectory(self, "Select Directory Source")
    #     if not destination:
    #         destination = QFileDialog.getExistingDirectory(self, "Select Directory Destination")
    #     if not project_name:
    #         project_name, ok3 = QInputDialog.getText(self, 'Name form', 'Project Name:')
    #     else:
    #         ok3 = True
    #
    #     if ok3 and source and destination:
    #         dest_fold = f"{destination}/{project_name}"
    #         dest_fold += QDateTime.currentDateTime().toString(Qt.ISODate).replace(":","_")
    #         # Should be created else where
    #
    #         insta = sc(parent=self)
    #         insta.copy_files(scr=source, dest=dest_fold)
    #     return dest_fold

    def simulation(self):
        p = 'gbm-ov-immune-stroma-patchy-sample'
        n = 'gbm_ov_immune_stroma_patchy.exe'
        os.system(f'start cmd /c  "make {p} & make & .\{n}"')
        progress_bar = SimulationProgress(parent=self)






