import os
import shutil
import sys
import time

import numpy as np
import pandas as pd
import pyqtgraph as pg
import scipy.io
import xmltodict
from PySide6.QtCore import QFile, QCoreApplication, QTimer, QDir
from PySide6.QtWidgets import QFileDialog, QInputDialog, QProgressDialog, QTreeWidget, QTreeWidgetItem, QTableWidget, \
    QWidget, QFormLayout, QLineEdit, QPushButton, QAbstractItemView, QTableWidgetItem, QHeaderView, QMessageBox, \
    QTabWidget

# basic info

filename = 'extra_function.py'
path = os.path.realpath(__file__).strip(filename)

sys.path.insert(1, path)
from .plot_initial_state import plot_initial_state as pis
from .plot_time_cell_number import plot_time_cell_number as ptcn
from .plot_concentration_chemokine import plot_concentration_chemokine as pcc

# import svg viewer from addons
sys.path.insert(1, os.path.join(path ,'..','..','SvgViewer'))
from ADDON_SvgViewer import SvgViewer as svg

# import from custom
sys.path.insert(1, os.path.join(path, '..', '..', '..', 'scr', 'python', 'custom'))
from FileCopyProgress import QFileCopyProgress as QFCP
from SearchComboBox import SearchComboBox as sc






# gbm_ov_immune_stroma_patchy_old_new
# gbm_ov_immune_stroma_patchy_old
# gbm_ov_immune_stroma_patchy



# Simple progress bar
class SimulationProgress(QProgressDialog):

    def __init__(self, parent=None, counter_end=144, data_source_folder=None, *args, **kwargs):
        super().__init__(parent)

        self.start_time = 0

        self.end_time = 0
        self.time_delta = []

        self.counter = 0
        self.counter_end = counter_end

        self.data_source_folder = data_source_folder

        # Ordered ending task list
        if not "end_task_list" in kwargs.keys():
            self.end_task_list = [lambda: None]
        else:
            self.end_task_list = kwargs['end_task_list']

        # Ordered recuring task list
        if not "recuring_task_list" in kwargs.keys():
            self.recuring_task_list = [lambda: None]
        else:
            self.recuring_task_list = lambda: kwargs['recuring_task_list']()

        self.setRange(0, self.counter_end)
        self.setWindowTitle("Simulation progress")


        self.timer = QTimer()
        self.timer.setInterval(500)

        self.timer.timeout.connect(self.recurring_function)
        self.timer.timeout.connect(self.update_estimating_time)
        self.timer.start()
        self.show()

    # TODO : make it usuable outside of this specific situation
    def recurring_function(self):

        if self.wasCanceled():
            self.timer.stop()
            self.close()
            return
        if not QFile.exists(os.path.join(self.data_source_folder,"final.svg")):

            # check for the lastest every sec svg file and took is number
            n = self.counter + 1
            filename = 'snapshot' + "%08i" % n + '.svg'

            if QFile.exists(os.path.join(self.data_source_folder, filename)):
                self.counter += 1
                self.end_time = time.time()
                self.update_estimating_time()

                self.start_time = time.time()

                self.setValue(self.counter)
                # TODO : plot1

                QCoreApplication.processEvents()
            self.update_estimating_time()


        else:
            self.timer.stop()
            self.close()
            self.end_function()

    def end_function(self):
        for task in self.end_task_list:
            task()
        return "DONE"

    def update_estimating_time(self):

        delta_time = abs(self.end_time - self.start_time)
        delta_step = abs(self.counter_end - self.counter)
        total_time = delta_time * delta_step

        min = round(total_time) // 60
        sec = round(abs(total_time - 60 * min))

        if min > 0 and sec > 0:
            self.setLabelText(f"Estimated time before finishing {min} min {round(sec)} sec")
