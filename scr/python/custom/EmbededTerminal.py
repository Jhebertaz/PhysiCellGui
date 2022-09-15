import sys
import os
# # https://learndataanalysis.org/source-code-create-a-simple-python-app-to-run-command-lines-commands-pyqt5-tutorial/
# # https://www.youtube.com/watch?v=LHX-09SBBtg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QPushButton, QApplication


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1200, 1500
        self.setMinimumSize(self.window_width, self.window_height)




        self.counter = 0

        self.setWindowTitle('Command Line App')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.editorCommand = QPlainTextEdit()
        layout.addWidget(self.editorCommand, 3)

        self.editorOutput = QPlainTextEdit()
        self.editorOutput.textChanged.connect(self.changeCounter)
        layout.addWidget(self.editorOutput, 7)

        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)

        self.button_run = QPushButton('&Run Command', clicked=self.runCommand)
        buttonLayout.addWidget(self.button_run)

        self.button_clear = QPushButton('&Clear', clicked=lambda: self.editorOutput.clear())
        buttonLayout.addWidget(self.button_clear)

        self.editorCommand.insertPlainText('dir')
    def changeCounter(self):

        self.counter +=1
        print(self.counter)
    def runCommand(self):
        command_line = self.editorCommand.toPlainText().strip()
        p = os.popen(command_line)
        if p:
            self.editorOutput.clear()
            output = p.read()
            self.editorOutput.insertPlainText(output)


if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # os.chdir(r"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1")
    os.chdir(r"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.6.0")
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 30px;
        }
    ''')

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')