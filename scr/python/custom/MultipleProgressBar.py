#############
## Package ##
#############
from PySide6.QtWidgets import QWidget, QFormLayout, QProgressBar, QLabel


class MultipleProgressBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.layout = QFormLayout()

        self.setLayout(self.layout)
        self.element = {}

        # arg are string that represent the name of the progress bar
        for arg in args:
            self.add_progress_bar(arg)

    def add_progress_bar(self, name):
        self.element[name] = {
            'progress_bar' : QProgressBar(),
            'label': QLabel()
        }
        for key, value in self.element[name].items():
            self.layout.addRow(name, value)

    def add_element(self, element, name):
        # element : {Widget, Label}
        self.element[name] = element
        for key, value in self.element[name].items():
            if value:
                self.layout.addRow(name, value)