# Data from collaborators conversion and manipulation
class Data:
    def __init__(self):
        self.temp_dict = {
            'Th': 1,
            'Cancer': 2,
            'Tc': 3,
            'Cl BMDM': 5,
            'Cl MG': 5,
            'Alt BMDM': 6,
            'Alt MG': 6,
            'Endothelial cell': 4
        }
        pass

    @staticmethod
    def ind2sub(sz, ind):
        x, y = np.unravel_index(ind, sz, order='F')
        y = np.array([[yy[0] + 1] for yy in y])
        return x, y

    @staticmethod
    def median_ind2sub(sz, ind):
        x, y = Data.ind2sub(sz, ind)
        return np.median(x), np.median(y)

    @staticmethod
    def mean_ind2sub(sz, ind):
        x, y = Data.ind2sub(sz, ind)
        return np.mean(x), np.mean(y)

    @staticmethod
    def x_y_position_type(position_file, cell_type_file, center=500, type_dict=None):
        mat1 = scipy.io.loadmat(position_file)
        mat2 = scipy.io.loadmat(cell_type_file)

        cell_number = mat2['cellTypes'].size

        # shape of the matrix
        size = mat1['nucleiImage'].shape

        for i in range(cell_number):

            # cell type
            try:
                c_t = mat2['cellTypes'][i][0][0]

                if type_dict:
                    if c_t in type_dict.keys():
                        cell_type = type_dict[c_t]
                    else:
                        cell_type = None
            except:
                cell_type = None

            if cell_type:
                # ith cell's boundaries
                cell_boudaries = mat1['Boundaries'][0][i]


                # median position of the cell
                x, y = Data.mean_ind2sub(size, cell_boudaries)

                cell_position = [round(x - center,4), round(y - center,4), 0, cell_type]
                # print(*([i]+cell_position), sep='\t\t\t\t')
                yield cell_position

    @staticmethod
    def convert_to_csv(destination, filename, data):
        np.savetxt(os.path.join(destination, f"{filename}.csv"), data, delimiter=",", fmt='%s')

    @staticmethod
    def create_dirtree_without_files(src, dst):
        # getting the absolute path of the source
        # directory
        src = os.path.abspath(src)

        # making a variable having the index till which
        # src string has directory and a path separator
        src_prefix = len(src) + len(os.path.sep)

        # making the destination directory
        os.makedirs(dst)

        # doing os walk in source directory
        for root, dirs, files in os.walk(src):
            for dirname in dirs:
                # here dst has destination directory,
                # root[src_prefix:] gives us relative
                # path from source directory
                # and dirname has folder names
                dirpath = os.path.join(dst, root[src_prefix:], dirname)

                # making the path which we made by
                # joining all of the above three
                os.mkdir(dirpath)

    @staticmethod
    def data_conversion_segmentation_celltypes(source, destination, type_dict=None):
        try:
            dest = os.path.join(destination, source.split(os.sep)[-1])
            Data.create_dirtree_without_files(source, dest)
        except:

            print("overwriting")
            shutil.rmtree(dest)
            Data.create_dirtree_without_files(source, dest)

        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(source):
            path = root.split(os.sep)

            for file in files:
                if 'nuclei_multiscale.mat' in file:
                    f_path = os.path.join(*([f"C:{os.sep}"] + path[1::] + [file]))
                    print(f_path)
                    position_file = f_path

                    # For each scan segmentation have a folder, not for celltypes
                    # we have one layer to substract
                    cell_type_file = os.path.join(*([f"C:{os.sep}"] + path[1::])).replace('Segmentation',
                                                                                          'CellTypes') + '.mat'

                    # data
                    data = np.asarray([item for item in Data.x_y_position_type(position_file, cell_type_file,type_dict=type_dict)])

                    # Construct destination path
                    idx = path.index('Segmentation')
                    relative_path = os.path.join(*(path[idx::]))
                    absolute_path = destination

                    dst = os.path.join(absolute_path, relative_path)

                    # filename
                    # filename = file.replace('.mat', '')
                    filename = path[-1].split(' ')[-1]

                    # convert_to_csv
                    Data.convert_to_csv(dst, filename, data)
                    # print(os.path.join(dst, filename))

    @staticmethod
    def scan_csv_file(source, name=None):
        file_list = []
        condition = None
        if name:
            condition = lambda f: (name in f) and ('.csv' in f)
        else:
            condition = lambda f: ('.csv' in f)
        for root, dirs, files in os.walk(source):
            path = root.split(os.sep)

            for file in files:
                if condition(file):
                    file_list.append(os.path.join(root,file))
        return file_list

    @staticmethod
    def loadFiles(start_directory=None):
        # filter = "TXT (*.txt);;PDF (*.pdf)"
        parent = None
        filter = "CSV (*.csv)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        names = file_name.getOpenFileNames(parent, "Open files", start_directory, filter)
        if not names[0]:
            return False

        return names[0]
