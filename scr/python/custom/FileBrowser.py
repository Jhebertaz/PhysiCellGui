from PySide6.QtCore import (QCoreApplication, QDir, QFile, QFileInfo,
                            QIODevice, QTextStream, QUrl, Qt, QDirIterator)
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QAbstractItemView, QComboBox,
                               QDialog, QFileDialog, QGridLayout, QHBoxLayout,
                               QHeaderView, QLabel, QProgressDialog,
                               QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QCheckBox)


class FileBrowser(QDialog):
    # Inspiration for the documentation example
    # https://doc.qt.io/qtforpython/examples/example_widgets_dialogs_findfiles.html
    def __init__(self, parent=None):
        super().__init__(parent)

        self._browse_button = self.create_button("&Browse...", self.browse)
        self._find_button = self.create_button("&Find", self.find)
        self._check_box = QCheckBox("include subfiles", self)

        self._file_combo_box = self.create_combo_box("*")
        self._text_combo_box = self.create_combo_box()
        self._directory_combo_box = self.create_combo_box(QDir.currentPath())

        file_label = QLabel("Named:")
        text_label = QLabel("Containing text:")
        directory_label = QLabel("In directory:")
        self._files_found_label = QLabel()

        self.create_files_table()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._find_button)
        buttons_layout.addWidget(self._check_box )

        main_layout = QGridLayout()
        main_layout.addWidget(file_label, 0, 0)
        main_layout.addWidget(self._file_combo_box, 0, 1, 1, 2)
        main_layout.addWidget(text_label, 1, 0)
        main_layout.addWidget(self._text_combo_box, 1, 1, 1, 2)
        main_layout.addWidget(directory_label, 2, 0)
        main_layout.addWidget(self._directory_combo_box, 2, 1)
        main_layout.addWidget(self._browse_button, 2, 2)
        main_layout.addWidget(self._files_table, 3, 0, 1, 3)
        main_layout.addWidget(self._files_found_label, 4, 1)
        main_layout.addLayout(buttons_layout, 5, 0, 1, 3)

        self.setLayout(main_layout)

        self.setWindowTitle("Find Files")
        self.resize(500, 300)

    @staticmethod
    def update_combo_box(comboBox):
        if comboBox.findText(comboBox.currentText()) == -1:
            comboBox.addItem(comboBox.currentText())
    def browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", QDir.currentPath())

        if directory:
            if self._directory_combo_box.findText(directory) == -1:
                self._directory_combo_box.addItem(directory)

            self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(directory))
    def find(self):
        self._files_table.setRowCount(0)

        file_name = self._file_combo_box.currentText()
        text = self._text_combo_box.currentText()
        path = self._directory_combo_box.currentText()

        self.update_combo_box(self._file_combo_box)
        self.update_combo_box(self._text_combo_box)
        self.update_combo_box(self._directory_combo_box)

        # Not searching in subfolders
        if not self._check_box.checkState():
            self._current_dir = QDir(path)
            if not file_name:
                file_name = "*"
            files = self._current_dir.entryList(["*"+file_name, file_name, file_name+"*"], QDir.Files | QDir.NoSymLinks)

        # Searching in subfolders
        # It would be faster with four threads or more.
        else:
            if not file_name:
                file_name = "*"
            self._current_dir = QDir(path)
            self._current_dir.setFilter(QDir.Files or QDir.NoDotAndDotDot)
            self._current_dir.setSorting(QDir.Name)
            dit = QDirIterator(path, ["*"+file_name, file_name, file_name+"*"], QDir.Files or QDir.NoDotAndDotDot, QDirIterator.Subdirectories | QDir.Files)
            files = []

            while dit.hasNext():
                im = self._current_dir.relativeFilePath(dit.next())
                files.append(im)

        if text:
            files = self.find_files(files, text)
        self.show_files(files)
    def find_files(self, files, text):
        progress_dialog = QProgressDialog(self)

        progress_dialog.setCancelButtonText("&Cancel")
        progress_dialog.setRange(0, len(files))
        progress_dialog.setWindowTitle("Find Files")

        found_files = []

        for i in range(len(files)):
            progress_dialog.setValue(i)
            n = len(files)
            progress_dialog.setLabelText(f"Searching file number {i} of {n}...")
            QCoreApplication.processEvents()

            if progress_dialog.wasCanceled():
                break

            in_file = QFile(self._current_dir.absoluteFilePath(files[i]))

            if in_file.open(QIODevice.ReadOnly):
                stream = QTextStream(in_file)
                while not stream.atEnd():
                    if progress_dialog.wasCanceled():
                        break
                    line = stream.readLine()
                    if text in line:
                        found_files.append(files[i])
                        break

        progress_dialog.close()

        return found_files
    def show_files(self, files):
        for fn in files:
            file = QFile(self._current_dir.absoluteFilePath(fn))
            size = QFileInfo(file).size()

            file_name_item = QTableWidgetItem(fn)
            file_name_item.setFlags(file_name_item.flags() ^ Qt.ItemIsEditable)
            size_kb = int((size + 1023) / 1024)
            size_item = QTableWidgetItem(f"{size_kb} KB")
            size_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            size_item.setFlags(size_item.flags() ^ Qt.ItemIsEditable)

            row = self._files_table.rowCount()
            self._files_table.insertRow(row)
            self._files_table.setItem(row, 0, file_name_item)
            self._files_table.setItem(row, 1, size_item)

        n = len(files)
        self._files_found_label.setText(f"{n} file(s) found (Double click on a file to open it)")
    def create_button(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button
    def create_combo_box(self, text=""):
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.addItem(text)
        combo_box.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)
        return combo_box
    def create_files_table(self):
        self._files_table = QTableWidget(0, 2)
        self._files_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._files_table.setHorizontalHeaderLabels(("File Name", "Size"))
        self._files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._files_table.verticalHeader().hide()
        self._files_table.setShowGrid(False)

        self._files_table.cellActivated.connect(self.open_file_of_item)
    def open_file_of_item(self, row, column):
        item = self._files_table.item(row, 0)

        QDesktopServices.openUrl(QUrl(self._current_dir.absoluteFilePath(item.text())))
    def set_working_directory(self, path):
        self._directory_combo_box.addItem(path)
        self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(path))

