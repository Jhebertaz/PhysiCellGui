# Inspiration
# # https://learndataanalysis.org/source-code-create-a-simple-python-app-to-run-command-lines-commands-pyqt5-tutorial/
# # https://www.pythonguis.com/tutorials/pyside-qprocess-external-programs/
# # https://doc.qt.io/qtforpython/overviews/qtuitools-textfinder-example.html
import os
import sys

from PySide6.QtWidgets import QDialog, QMessageBox

# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic ui{os.sep}..{os.sep}TextSearch.ui > .{os.sep}ui_TextSearch.py")
elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic ..{os.sep}ui{os.sep}TextSearch.ui -o .{os.sep}ui_TextSearch.py")


from custom.ui_TextSearch import Ui_Dialog

class TextSearch(QDialog):

    def __init__(self, parent):
        self.parent = parent
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(lambda:self.search(self.ui.lineEdit.text()))

    # Too specific
    def search(self, word):

        parent_current_tab = self.parent.ui.tabWidget.currentWidget()
        parent_current_document = self.parent.widget_tool[parent_current_tab]
        found = parent_current_document.find(word)
        # parent_current_document.textCursor().setPosition(0)


        if not word:
            QMessageBox.information(self, "Empty Search Field", "The search field is empty.\nPlease enter a word and click Find.")

        if not found and word:
            QMessageBox.information(self, "Word Not Found", "Sorry, the word cannot be found.")

    def focus(self):
        self.ui.lineEdit.setFocus()
        self.ui.lineEdit.selectAll()