# Simulation instance to facilitate series of simulation
class Simulation:
    def __init__(self, *args, **kwargs):

        self.kwargs = kwargs
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        # *args should be function in order
        self.args = args

        self.basic_task = []

        if 'data_destination_folder' in kwargs and 'data_source_folder' in kwargs:
            self.basic_task.append(lambda: self.__setattr__('data_destination', Simulation.specific_export_output(**kwargs)))
            # self.basic_task.append(lambda: Simulation.make_gif(self.data_destination, self.data_destination))

        # if 'program_path' in kwargs:
        #     self.basic_task.append(lambda:Simulation.cleanup(kwargs["program_path"]))

    def start_simulation(self):
        Simulation.cleanup(**self.kwargs)
        Simulation.run_simulation(**self.kwargs)
        SimulationProgress(**self.kwargs, end_task_list=self.basic_task+list(self.args))
        return True

    def verification(self, *args, **kwargs):
        ok_bool_list = [True]
        param = self.kwargs
        for k, v in param.items():
            if not v:
                if k in ['suffix', 'csv_files']:
                    ok_bool_list.append(True)
                else:
                    ok_bool_list.append(False)
        return not (False in ok_bool_list)



    @staticmethod
    def cleanup(program_path, *args, **kwargs):
        # os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
        os.system(f'start cmd /c make -C {program_path} reset & make -C {program_path} reset & make -C {program_path} data-cleanup & make -C {program_path} clean"')
        return True
    @staticmethod
    def run_simulation(program_path, project_name, executable_name,*args,**kwargs):
        executable_path = os.path.abspath(os.path.join(program_path,executable_name))
        os.system(f'start cmd /k  "make -C {program_path} {project_name} & make -C {program_path} & {executable_path}"')  # to keep cmd open --> cmd /k and /c for closing after task
        return True
    @staticmethod
    def make_gif(data_source_folder, data_destination_folder,*args, **kwargs):
        os.system(f'start cmd /c "magick convert {data_source_folder}/s*.svg {data_destination_folder}/out.gif"')
        return f"{data_destination_folder}/out.gif"
    @staticmethod
    def specific_export_output(data_source_folder=None, data_destination_folder=None, *args, **kwargs):
        if not data_source_folder:
            data_source_folder = QFileDialog.getExistingDirectory(None, "Select Directory Source")
        if not data_destination_folder:
            data_destination_folder = QFileDialog.getExistingDirectory(None, "Select Directory Destination")

        if data_source_folder and data_destination_folder:
            insta = QFCP()
            insta.copy_files(scr=data_source_folder, dest=data_destination_folder)

        return data_destination_folder

    @staticmethod
    def test_param_dictionnary():
        param = {
            'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
            'project_name': "gbm-ov-tmz-immune-stroma-patchy-sample",
            'executable_name': "gbm_ov_tmz_immune_stroma_patchy.exe",
            'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
            'data_destination_folder': r"C:\Users\VmWin\Pictures\test\gbm_ov_tmz_immune_stroma_patchy_sample_2022-08-03T09_42_54",
            'suffix': "2022-08-03T09_42_54",
            'xml_template_file': r"C:\Users\VmWin\Pictures\test\template.xml",
            'csv_files': [r"C:\Users\VmWin\Pictures\test\Segmentation\Project 1 ICI glioma IMC\20200617\OneDrive_10_7-7-2020-1\Pano 01_Col2-3_1_ROI 05_X17-343-B2_5\05_X17-343-B2_5.csv"],
            'configuration_files_destination_folder':r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov_tmz_immune_stroma_patchy\config",
            'counter_end': 144
        }
        return param
    @staticmethod
    def empty_param_dictionnary():
        param = {
            'program_path': None,
            'project_name': None,
            'executable_name': None,
            'data_source_folder': None,
            'data_destination_folder': None,
            'suffix': None,
            'xml_template_file':None,
            'csv_files': [],
            'configuration_files_destination_folder':None,
            'counter_end': 0
        }
        return param
    @staticmethod
    def type_dict():
        temp_dict = {
            'Th': 1,
            'Cancer': 2,
            'Tc': 3,
            'Cl BMDM': 5,
            'Cl MG': 5,
            'Alt BMDM': 6,
            'Alt MG': 6,
            'Endothelial cell': 4
        }
        return temp_dict
    @staticmethod
    def reverse_type_dict():
        temp_dict2 = {
            1: 'Th',
            2: 'Cancer',
            3: 'Tc',
            5: 'Cl BMDM/MG',
            6: 'Alt BMDM/MG',
            4: 'Endothelial cell'
        }
        return temp_dict2

