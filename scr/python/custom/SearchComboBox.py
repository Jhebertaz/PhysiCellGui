from PySide6.QtCore import QDir
from PySide6.QtWidgets import QHBoxLayout, QComboBox, QPushButton, QSizePolicy, QFileDialog, QWidget


class SearchComboBox(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create layout
        self.horizontal_layout = QHBoxLayout()
        # self.horizontal_layout.addStretch(1)
        self.horizontal_layout.setContentsMargins(0,0,0,0)
        self.horizontal_layout.setSpacing(0)

        # Combo box
        #QDir.currentPath()
        self._directory_combo_box = self.create_combo_box()

        # Search button
        self._browse_button = self.create_button("&Browse...", self.browse)

        # Size policy
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self._directory_combo_box.setSizePolicy(sizePolicy)
        self._browse_button.setSizePolicy(sizePolicy)

        # Adding widgets to layout
        self.horizontal_layout.addWidget(self._directory_combo_box)
        self.horizontal_layout.addWidget(self._browse_button)

        # Set stretch
        self.horizontal_layout.setStretch(0,3)
        self.horizontal_layout.setStretch(1,1)


        # Set layout to widget
        self.setLayout(self.horizontal_layout)

    @staticmethod
    def update_combo_box(comboBox):
        if comboBox.findText(comboBox.currentText()) == -1:
            comboBox.addItem(comboBox.currentText())
    def create_button(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button
    def create_combo_box(self, text=""):
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.addItem(text)
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return combo_box
    def browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Directory", QDir.currentPath())

        if directory:
            if self._directory_combo_box.findText(directory) == -1:
                self._directory_combo_box.addItem(directory)

            self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(directory))
    def set_working_directory(self, path):
        self.working_directory = path
        self._directory_combo_box.addItem(path)
        self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(path))
    def text(self):
        return self._directory_combo_box.currentText()
    def setText(self, directory):

        if directory:
            if self._directory_combo_box.findText(directory) == -1:
                self._directory_combo_box.addItem(directory)

            self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(directory))