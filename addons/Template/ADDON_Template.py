import os
import sys


from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout

# basic info
filename = 'ADDON_Template.py'
path = os.path.realpath(__file__).strip(filename)

# Change directory for the script one
# os.chdir(path)

# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic {path}{os.sep}template.ui > {path}{os.sep}templateUi.py")

elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic {path}{os.sep}template.ui -o {path}{os.sep}templateUi.py")

from templateUi import Ui_Dialog

class Template(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Title
        self.setWindowTitle("Template")

        # Horizontal layout for main widget
        self.ui.main_horizontal_layout = QHBoxLayout(self.ui.widget)

        # Label
        self.ui.label = QLabel("Template")

        # Label option
        self.ui.label.setFont(QFont('Times font', 25))
        self.ui.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Add label to layout
        self.ui.main_horizontal_layout.addWidget(self.ui.label)

    def set_working_directory(self, path):
        self.working_directory = path