# Plotting tool
class Plotting:
    def __init__(self, *args, **kwargs):

        # plot information
        self.kwargs = kwargs
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.args = args

    @staticmethod
    def outside_ready_to_plot_function(*args, **kwargs):
        """return a ready_to_run function"""
        return lambda:Plotting.outside_plot_function(*args, **kwargs)

    @staticmethod
    def inside_ready_to_plot_function(*args, **kwargs):
        """return a ready_to_run function"""
        return lambda: Plotting.plot_function(*args, **kwargs)

    @staticmethod
    def get_script_name(script_path):
        """Retrieve script_name from path"""
        return os.path.abspath(script_path).split(os.sep)[-1].replace('.py', '')

    @staticmethod
    def get_figure_name(script_name, *args, **kwargs):
        """Figure naming schema : script_name_arg1_arg2..."""
        return script_name+"_".join(args)

    @staticmethod
    def outside_plot_function(*args, **kwargs):
        # script_path, data_source_folder, data_destination_folder, figure_name ,... in order
        arguments_in_string = ' '.join(map(str, list(args)+list(kwargs.values())))
        # os.system(f"""start cmd /k 'python {arguments_in_string} ' """)
        os.system(f"""start cmd /c python {arguments_in_string} """)
        return True

    @staticmethod
    def inside_plot_function(*args, **kwargs):
        plot_type = {"plot_concentration_chemokine":lambda *argss, **kwargss : pcc(*argss, **kwargss),
                     "plot_initial_state":lambda *argss, **kwargss :pis(*argss, **kwargss),
                     "plot_time_cell_number":lambda *argss, **kwargss :ptcn(*argss, **kwargss)}

        if 'plot_type' in kwargs:
            figure_path, fig, argument, legend= plot_type[kwargs['plot_type']](*args, **kwargs)

            return figure_path, fig, argument, legend






