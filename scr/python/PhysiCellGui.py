# This Python file uses the following encoding: utf-8
import os
import sys
import importlib
from PySide6.QtCore import QDir, QCoreApplication, QFile, Slot, QDirIterator
from PySide6.QtGui import QTextDocumentWriter, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QWidget, QPlainTextEdit, QHBoxLayout, \
    QMessageBox, QFileDialog, QDialog


# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic ui{os.sep}..{os.sep}PhysiCellGui.ui > .{os.sep}ui_PhysiCellGui.py")
elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic ..{os.sep}ui{os.sep}PhysiCellGui.ui -o .{os.sep}ui_PhysiCellGui.py")

### relative import
from custom.CodeEditor import CodeEditor
from custom.FileBrowser import FileBrowser
from custom.TextSearch import TextSearch
# from custom.SvgViewer import SvgViewer
from ui_PhysiCellGui import Ui_MainWindow

### addons import
addons = QDirIterator(f'..{os.sep}..{os.sep}addons', QDirIterator.Subdirectories)

with open('module_to_import.py','w') as file:

    file.write("import sys\n")

    while addons.hasNext():
        current = QDir(addons.next())
        path = current.path()

        if 'ADDON' in path and not '__pycache__' in path:
            module_file_name = current.dirName()
            module_path = current.path().strip(module_file_name)[:-1]

            file.write(f"sys.path.append('..{module_path}')\n")
            file.write(f"from {module_file_name.strip('.py')} import *\n")



