# Inspiration
# # https://learndataanalysis.org/source-code-create-a-simple-python-app-to-run-command-lines-commands-pyqt5-tutorial/
# # https://www.pythonguis.com/tutorials/pyside-qprocess-external-programs/
import sys

from PySide6.QtWidgets import QDialog

sys.path.append(f'..')
from ui_TextSearch import Ui_Dialog

class TextSearch(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