# Config file manipulation
class Config:
    def __init__(self, *args, **kwargs):

        self.kwargs = kwargs
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.args = args
        self.dict_from_xml = self.dict_form()
        self.xml_from_dict = self.xml_form()

    def xml_form(self):
        if 'data' in self.kwargs:
            # From conversion of dict to xml
            self.dict_from_xml = Config.dict2xml(self.kwargs['data'])

            return self.xml_from_dict
        else:
            return False
    def dict_form(self):
        if 'file' in self.kwargs:
            # From conversion of xml to dict
            self.dict_from_xml = Config.xml2dict(self.kwargs['file'])
            return self.dict_from_xml
        else:
            return False
    def list_user_parameters(self):
        if self.dict_from_xml == {}:
            self.dict_form()

        arguments = ['PhysiCell_settings', 'user_parameters']
        karguments = {'dictionary': self.dict_from_xml}

        return Config.get2dict(*arguments, **karguments)
    def list_cell(self):
        if self.dict_from_xml == {}:
            self.dict_form()

        arguments = ['PhysiCell_settings', 'cell_definitions', 'cell_definition']
        karguments = {'dictionary': self.dict_from_xml}

        return list(map(lambda p: p['@name'], Config.get2dict(*arguments, **karguments)))
    def change_user_parameters(self, *args, new_value=None):
        # subnode possibility:
        # '@type'
        # '@units'
        # '@description'
        # '#text'

        arguments = ['PhysiCell_settings', 'user_parameters'] + list(args)
        karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
        Config.edit2dict(*arguments, **karguments)
    def change_microenvironment_physical_parameter_set(self, *args, name=None, new_value=None):
        idx = Config.find_variable_index(data=self.dict_from_xml, name=name)
        if idx:
            arguments = ['PhysiCell_settings', 'microenvironment_setup', 'variable', idx,
                         'physical_parameter_set'] + list(args)
            karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
            Config.edit2dict(*arguments, **karguments)
            return True
        else:
            return False
    def change_cell_definition_phenotype(self, *args, name=None, new_value=None):
        idx = Config.find_cell_index(data=self.dict_from_xml, name=name)
        if idx:
            arguments = ['PhysiCell_settings', 'cell_definitions', 'cell_definition', idx, 'phenotype'] + list(args)
            karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
            Config.edit2dict(*arguments, **karguments)
            return True
        else:
            return False
    def change_cell_definition_custom_data(self, *args, name=None, new_value=None):
        idx = Config.find_cell_index(data=self.dict_from_xml, name=name)
        if idx:
            arguments = ['PhysiCell_settings', 'cell_definitions', 'cell_definition', idx, 'custom_data'] + list(args)
            karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
            Config.edit2dict(*arguments, **karguments)
        else:
            return False



    @staticmethod
    def xml2dict(xml_file, *args, **kwargs):
        xml = open(xml_file, "r")
        org_xml = xml.read()
        tree = xmltodict.parse(org_xml, process_namespaces=True)
        return tree
    @staticmethod
    def dict2xml(data, destination, xml_file_name, *args, **kwargs):
        out = xmltodict.unparse(data, pretty=True)
        with open(f"{destination}/{xml_file_name}.xml", 'w') as f:
            f.write(out)
    @staticmethod
    def find_variable_index(data, name):
        i = 0
        for var in data['PhysiCell_settings']['microenvironment_setup']['variable']:
            if not var['@name'] == name:
                i += 1
            else:
                return i
        return False
    @staticmethod
    def find_cell_index(data, name):
        i = 0
        for var in data['PhysiCell_settings']['cell_definitions']['cell_definition']:
            if not var['@name'] == name:
                i += 1
            else:
                return i
        return False
    @staticmethod
    def get2dict(*args, **kwargs):
        """From every argument, retrieve the value in the dictionary"""
        dictionary = kwargs['dictionary']
        if len(args) == 0:
            return

        if len(args) == 1:
            return dictionary[args[0]]
        else:
            return Config.get2dict(*args[1::], **{'dictionary': dictionary[args[0]]})
    @staticmethod
    def edit2dict(*args, **kwargs):
        """

        :param args: str, str, ....
        :param kwargs: dictionary=dict, new_value=...

        Example we want to change dicto['un']['deux1']['quatre']['cinq1'] to 13
        dicto = {'un': {'deux1':{'trois1':31,'quatre':{'cinq1':51,'six1':61}},'deux2':22}, 'deux':{'trois1':31,'quatre':{'cinq1':51,'six1':61}},'deux2':22}
        arc = ['un','deux1','quatre','cinq1']

        edit2dict(*arc, **{'dictionary':dicto, 'new_value':13})

        Before
        ------------------------------------------------------------------------------------------------------------------------
        {'un': {'deux1': {'trois1': 31, 'quatre': {'cinq1': 51, 'six1': 61}}, 'deux2': 22}, 'deux': {'trois1': 31, 'quatre': {'cinq1': 51, 'six1': 61}}, 'deux2': 22}
        ------------------------------------------------------------------------------------------------------------------------
        After
        ------------------------------------------------------------------------------------------------------------------------
        {'un': {'deux1': {'trois1': 31, 'quatre': {'cinq1': 13, 'six1': 61}}, 'deux2': 22}, 'deux': {'trois1': 31, 'quatre': {'cinq1': 51, 'six1': 61}}, 'deux2': 22}
        """
        dictionary = kwargs['dictionary']
        new_value = kwargs['new_value']
        if len(args) == 0:
            return
        if len(args) == 1:
            dictionary[args[-1]] = new_value
            return
        else:
            tmp = Config.get2dict(*args[:-1:], **{'dictionary': dictionary})
            tmp[args[-1]] = new_value
            Config.edit2dict(*args[:-1:], **{'dictionary': dictionary, 'new_value': tmp})
    @staticmethod
    def unit_test():
        file = r'C:\Users\VmWin\Pictures\test\PhysiCell_settings.xml'
        unit = {}
        print_test = lambda txt, cdn: print(txt + '-' * (90 - len(txt)), str(cdn))

        # load xml file
        test = Config(file=file)

        parameters_list = ["random_seed", "kappa", "c_s", "epsilon", "xhi",  "proportion", "p_max", "pbar_max", "rho_max", "f_F", "c_j_ccr", "A_frag", "R", "sigma", "mu", "eta", "K_V", "K_C", "r_10", "V_N_CD4", "N_CD4", "R_CD4", "r_01_CD4", "S_chemokine_CD4", "TH_prolif_increase_due_to_stimulus", "V_N_GBM", "R_GBM", "beta", "u_g", "N_GBM_sparse", "N_GBM_dense", "V_N_CD8", "N_CD8", "R_CD8", "r_01_CD8", "d_attach", "nu_max", "tau", "b_CD8", "CTL_prolif_increase_due_to_stimulus", "V_N_stromal", "R_stromal", "nu", "u_s", "N_stroma_sparse", "N_stroma_dense", "lambda_virus", "D_virus", "alpha", "delta_V", "gamma", "m_half", "rho_star_virus", "V_0", "lambda_chemokine", "D_chemokine", "nu_star", "rho_star_chemokine",  "lambda_tmz", "D_tmz", "IC50"]

        # list_user_parameters
        unit["list_user_parameters"] =  list(filter(lambda t: t[0]!=t[1], zip(test.list_user_parameters(), parameters_list))) == []

        # list_cell
        unit['list_cell'] = test.list_cell() == ['default','th', 'cancer', 'ctl', 'stromal']

        # change_user_parameters
        test.change_user_parameters('kappa', '#text', new_value=3223)
        unit['change_user_parameters'] = test.dict_from_xml['PhysiCell_settings']['user_parameters']['kappa']['#text'] == 3223

        # find_variable_index
        unit['find_variable_index'] = Config.find_variable_index(test.dict_from_xml, name='tmz') == 3

        # change_microenvironment_physical_parameter_set
        test.change_microenvironment_physical_parameter_set('diffusion_coefficient', '#text', name='tmz', new_value=46.1)
        unit['change_microenvironment_physical_parameter_set'] = test.dict_from_xml['PhysiCell_settings']['microenvironment_setup']['variable'][3]['physical_parameter_set']['diffusion_coefficient']['#text'] == 46.1

        # find_cell_index
        unit['find_cell_index'] = Config.find_cell_index(test.dict_from_xml, name='stromal') == 4

        # change_cell_definition_phenotype
        test.change_cell_definition_phenotype('cycle', 'phase_transition_rates', 'rate', '#text', name='stromal', new_value=1)
        unit['change_cell_definition_phenotype'] = test.dict_from_xml['PhysiCell_settings']['cell_definitions']['cell_definition'][4]['phenotype']['cycle']['phase_transition_rates']['rate']['#text'] == 1

        # change_cell_definition_custom_data
        test.change_cell_definition_custom_data('sample', '#text', name='stromal', new_value=2)
        unit['change_cell_definition_custom_data'] = test.dict_from_xml['PhysiCell_settings']['cell_definitions']['cell_definition'][4]['custom_data']['sample']['#text'] == 2

        for k, v in unit.items():
            print_test(k, v)
        return

