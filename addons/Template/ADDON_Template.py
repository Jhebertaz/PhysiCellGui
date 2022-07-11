import os
import sys
from PySide6.QtWidgets import QDialog

# basic info
filename = 'ADDON_Template.py'
path = os.path.realpath(__file__).strip(filename)

# Change directory for the script one
os.chdir(path)

# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic template.ui > templateUi.py")

elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic template.ui -o templateUi.py")

from templateUi import Ui_Dialog

class Template(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Template")

    def set_working_directory(self, path):
        self.working_directory = path




