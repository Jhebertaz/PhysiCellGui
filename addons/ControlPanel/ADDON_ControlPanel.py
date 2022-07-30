from PySide6.QtCore import QDir
from PySide6.QtWidgets import QDialog, QScrollArea, QVBoxLayout, QWidget, QLabel, QPushButton, QSizePolicy, \
    QDialogButtonBox, QHBoxLayout, QMdiArea

from script.extra_function import *

# basic info
filename = 'ADDON_ControlPanel.py'
path = os.path.realpath(__file__).strip(filename)

# Change directory for the script one
# os.chdir("C"+path)

# Refresh ui file
if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    # linux or OS X
    os.system(f"pyside6-uic {'C'+path}{os.sep}controlPanel.ui > {'C'+path}{os.sep}controlPanelUi.py")
elif sys.platform == "win32":
    # Windows
    os.system(f"pyside6-uic {'C'+path}{os.sep}controlPanel.ui -o {'C'+path}{os.sep}controlPanelUi.py")

from controlPanelUi import Ui_Dialog

sys.path.insert(1, 'C'+path+"../SvgViewer")
from ADDON_SvgViewer import SvgViewer as svg

sys.path.insert(1,path+"../../scr/python/custom")
from FileCopyProgress import QFileCopyProgress as QFCP


class ControlPanel(QDialog):

    def __init__(self, parent=None, option=False):
        super().__init__()

        self.parent = parent

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Control Panel GBM")

        # Horizontal layout for main widget
        self.ui.main_horizontal_layout = QHBoxLayout(self.ui.widget)

        # 
        self.working_directory = QDir.currentPath()
        
        # For button
        self.ui.formLayout = QVBoxLayout()
        
        # Left 
        self.ui.groupBox = QWidget()
        
        # Setting up for the widget
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.ui.groupBox.setSizePolicy(sizePolicy)
        self.ui.groupBox.setLayout(self.ui.formLayout)

        self.label = {}
        self.button = {}

        functions["run_simulation"] = lambda : self.simulation()
        functions["Clear"] = lambda : clear(self.working_directory)

        for key, value in functions.items():
            self.label[key] = QLabel(key)
            self.button[key] = QPushButton(key)
            self.button[key].clicked.connect(value)
            self.ui.formLayout.addWidget(self.button[key]) #, self.button[key])

        self.ui.scroll = QScrollArea()
        self.ui.main_horizontal_layout.addWidget(self.ui.scroll)

        self.ui.scroll.setWidget(self.ui.groupBox)
        self.ui.scroll.setWidgetResizable(True)
        self.ui.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.ui.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.ui.svgViewer = svg(option=False)

        self.ui.mdiArea = QMdiArea()
        self.ui.mdiArea.addSubWindow(self.ui.svgViewer)

        self.ui.main_horizontal_layout.addWidget(self.ui.mdiArea)
        self.ui.main_horizontal_layout.setStretch(1, 10)


        # Button box
        if option == True:
            self.ui.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.ui.verticalLayout.addWidget(self.ui.buttonBox)

            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.verticalLayout.setSpacing(0)
        self.ui.verticalLayout.setContentsMargins(0, 0, 0, 0)

    def set_working_directory(self, path):
        self.working_directory = path
        self.ui.svgViewer.set_working_directory(path=self.working_directory)


    def simulation(self):

        # Information
        sample_name = 'gbm-ov-tmz-immune-stroma-patchy-sample'
        executable_name = 'gbm_ov_tmz_immune_stroma_patchy.exe'
        # sample_name = 'gbm-ov-immune-stroma-patchy-sample'
        # executable_name = 'gbm_ov_immune_stroma_patchy.exe'
        program_path = self.working_directory
        data_source = os.path.join(self.working_directory, 'output')
        data_destination = r"C:\Users\Julien\Documents\test\normal"
        export_folder_name = "GBM_TMZ"
        # export_folder_name = "GBM"
        time_ = QDateTime.currentDateTime().toString(Qt.ISODate).replace(":", "_")
        export_folder_name += time_
        export_data_folder = os.path.join(data_destination, export_folder_name)
        plot_time_cell_number_script_path = os.path.join(self.parent.program_directory, "addons", "ControlPanel", "script", "plot_time_cell_number.py")

        ## Function

        # run simulation
        run_simulation = lambda arg1=program_path, arg2=sample_name,arg3=executable_name : os.system(f'start cmd /k  "make -C {arg1} {arg2} & make -C {arg1} & {arg1}{os.sep}{arg3}"')

        # Export files
        export_file= lambda parent_=self, source=data_source, destination=export_data_folder: QFCP(parent=parent_).copy_files(scr=source, dest=destination)
        # Make gif
        gif = lambda destination=export_data_folder: os.system(f'start cmd /c "magick convert {destination}/s*.svg {destination}/out.gif"')
        # Make plot_time_cell_number
        plot1 = lambda script_path=plot_time_cell_number_script_path, destination=export_data_folder, figure_dest=data_destination, project_name=export_folder_name:os.system(rf'start cmd /c "python {script_path} {destination} {figure_dest} {project_name}plot_time_cell_number"')
        # Make plot_concentration_chemokine
        plot2 = lambda script_path=plot_time_cell_number_script_path, destination=export_data_folder, figure_dest=data_destination, project_name=export_folder_name:os.system(rf'start cmd /c "python {script_path} {destination} {figure_dest} {project_name}plot_concentration_chemokine"')
        # Cleanup
        cleanup = lambda arg1=program_path:os.system(f'start cmd /c make -C {arg1} reset & make -C {arg1} reset & make -C {arg1} data-cleanup & make -C {arg1} clean"')



        run_simulation()
        task_list = [export_file, cleanup, gif, plot1, plot2]
        progress_bar = SimulationProgress(parent=self, end_task_list=task_list)