from module_to_import import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.working_directory = QDir.currentPath()

        self.setWindowTitle("Dev Gui")

        # For tree_file_comboBox
        # initiate with the current directory
        self.ui.tree_file_comboBox.addItem(QDir.currentPath())
        self.ui.tree_file_comboBox.currentIndexChanged.connect(self.apply_treeview)

        # File browser
        # Custom function to FileBrowser class
        def open_file_of_item(parent, row, column):
            item = parent._files_table.item(row, 0)
            self.load(parent._current_dir.absoluteFilePath(item.text()))

        FileBrowser.open_file_of_item = open_file_of_item

        self.ui.window = FileBrowser()
        self.ui.inside_dock_vertical_layout.addWidget(self.ui.window)

        # Treeview
        # Default working directory
        dir_path = "."
        self.ui.model = QFileSystemModel()
        self.ui.model.setRootPath(dir_path)

        self.ui.treeView.setModel(self.ui.model)
        self.ui.treeView.setRootIndex(self.ui.model.index(dir_path))
        self.ui.treeView.doubleClicked.connect(self.treeView_doubleClicked)

        self.ui.treeView.setColumnHidden(2, True)
        self.ui.treeView.setColumnHidden(3, True)
        self.ui.treeView.setColumnHidden(1, True)

        # Tab widget
        self.ui.tabWidget.tabCloseRequested.connect(self.delete_Tab)

        # Correspondence dictionary
        self.widget_plaintextedit = {}
        self.plaintextedit_path = {}

        # Custom
        self.open_tool_dict = {}
        self.widget_tool = {}
        self.tool_key = {}

        # File menu
        self.ui.actionNew.triggered.connect(self.file_new)
        self.ui.actionSave.triggered.connect(self.file_save)
        self.ui.actionSave_as.triggered.connect(self.file_save_as)
        self.ui.actionOpen.triggered.connect(self.file_open)
        self.ui.actionExit.triggered.connect(QCoreApplication.quit)
        self.ui.actionOpen_terminal.triggered.connect(self.open_terminal)

        # Edit menu
        self.ui.actionUndo.triggered.connect(lambda:self.simple_operation('undo'))
        self.ui.actionRedo.triggered.connect(lambda:self.simple_operation('redo'))
        self.ui.actionSelect_all.triggered.connect(lambda:self.simple_operation('select all'))
        self.ui.actionCut.triggered.connect(lambda:self.simple_operation('cut'))
        self.ui.actionCopy.triggered.connect(lambda:self.simple_operation('copy'))
        self.ui.actionPaste.triggered.connect(lambda:self.simple_operation('paste'))
        self.ui.actionFind.triggered.connect(self.find)

        # View menu
        self.ui.actionZoom_in.triggered.connect(lambda:self.simple_operation('zoom in'))
        self.ui.actionZoom_out.triggered.connect(lambda:self.simple_operation('zoom out'))

        # Tool menu
        # self.ui.actionSvg_viewer.triggered.connect(self.open_svg_viewer)




        # search for addons
        addons = QDirIterator(f'..{os.sep}..{os.sep}addons')

        while addons.hasNext():

            current = QDir(addons.next())
            addon_name = current.dirName()

            if not addon_name == '.' and not addon_name== '..':
                print(addon_name)
                # Create action
                self.open_tool_dict['QAction'] = QAction(addon_name, self)

                # Tool instance
                self.open_tool_dict['process'] = tool = globals()[addon_name]
                # https://zetcode.com/gui/pysidetutorial/menusandtoolbars/
                # self.open_tool_dict['QAction'].setShortcut('...')
                # self.open_tool_dict['QAction'].setStatusTip('...')

                self.open_tool_dict['QAction'].triggered.connect(lambda k=addon_name, t=tool:self.open_generic_tool(k, t))
                #

                # menubar = self.menuBar()
                # fileMenu = menubar.addMenu('&File')
                self.ui.menuTools.addAction(self.open_tool_dict['QAction'])

        # Treeview supplementary widgets
        self.ui.tree_file_browse_button.clicked.connect(self.browse_treeview)

        # Create an empty tab
        self.createTextTab()

    # Extra TabWidget
    def createTextTab(self, title=None):

        # Create QWidget
        new_tab = QWidget()

        # Adding correspondence
        self.widget_plaintextedit[new_tab] = CodeEditor()
        self.plaintextedit_path[self.widget_plaintextedit[new_tab]] = None

        # No text wraping
        self.widget_plaintextedit[new_tab].setLineWrapMode(QPlainTextEdit.NoWrap)

        # Define Layout
        layout = QHBoxLayout()

        # Set layout to QWidget
        new_tab.setLayout(layout)

        # Add QPlainTextEdit inside the layout
        layout.addWidget(self.widget_plaintextedit[new_tab])

        # Add Tab
        self.ui.tabWidget.addTab(new_tab, title)
    def delete_Tab(self, index):
        if self.maybe_save(index):
            # Retrieve widget
            widget = self.ui.tabWidget.widget(index)
            # Delete correspondence
            del self.widget_plaintextedit[widget]
            # Remove tab
            self.ui.tabWidget.removeTab(index)
    def simple_operation(self,command=None):

        current_widget = self.ui.tabWidget.currentWidget()
        current_plaintextedit = self.widget_plaintextedit[current_widget]
        if command == 'undo':
            current_plaintextedit.undo()
        elif command == 'redo':
            current_plaintextedit.redo()
        elif command == 'select all':
            current_plaintextedit.selectAll()
        elif command == 'cut':
            current_plaintextedit.cut()
        elif command == 'copy':
            current_plaintextedit.copy()
        elif command == 'paste':
            current_plaintextedit.paste()
        elif command == 'zoom in':
            current_plaintextedit.zoomIn()
        elif command == 'zoom out':
            current_plaintextedit.zoomOut()

    # Extra CodeEditor function
    def indexes(self):
        return [self.ui.tabWidget.indexOf(w) for w in self.widget_plaintextedit.keys()]
    def widgets(self):
        return [self.ui.tabWidget.widget(i) for i in self.indexes()]
    def paths(self):
        return [self.plaintextedit_path[self.widget_plaintextedit[w]] for w in self.widgets()]

    def closeEvent(self, event):
        # Inspiration
        # https://doc.qt.io/qtforpython/examples/example_widgets_richtext_textedit.html
        condition = True
        widgets = self.widgets()

        # verify if tabs contents have been change
        for widget in widgets:
            if self.widget_plaintextedit[widget].document().isModified():
                index = widgets.index(widget)
                condition = self.maybe_save(index)

        if condition:
            event.accept()
        else:
            event.ignore()
    def load(self, file_path):
        # Does it exists
        if not QFile.exists(file_path):
            return False

        # Qfile object
        file = QFile(file_path)


        if not file.open(QFile.ReadOnly):
            return False

        try:
            # Can it be decodec in utf8
            data = file.readAll()
            text = data.data().decode('utf8')

        except UnicodeDecodeError as error:
            # When file can't be decoded in utf8
            notification = QMessageBox()
            notification.setIcon(QMessageBox.Warning)
            notification.setWindowTitle('Warning')
            notification.setText(f"Unexpected {type(error)=}\nUnsupported encoding")
            notification.exec()
            return False

        index = None
        indexes = self.indexes()
        widgets = self.widgets()
        paths = self.paths()

        # Verify if there is an empty tab
        # empty title is enough to decide the emptiness of the tab

        # verify uniqueness
        if file_path in paths:
            widget = widgets[paths.index(file_path)]

        else:
            # verify if tabWidget empty
            if self.ui.tabWidget.count() == 0:
                # Create empty tab
                self.createTextTab()

                # by default the first tab have index 0
                index = 0

            for i, w in zip(indexes, widgets):

                if self.ui.tabWidget.tabText(i) in [None, '']:
                    index = i
                    i = indexes[-1]

            if index == None:
                self.createTextTab()
                index = indexes[-1] + 1

            # Retrieve page
            widget = self.ui.tabWidget.widget(index)

            # Retrieve object
            plaintextedit = self.widget_plaintextedit[widget]

            # Storing path
            self.plaintextedit_path[plaintextedit] = file_path

            # tab title
            title = os.path.basename(os.path.normpath(file_path))

            # Set title
            self.ui.tabWidget.setTabText(index, title)

            # Set data
            plaintextedit.setPlainText(text)

        self.ui.tabWidget.setCurrentWidget(widget)
        # self.statusBar().showMessage(f'Opened "{f}"')

        return True
    def maybe_save(self, index):
        widget = self.ui.tabWidget.widget(index)

        if not self.widget_plaintextedit[widget].document().isModified():
            return True

        self.ui.tabWidget.setCurrentWidget(widget)
        ret = QMessageBox.warning(self, QCoreApplication.applicationName(),
                                  "The document has been modified.\n"
                                  "Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard
                                  | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            return self.file_save()

        if ret == QMessageBox.Cancel:
            return False

        return True

    # File menu slot
    @Slot()
    def file_new(self):
        self.createTextTab()
    @Slot()
    def file_open(self):
        file_dialog = QFileDialog(self, "Open File...")
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        # file_dialog.setMimeTypeFilters(MIME_TYPES)
        if file_dialog.exec() != QDialog.Accepted:
            return

        fn = file_dialog.selectedFiles()[0]
        native_fn = QDir.toNativeSeparators(fn)
        if self.load(fn):
            self.statusBar().showMessage(f'Opened "{native_fn}"')

        else:
            self.statusBar().showMessage(f'Could not open "{native_fn}"')
    @Slot()
    def file_save(self):
        # Save the current open tab
        current_widget = self.ui.tabWidget.currentWidget()
        current_plaintextedit = self.widget_plaintextedit[current_widget]
        current_path = self.plaintextedit_path[current_plaintextedit]

        if current_path in [None, ''] or current_path.startswith(":/"):
            return self.file_save_as()

        writer = QTextDocumentWriter(current_path)
        document = current_plaintextedit.document()
        success = writer.write(document)
        native_fn = QDir.toNativeSeparators(current_path)

        if success:
            document.setModified(False)
            self.statusBar().showMessage(f'Wrote "{native_fn}"')

        else:
            self.statusBar().showMessage(f'Could not write to file "{native_fn}"')

        return success
    @Slot()
    def file_save_as(self):
        # Save the current open tab
        current_widget = self.ui.tabWidget.currentWidget()
        current_index = self.ui.tabWidget.currentIndex()
        current_plaintextedit = self.widget_plaintextedit[current_widget]
        # current_path = self.plaintextedit_path[current_plaintextedit]

        file_dialog = QFileDialog(self, "Save as...")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        if file_dialog.exec() != QDialog.Accepted:
            return False

        self.plaintextedit_path[current_plaintextedit] = f = file_dialog.selectedFiles()[0]
        self.ui.tabWidget.setTabText(current_index, os.path.basename(os.path.normpath(f)))
        return self.file_save()


    # Help menu slot
    @Slot()
    def open_terminal(self):
        os.system("start cmd")

    # Edit menu slot
    @Slot()
    def find(self):

        if not 'text_search' in self.__dict__.keys():
            self.text_search = TextSearch(self)

        # self.text_search
        if self.text_search.isVisible():
            self.text_search.hide()

        else:
            self.text_search.show()
            self.text_search.focus()

    # Tool menu slot
    @Slot()
    def open_generic_tool(self, key, tool):

        if not 'key' in self.open_tool_dict.keys():
            self.open_tool_dict[key] = tool()

        if self.open_tool_dict[key].isVisible():
            self.open_tool_dict[key].hide()

        else:
            self.open_tool_dict[key].show()

    def open_generic_tool_tab(self, key, tool):

        # Create QWidget
        new_tab = QWidget()
        # Define Layout
        layout = QHBoxLayout()

        # Open new tab
        if not 'key' in self.open_tool_dict.keys():
            self.open_tool_dict[key] = tool()
            layout.addWidget(self.open_tool_dict[key])


        # Change tab
        else:
            pass
            # self.open_tool_dict[key].show()

        # Set layout to QWidget
        new_tab.setLayout(layout)

        # Add Tab
        self.ui.tabWidget.addTab(new_tab, key)



    # Extra Treeview
    def treeView_doubleClicked(self, index):
        idx = self.ui.model.index(index.row(), 1, index.parent())
        path = self.ui.model.filePath(idx)

        if os.path.isfile(path):
            # Display
            self.load(path)


    def browse_treeview(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", QDir.currentPath())

        if directory:
            if self.ui.tree_file_comboBox.findText(directory) == -1:
                self.ui.tree_file_comboBox.addItem(directory)

            self.ui.tree_file_comboBox.setCurrentIndex(self.ui.tree_file_comboBox.findText(directory))
            self.ui.model.setRootPath(directory)

            self.working_directory = directory

            self.ui.window.set_working_directory(self.working_directory)
    def apply_treeview(self):
        directory = self.ui.tree_file_comboBox.currentText()
        if directory:
            self.ui.model.setRootPath(directory)
            self.ui.treeView.setModel(self.ui.model)
            self.ui.treeView.setRootIndex(self.ui.model.index(directory))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())