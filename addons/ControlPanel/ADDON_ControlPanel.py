import os
import sys

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QScrollArea, QVBoxLayout, QWidget, QFormLayout, QLineEdit, QLabel, QGridLayout, \
    QPushButton, QGroupBox, QSizePolicy, QDialogButtonBox

# basic info
filename = 'ADDON_ControlPanel.py'
path = os.path.realpath(__file__).strip(filename)

# Change directory for the script one
os.chdir('C'+path)


# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic controlPanel.ui > controlPanelUi.py")

elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic controlPanel.ui -o controlPanelUi.py")

from controlPanelUi import Ui_Dialog

function = {
            'reset':lambda:os.system('make reset'),
            'data-cleanup':lambda:os.system('make data-cleanup'),
            'clean':lambda:os.system('make clean'),
            'gbm_tmz_ov_immune_stroma_patchy':lambda:os.system('gbm_tmz_ov_immune_stroma_patchy')
            }
function = {
            'reset':lambda:print('make reset'),
            'data-cleanup':lambda:print('make data-cleanup'),
            'clean':lambda:print('make clean'),
            'gbm_tmz_ov_immune_stroma_patchy':lambda:print('gbm_tmz_ov_immune_stroma_patchy')
            }

sys.path.insert(1, 'C'+path+"../SvgViewer")
from ADDON_SvgViewer import SvgViewer as svg

sys.path.insert(1,"C"+path+"/../../scr/python/custom")
from SearchComboBox import SearchComboBox

class ControlPanel(QDialog):

    def __init__(self, parent=None, option=True):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Control Panel")
        self.ui.label.setText('Control Panel')

        self.ui.formLayout = QVBoxLayout()

        # Setting up for the widget
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())

        self.ui.groupBox = QWidget()                    #QGroupBox("This Is Group Box")
        self.ui.groupBox.setSizePolicy(sizePolicy)

        self.label = {}
        self.button = {}

        # Put button on screen
        for key, value in function.items():
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

        self.ui.svgViewer = svg(option=False) # Not dialog button

        self.ui.horizontalLayout_2.addWidget(self.ui.svgViewer)
        self.ui.horizontalLayout_2.setStretch(1, 12)

        # File combo box browser
        self.ui.search_combo_box = SearchComboBox()
        self.ui.verticalLayout.addWidget(self.ui.search_combo_box)

        # Button box
        if option == True:
            self.ui.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.ui.verticalLayout.addWidget(self.ui.buttonBox)

            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)


