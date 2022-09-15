#############
## Package ##
#############
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QMdiArea, QSizePolicy, QFrame, \
    QAbstractScrollArea, QVBoxLayout, QWidget

from script.extra_function import *

# basic info
filename = 'ADDON_SimulationWithPhysiCell.py'
path = os.path.realpath(__file__).strip(filename)

# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic {path}{os.sep}controlPanel.ui > {path}{os.sep}controlPanelUi.py")
elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic {'C' + path}{os.sep}controlPanel.ui -o {'C' + path}{os.sep}controlPanelUi.py")

from controlPanelUi import Ui_Dialog

class SimulationWithPhysiCell(QDialog):

    def __init__(self, parent=None, option=False):
        super().__init__()

        self.parent = parent
        self.information = {}

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Control Panel")

        # Horizontal layout for main widget
        self.ui.main_horizontal_layout = QHBoxLayout(self.ui.widget)

        # Current path
        self.working_directory = QDir.currentPath()

        # MDI Area where subwindows are
        self.test_vertical_layout = QVBoxLayout()

        self.test_widget = QWidget()
        self.test_widget.setLayout(self.test_vertical_layout)
        self.ui.mdiArea = QMdiArea()

        self.test_vertical_layout.addWidget(self.ui.mdiArea)

        ## Customize MDI Area
        self.ui.mdiArea.keyPressEvent = lambda e: SimulationWithPhysiCell.keyPressEvent(parent=self, event=e)
        self.ui.mdiArea.tileSubWindows()
        self.ui.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.ui.mdiArea.setTabsClosable(False)

        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ui.mdiArea.sizePolicy().hasHeightForWidth())

        self.ui.mdiArea.setSizePolicy(sizePolicy1)
        self.ui.mdiArea.setFrameShape(QFrame.StyledPanel)
        self.ui.mdiArea.setFrameShadow(QFrame.Sunken)
        self.ui.mdiArea.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.mdiArea.setTabsMovable(True)


        # Shortcut to organize subwindows
        self.shortcut_tiling = QShortcut(QKeySequence('Ctrl+T'), self)
        self.shortcut_tiling.activated.connect(lambda: self.shortcut_mdi(option='tiling'))

        # Shortcut to cascade subwindows
        self.shortcut_cascade = QShortcut(QKeySequence('Ctrl+Shift+T'), self)
        self.shortcut_cascade.activated.connect(lambda: self.shortcut_mdi(option='cascade'))

        # Use one predefined configuration
        self.configuration = Configuration1(parent=self)
        self.configuration.init_configuration_1()


        for k, v in self.configuration.subwindows_init.items():
            v['widget'].setWindowTitle(k)

            if v['layout']:
                v['widget'].setLayout(v['layout'])

            self.ui.mdiArea.addSubWindow(v['widget'], Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint)


        self.ui.main_horizontal_layout.addWidget(self.test_widget)
        self.ui.main_horizontal_layout.setStretch(1, 10)

        # Button box
        if option == True:
            self.ui.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.ui.verticalLayout.addWidget(self.ui.buttonBox)

            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)

        # self.ui.verticalLayout.setSpacing(0)
        # self.ui.verticalLayout.setContentsMargins(0, 0, 0, 0)

    def set_working_directory(self, path):
        self.working_directory = path

    def shortcut_mdi(self, option):
        if option == 'tiling':
            self.ui.mdiArea.tileSubWindows()
        if option == 'cascade':
            self.ui.mdiArea.cascadeSubWindows()
        return

    @staticmethod
    # Prevent closing control panel by pressing esc key
    def keyPressEvent(parent, event=None):
        if event:
            if (event.key() != Qt.Key_Escape):
                parent.keyPressEvent(event)
        return None