# Help to display dictionnary into editable treeview
class ViewTree(QTreeWidget):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fill_item(self.invisibleRootItem(), value)
        self.latest_modify_element_path_value_dict = None
        self.doubleClicked.connect(self.edit_and_store_path_value_dict)

    def edit_and_store_path_value_dict(self):
        ok = bool()
        if not ViewTree.is_sub_tree(self.selectedItems()[0]):
            text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')

        if ok and text:
            path_value_dict = ViewTree.modify_element(self.selectedItems()[0], text)
            self.latest_modify_element_path_value_dict = path_value_dict

    @staticmethod
    def modify_element(qtreewidgetitem, new_value):
        # get the current item
        si = qtreewidgetitem
        # verify if it has a child
        if not ViewTree.is_sub_tree(si):
            if new_value:
                si.setText(0, new_value)
            # print(ViewTree.current_item_path(qtreewidgetitem))
            return ViewTree.current_item_path_value_dict(qtreewidgetitem)
        else:
            print("selected item have one or multiple child")

    @staticmethod
    def is_sub_tree(qtreewidgetitem):

        if qtreewidgetitem.childCount()>=1:
            return True
        else:
            return False

    @staticmethod
    def current_item_path_value_dict(qtreewidgetitem):
        path = []
        #.currentItem() for QTreeWidget
        si = qtreewidgetitem
        while si.parent():
            parent_child_count = si.parent().childCount()
            if parent_child_count>1:
                tmp = []
                uniqueness = True

                # verify if their names are different
                for i in range(parent_child_count):
                    child_name = si.parent().child(i).text(0)

                    if child_name in tmp:
                        uniqueness = False

                    tmp.append(child_name)

                if not uniqueness:
                    path.append(si.parent().indexOfChild(si))

                else:
                    path.append(si.text(0))
            else:
                path.append(si.text(0))
            si = si.parent()

        path.append(si.text(0))
        path.reverse()

        return {'path':path[:-1:], 'value':path[-1]}

    @staticmethod
    def fill_item(item: QTreeWidgetItem, value):
        if value is None:
            return
        elif isinstance(value, dict):
            for key, val in sorted(value.items()):
                ViewTree.new_item(item, str(key), val)
        elif isinstance(value, (list, tuple)):
            for val in value:
                if isinstance(val, (str, int, float)):
                    ViewTree.new_item(item, str(val))
                else:
                    ViewTree.new_item(item, f"[{type(val).__name__}]", val)
        else:
            ViewTree.new_item(item, str(value))

    @staticmethod
    def new_item(parent: QTreeWidgetItem, text:str, val=None):
        child = QTreeWidgetItem([text])
        ViewTree.fill_item(child, val)
        parent.addChild(child)
        child.setExpanded(True)


class Configuration1:
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        # self.kwargs = kwargs
        # for key, value in kwargs.items():
        #     self.__setattr__(key, value)
        #
        # self.args = args

    def init_configuration_1(self):
        # Dictionnary for creating subwindows
        self.subwindows_init = {
            'media_viewer':
                {
                    'widget':QTabWidget(),
                    'layout':None
                },
            'minimal_xml_setup':
                {
                    'widget': ViewTree(value={}),
                    'layout': QFormLayout()
                },
            'minimal_simulation_information':
                {
                    'widget': QWidget(),
                    'layout': QFormLayout()
                },
            'csv_file_table':
                {
                    'widget': QTableWidget(),
                    'layout': None
                },
        }
        self.subwindows_init['media_viewer']['widget'].setTabsClosable(True)
        self.subwindows_init['media_viewer']['widget'].tabCloseRequested.connect(self.delete_Tab)
        self.media_viewer_tab_dict = {'svg_viewer':svg(option=False)}

        self.subwindows_init['media_viewer']['widget'].addTab(self.media_viewer_tab_dict['svg_viewer'], 'svg_viewer')
        # customization to ViewTree
        self.subwindows_init['minimal_xml_setup']['widget'].changeEvent = self.update_XML_CHANGES

        # Initiate parameters to be editable in a future subwindow
        self.param = {
            'program_path': None,
            'project_name': None,
            'executable_name': None,
            'data_source_folder': None,
            'data_destination_folder': None,
            'suffix': None,
            'xml_template_file':None,
            'csv_files': [],
            'configuration_files_destination_folder':None,
            'counter_end': 0
        }

        # If xml_template_file is specify then for every modification to be made
        # this list of dict {path, value} will track
        self._XML_CHANGES = []

        # The widget needed to modify parameters
        self.simulation_config_widget = {
            "program_path": sc(),
            "project_name": QLineEdit(),
            'counter_end': QLineEdit(),
            "executable_name": QLineEdit(),
            "data_source_folder": sc(),
            "data_destination_folder": sc(),
            "suffix": QLineEdit(),
            # function
            "configuration_files_destination_folder": sc(),
            "xml_template_file": QPushButton('click to choose'),
            "csv_files": QPushButton('click to choose'),
        }

        self.option_command = {
            "special_csv_scan": QPushButton('click to choose'),
            "run_simulation": QPushButton('click to choose'),
            "convert_scan_to_csv":QPushButton('click to run')
        }

        self.populate_minimal_simulation_information()

    def populate_minimal_simulation_information(self):
        for key, value in {**self.simulation_config_widget, **self.option_command}.items():

            if key in ['xml_template_file', 'csv_files', 'special_csv_scan','run_simulation','convert_scan_to_csv']:
                def updater():
                    pass

                if key == 'csv_files':
                    def updater():
                        file_ = Data.loadFiles()
                        if file_:
                            self.param['csv_files'] = file_
                            self.update_csv_file_table()

                if key == 'special_csv_scan':
                    def updater():
                        source_ = QFileDialog.getExistingDirectory(None, "Find Directory",".")
                        if source_:
                            self.param['csv_files'] = Data.scan_csv_file(source=source_)
                            self.update_csv_file_table()

                if key == 'xml_template_file':
                    def updater():
                        filter = "XML (*.xml)"
                        file_name = QFileDialog()
                        file_name.setFileMode(QFileDialog.ExistingFiles)
                        xml_file_, filter = file_name.getOpenFileName(None, "Find xml_template_file",".", filter)

                        if xml_file_:
                            self.param['xml_template_file'] = xml_file_
                            short = QDir.toNativeSeparators(xml_file_).split(os.sep)[-1]
                            self.simulation_config_widget['xml_template_file'].setText(short)
                            self.init_minimal_xml_setup()

                fun = updater

                if key == 'run_simulation':
                    fun = self.simulation

                if key == 'convert_scan_to_csv':
                    temp_dict = Simulation.type_dict()
                    fun = lambda:Data.data_conversion_segmentation_celltypes(
                        r"C:\Users\VmWin\Documents\University\Ete2022\Stage\data\Segmentation", r"C:\Users\VmWin\Pictures\test", type_dict=temp_dict)

                value.clicked.connect(fun)

            self.subwindows_init['minimal_simulation_information']['layout'].addRow(key, value)
    def delete_Tab(self, index):
        widget = self.subwindows_init['media_viewer']['widget'].widget(index)
        if not widget == self.media_viewer_tab_dict['svg_viewer']:
            # Delete correspondence
            title = self.subwindows_init['media_viewer']['widget'].tabText(index)
            del self.media_viewer_tab_dict[title]
            # Remove tab
            self.subwindows_init['media_viewer']['widget'].removeTab(index)
    def update_csv_file_table(self):
        temp_dict2 = Simulation.reverse_type_dict()

        # csv file table
        # short name
        short = self.subwindows_init['csv_file_table']['widget']

        columns = ['file_name', 'total_cell'] + list(temp_dict2.values())
        if short.horizontalHeader().count() == 0:
            # Desactivate edit mode
            short.setEditTriggers(QAbstractItemView.NoEditTriggers)

            # set number of columns before the table is populated
            short.setColumnCount(len(columns))
            short.setHorizontalHeaderLabels(columns)

            # visual preference
            short.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            short.horizontalHeader().setSectionResizeMode(len(columns), QHeaderView.Stretch)

            # Cell initial state preview
            # script_path = os.path.abspath(os.path.join(self.parent.parent.program_directory,'addons','ControlPanel','script','plot_initial_state.py'))
            # script_path = f'"{script_path}"'

            short.doubleClicked.connect(self.double_click_csv_table)
                # lambda event:Plotting.ready_to_plot_function(script_path, f'"{os.path.abspath(self.param["csv_files"][event.row()])}"')()
            # )




            # self.tableWidget.doubleClicked.connect(lambda event: Simulation.plot_for_physicell(,self.param['csv_files'][event.row()]))#print(event.row()+1, self.param['csv_files'][event.row()]))

        # Delete previous rows
        short.clearContents()
        for i in range(short.rowCount()):
            short.removeRow(i)

        # Insert row
        for _ in self.param['csv_files']:
            short.insertRow(short.rowCount())

        k=0
        for csv_file in self.param['csv_files']:

            try:
                # import data from csv with columns (x,y,z,type_number)
                df = pd.read_csv(csv_file)

                # Cell frequency count
                freq = df.iloc[:, 3].value_counts().to_dict()

                in_order_row_element = []

                # Retrieve the patient code
                file_name = os.path.abspath(csv_file).split(os.sep)[-1].replace('.csv', '')

                # TODO : fix this ugly none flexible code
                for j in range(1,len(temp_dict2)+1):
                    if float(f"{j}.0") in freq:
                        in_order_row_element.append(freq[float(f"{j}.0")])
                    else:
                        in_order_row_element.append(0)

                total_cell = len(pd.read_csv(csv_file))
                in_order_row_element = [file_name, total_cell] + in_order_row_element

                for i in range(len(in_order_row_element)):
                    short.setItem(*(k, i), QTableWidgetItem(f"{in_order_row_element[i]}"))

            except:
                # When the csv has a problem (eg. empty)
                short.removeRow(k)
                self.param['csv_files'].remove(csv_file)
                k-=1
            k+=1

    def init_minimal_xml_setup(self):
        short = self.subwindows_init['minimal_xml_setup']['widget']
        short.clear()
        value = Config.xml2dict(self.param['xml_template_file'])
        short.fill_item(short.invisibleRootItem(), value)

    def double_click_csv_table(self, event):
        csv_file = self.param["csv_files"][event.row()]
        csv_file_name = os.path.abspath(csv_file).split(os.sep)[-1].replace('.csv','')


        if not csv_file_name in self.media_viewer_tab_dict.keys():
            # get plot
            self.media_viewer_tab_dict[csv_file_name] = widget = pg.PlotWidget()
            widget.setBackground('w')
            self.subwindows_init['media_viewer']['widget'].addTab(widget, csv_file_name)

        self.subwindows_init['media_viewer']['widget'].setCurrentWidget(self.media_viewer_tab_dict[csv_file_name])


    def simulation(self):
        self.param = Simulation.test_param_dictionnary()

        # show param value on screen
        for k, v in self.param.items():
            if not type(self.simulation_config_widget[k]) == type(QPushButton()):
                self.simulation_config_widget[k].setText(str(self.param[k]))

        if len(self.param['csv_files']) >= 1:
            for csv_file in self.param['csv_files']:

                # copy csv to the right destination
                patient_name = csv_file.split(os.sep)[-1].replace('.csv', '')

                csv_copy_path = os.path.join(self.param['configuration_files_destination_folder'], patient_name + '.csv')
                if not QFile.copy(csv_file, csv_copy_path):
                    print("overwriting current csv")
                    QFile.remove(csv_copy_path)
                    QFile.copy(csv_file, csv_copy_path)

                # copy xml config file to the right destination and renaming
                config_file_template_file = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov_tmz_immune_stroma_patchy\config\template.xml"
                config_file_path_file = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov_tmz_immune_stroma_patchy\config\PhysiCell_settings.xml"

                if not QFile.copy(config_file_template_file, config_file_path_file):
                    print("overwriting current config file")
                    QFile.remove(config_file_path_file)
                    QFile.copy(config_file_template_file, config_file_path_file)

                # export_config_file = lambda: QFile.copy(csv_file, csv_copy_path)
                # automatic modification to the config file

                test = Simulation(parent=self, **self.param)
                if test.verification():
                    test.start_simulation()

                else:
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Alert!")
                    dlg.setText("One or more parameter are empty")
                    dlg.exec_()
                return


        # no csv file needed for the simulation
        else:
            test = Simulation(parent=self, **self.param)

            if test.verification():
                test.start_simulation()
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Alert!")
                dlg.setText("One or more parameter are empty")
                dlg.exec_()
            return

    def update_XML_CHANGES(self, *args):
        last_change_path = self.subwindows_init['minimal_xml_setup']['widget'].latest_modify_element_path_value_dict
        if last_change_path:
            if self._XML_CHANGES:
                if last_change_path == self._XML_CHANGES[-1]:
                    pass

                else:
                    print('change have been made')
                    # print(last_change_path)
                    self._XML_CHANGES.append(last_change_path)
            else:
                self._XML_CHANGES.append(last_change_path)
                print('change have been made')
