import math
import os
import shutil
import sys
import time
import traceback

import numpy as np
import pandas as pd
import pyqtgraph as pg
import scipy.io
import xmltodict
from PySide6.QtCore import QFile, QTimer, QDir, QDateTime, Qt, QObject, QRunnable, Signal, Slot, \
    QThreadPool
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QFileDialog, QInputDialog, QTreeWidget, QTreeWidgetItem, QTableWidget, \
    QWidget, QFormLayout, QLineEdit, QPushButton, QAbstractItemView, QTableWidgetItem, QHeaderView, QMessageBox, \
    QTabWidget, QProgressBar, QLabel

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

## Multithreading
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done





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
        #
        self.is_finish = False
        if 'progress_widget' in kwargs:
            self.progress_widget = kwargs['progress_widget']

            self.progress_bar = self.progress_widget['progress_bar']
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(kwargs['counter_end'])

        self.time_data = {'sec': None, 'min': None, 'hour': None, 'day':None}


        # every param
        self.kwargs = kwargs

        # *args should be ending function in order
        self.args = args

        self.basic_task = []

        if 'data_destination_folder' in kwargs and 'data_source_folder' in kwargs:
            self.basic_task.append(lambda: Simulation.specific_export_output(**self.kwargs))
            self.basic_task.append(lambda: Simulation.make_gif(**self.kwargs))

        # if 'program_path' in kwargs:
        #     self.basic_task.append(lambda:Simulation.cleanup(kwargs["program_path"]))

    def start_simulation(self):

        param = self.kwargs
        # loop variable
        self.now_counter = 0
        end_counter = param['counter_end']

        start_time = time.time()


        # Cleanup
        Simulation.cleanup(**param)
        # Run
        Simulation.run_simulation(**param)

        self.progress_bar.setValue(self.now_counter)

        while not QFile.exists(os.path.join(param['data_source_folder'], "final.svg")):
            # wait one second
            time.sleep(1)
            self.time_data = Configuration1.estimated_time(start_time, time.time(), self.now_counter, end_counter)
            # self.update(start_time, time.time(), now_counter, end_counter)



            # check for the lastest every sec svg file and took is number
            filename = 'snapshot' + "%08i" % self.now_counter + '.svg'

            if QFile.exists(os.path.join(param['data_source_folder'], filename)):
                self.now_counter += 1
                self.progress_bar.setValue(self.now_counter)

                # update estimated time
                start_time = time.time()


        self.is_finish = True
        print('finish')

        # Other function from args
        # for task in self.basic_task+list(self.args):
        #     task()


    ## Function
    @staticmethod
    def cleanup(*args, **kwargs):
        print('cleanup')
        program_path = kwargs['program_path']
        # os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
        # os.system(f'start cmd /k make -C {program_path} reset & make -C {program_path} reset & make -C {program_path} data-cleanup & make -C {program_path} clean"')
        os.system(f'make -C {program_path} reset')
        os.system(f'make -C {program_path} reset')
        os.system(f'make -C {program_path} data-cleanup')
        os.system(f'make -C {program_path} clean')

        return True
    @staticmethod
    def run_simulation(*args,**kwargs):
        print('run_simulation')
        program_path = kwargs['program_path']
        project_name = kwargs['project_name']
        executable_name = kwargs['executable_name']

        executable_path = os.path.abspath(os.path.join(program_path,executable_name))
        os.system(f'start cmd /k  "make -C {program_path} {project_name} & make -C {program_path} & cd {program_path} & {executable_path}"')  # to keep cmd open --> cmd /k and /c for closing after task
        return True
    @staticmethod
    def make_gif(*args, **kwargs):
        print('make_gif')
        data_source_folder = kwargs['data_source_folder']
        data_destination_folder = kwargs['data_destination_folder']
        os.system(f'start cmd /k "magick convert {data_source_folder}/s*.svg {data_destination_folder}/out.gif"')
        return f"{data_destination_folder}/out.gif"
    @staticmethod
    def specific_export_output(data_source_folder=None, data_destination_folder=None, *args, **kwargs):
        print('specific_export_output')
        print('truc',data_source_folder, data_destination_folder)
        if not data_source_folder:
            data_source_folder = QFileDialog.getExistingDirectory(None, "Select Directory Source")
        if not data_destination_folder:
            data_destination_folder = QFileDialog.getExistingDirectory(None, "Select Directory Destination")

        if data_source_folder and data_destination_folder:
            insta = QFCP()
            insta.copy_files(scr=data_source_folder, dest=data_destination_folder)

        return data_destination_folder

    def verification(self, *args, **kwargs):
        print('verification')
        ok_bool_list = [True]
        param = self.kwargs
        for k, v in param.items():
            if not v:
                if k in ['suffix', 'csv_file']:
                    ok_bool_list.append(True)
                else:
                    ok_bool_list.append(False)
        return not (False in ok_bool_list)

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
        return
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
        with open(os.path.join(destination,f"{xml_file_name}.xml"), 'w') as f:
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
        self.modify_element_path_value_list_dict = []
        self.doubleClicked.connect(self.edit_and_store_path_value_dict)

    def edit_and_store_path_value_dict(self):
        ok = bool()
        if not ViewTree.is_sub_tree(self.selectedItems()[0]):
            text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')

            if ok and text:
                path_value_dict = ViewTree.modify_element(self.selectedItems()[0], text)

                if path_value_dict:
                    if self.modify_element_path_value_list_dict:
                        if path_value_dict == self.modify_element_path_value_list_dict[-1]:
                            return

                        else:
                            self.modify_element_path_value_list_dict.append(path_value_dict)
                            return
                    else:
                        self.modify_element_path_value_list_dict.append(path_value_dict)
                        return


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

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args

    def init_configuration_1(self):
        print('init_configuration_1')

        # Dictionnary for creating subwindows
        self.subwindows_init = Configuration1.subwindows_dictionary()

        # Creating a dictionary to contain every widget appearing on the media_viewer
        self.media_viewer_tab_dict = Configuration1.media_viewer_dictionary()

        # Customize media_viewer
        self.subwindows_init['media_viewer']['widget'].setTabsClosable(True)
        self.subwindows_init['media_viewer']['widget'].tabCloseRequested.connect(self.delete_Tab)
        self.subwindows_init['media_viewer']['widget'].addTab(self.media_viewer_tab_dict['svg_viewer'], 'svg_viewer')


        # Initiate parameters to be editable in a future sub-windows
        self.param = Configuration1.test_param_dictionnary()
        self.csv_files = [self.param['csv_file'], r"C:\Users\VmWin\Pictures\test\Segmentation\Project 3 SOC glioma IMC (McGill)\20200702\OneDrive_5_7-14-2020\Pano 01_Col5-13_1_ROI 10_NP14-1026-2A_10\10_NP14-1026-2A_10.csv"] # testing

        # # If xml_template_file is specify then for every modification to be made
        # # this list of dict {path, value} will track
        self._XML_CHANGES = self.subwindows_init['minimal_xml_setup']['widget'].modify_element_path_value_list_dict

        # The widget needed to modify parameters
        self.simulation_config_widget = Configuration1.simulation_config_widget_dictionary()

        # Addional command widget for minimal_simulation_information subwindow
        self.option_command = Configuration1.option_command_dictionary()

        # Script to put every thing in place
        self.populate_minimal_simulation_information()

    ## Gui manipulation related
    def populate_minimal_simulation_information(self):
        print('populate_minimal_simulation_information')
        for key, value in {**self.simulation_config_widget, **self.option_command}.items():

            if key in ['xml_template_file', 'csv_file', 'special_csv_scan','run_simulation','convert_scan_to_csv','print_XML_CHANGES','test_copy']:
                def updater():
                    pass

                if key == 'csv_file':
                    def updater():
                        file_ = Data.loadFiles()
                        if file_:
                            self.csv_files = file_
                            self.update_csv_file_table()

                if key == 'special_csv_scan':
                    def updater():
                        source_ = QFileDialog.getExistingDirectory(None, "Find Directory",".")
                        if source_:
                            self.csv_files = Data.scan_csv_file(source=source_)
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
                    def updater():
                        self.option_command['run_simulation'].setEnabled(False)
                        self.fun_fun()

                    fun = updater

                if key == 'print_XML_CHANGES':

                    fun = lambda: print("self._XML_CHANGES", self._XML_CHANGES)

                if key == 'convert_scan_to_csv':
                    temp_dict = Configuration1.type_dict()
                    fun = lambda:Data.data_conversion_segmentation_celltypes(
                        r"C:\Users\VmWin\Documents\University\Ete2022\Stage\data\Segmentation", r"C:\Users\VmWin\Pictures\test", type_dict=temp_dict)
                if key == 'test_copy':
                    fun = lambda: Simulation.specific_export_output(**self.param)

                value.clicked.connect(fun)

            self.subwindows_init['minimal_simulation_information']['layout'].addRow(key, value)
    def delete_Tab(self, index):
        print('delete_Tab')
        widget = self.subwindows_init['media_viewer']['widget'].widget(index)
        if not widget == self.media_viewer_tab_dict['svg_viewer']:
            # Delete correspondence
            title = self.subwindows_init['media_viewer']['widget'].tabText(index)
            del self.media_viewer_tab_dict[title]
            # Remove tab
            self.subwindows_init['media_viewer']['widget'].removeTab(index)
    def update_csv_file_table(self):
        print('update_csv_file_table')
        temp_dict2 = Configuration1.reverse_type_dict()

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
        for _ in self.csv_files:
            short.insertRow(short.rowCount())

        k=0
        for csv_file in self.csv_files:

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
                self.csv_files.remove(csv_file)
                k-=1
            k+=1
    def init_minimal_xml_setup(self):
        print('init_minimal_xml_setup')
        short = self.subwindows_init['minimal_xml_setup']['widget']
        short.clear()
        value = Config.xml2dict(self.param['xml_template_file'])
        short.fill_item(short.invisibleRootItem(), value)
    def double_click_csv_table(self, event):
        print('double_click_csv_table')
        csv_file = self.csv_files[event.row()]
        csv_file_name = os.path.abspath(csv_file).split(os.sep)[-1].replace('.csv','')
        if not csv_file_name in self.media_viewer_tab_dict.keys():
            # get plot
            self.media_viewer_tab_dict[csv_file_name] = widget = pg.PlotWidget()
            widget.setBackground('w')
            self.subwindows_init['media_viewer']['widget'].addTab(widget, csv_file_name)

        self.subwindows_init['media_viewer']['widget'].setCurrentWidget(self.media_viewer_tab_dict[csv_file_name])
    @staticmethod
    def setColortoRow(table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)


    ## Set up simulation functions
    def show_param_on_widget(self):
        print('show_param_on_widget')
        # show param value on screen
        for k, v in self.param.items():
            if not type(self.simulation_config_widget[k]) == type(QPushButton()):
                print(k, "-" * (90 - len(k)), v)
                self.simulation_config_widget[k].setText(str(self.param[k]))
    def setup_simulation(self, *arg, **kwargs):
        print('setup_simulation')

        self.param = kwargs
        self.show_param_on_widget()


        # Automatic suffix for uniqueness
        self.param['suffix'] = Configuration1.now_time_in_str()
        self.param['data_destination_folder'] = self.export_folder_naming_rule()

        # copy csv to the right destination
        csv_file_name = self.param['csv_file'].split(os.sep)[-1]
        csv_copy_path = os.path.join(self.param['configuration_files_destination_folder'], csv_file_name)

        if not QFile.copy(self.param['csv_file'], csv_copy_path):
            print("overwriting current csv")
            QFile.remove(csv_copy_path)
            QFile.copy(self.param['csv_file'], csv_copy_path)

        # Maybe a condition to disable it
        # Automatic change to xml
        if self.automatic_change_to_config():

            # create xml config file from the template and from the changes
            self.create_xml_from_template_change(**self.param)

        # Return configured simulation object
        return Simulation(**{**self.param,**{'progress_widget':self.subwindows_init['progress_view']['widget'].element['local_']}})

    @staticmethod
    def now_time_in_str():
        return str(QDateTime.currentDateTime().toString(Qt.ISODate)).replace(':', '_')
    def export_folder_naming_rule(self):
        print('export_folder_naming_rule')
        return os.path.join(r"C:\Users\VmWin\Pictures\test", self.param['project_name'] + '_' + self.param['suffix'])
    def create_xml_from_template_change(self, *args, **kwargs):
        print('create_xml_from_template_change')
        param = kwargs
        xml_dict = Config.xml2dict(param['xml_template_file'])

        for change in self._XML_CHANGES:
            path_list = change['path']
            new_value = change['value']
            Config.edit2dict(*path_list, dictionary=xml_dict, new_value=new_value)

        destination = param['configuration_files_destination_folder']
        xml_file_name = "PhysiCell_settings"
        data = xml_dict
        Config.dict2xml(data, destination, xml_file_name)
        return True
    def automatic_change_to_config(self, *args, **kwargs):
        print('automatic_change_to_config')
        xml_file = self.param['xml_template_file']
        csv_file = self.param['csv_file']

        if xml_file:
            xml_dict = Config.xml2dict(xml_file)

        if csv_file and xml_file:

            # read csv
            df = pd.read_csv(csv_file)
            df.columns = ['x', 'y', 'z', 'type']
            cell_type_concern = list(map(float, range(1, 5)))
            sub = df.loc[df['type'].isin(cell_type_concern)]

            # Number of cells
            total_cell = len(sub)

            # Tumour zone
            x_max = sub['x'].max()
            x_min = sub['x'].min()

            y_max = sub['y'].max()
            y_min = sub['y'].min()

            # Tumour radius
            tumour_radius = round(max(x_max,abs(x_min), y_max, abs(y_min)))+1

            # cell_density
            cell_density = total_cell/(tumour_radius**2)

            #  A_frag
            a_frag = tumour_radius**2 * math.pi

            # Change tumour radius
            self._XML_CHANGES.append({'path':['PhysiCell_settings','user_parameters','R','#text'], 'value':f'{tumour_radius}'})
            # Change domain
            for item, value in zip(['x_max','x_min', 'y_max', 'y_min'],[2*tumour_radius,-2*tumour_radius,2*tumour_radius,-2*tumour_radius]):
                self._XML_CHANGES.append({'path':['PhysiCell_settings','domain', item], 'value':f'{value}'})
                # print(f'{item}\t\t\t:',item)
            # Change cell density
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'xhi', '#text'], 'value': f'{cell_density}'})
            # Change tumour surface A_frag
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'A_frag', '#text'], 'value': f'{a_frag}'})
            # Change path to csv
            self._XML_CHANGES.append({'path': ['PhysiCell_settings','initial_conditions','cell_positions','filename'], 'value':os.path.abspath(csv_file).split(os.sep)[-1]})

            # Verify that the option is enable
            if not Config.get2dict(*['PhysiCell_settings','initial_conditions','cell_positions','@enabled'], dictionary=xml_dict):
                self._XML_CHANGES.append({'path': ['PhysiCell_settings','initial_conditions','cell_positions','@enabled'], 'value':'"true"'})
            return True

        return False


    ## Threading related functions
    def fun_fun(self):
        print("fun_fun")

        # Threadpool for simulation in background
        self.threadpool = QThreadPool()
        self.simulation_on_the_way = Simulation()

        # Timer for progress bar update
        self.timer = QTimer()
        self.timer.setInterval(1500)
        self.timer.timeout.connect(self.recurring_function)
        self.timer.start()


        # Pass the function to execute
        worker = Worker(self.execute_function)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.result_function)
        worker.signals.finished.connect(self.finish_function)
        worker.signals.progress.connect(self.update_progress_view)

        # Execute
        self.threadpool.start(worker)
        return True
    def execute_function(self, progress_callback):
        print('execute_function')

        # loop variable
        self.now_counter = 0
        self.start_time = time.time()

        end_counter = len(self.csv_files)

        # setup progress bar
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setMinimum(0)
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setMaximum(end_counter)
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setValue(0)


        # with csv
        if end_counter >= 1:

            ## to show csv_file on a subwindow
            # self.update_csv_file_table()
            self.color_row_in_yellow(0)

            for csv_file in self.csv_files:

                # update parameters
                self.param['csv_file'] = csv_file

                # set up
                self.simulation_on_the_way = self.setup_simulation(**self.param)

                if self.simulation_on_the_way.verification():
                    # start
                    self.start_time = time.time()
                    self.simulation_on_the_way.start_simulation()

                    self.now_counter += 1

                    # emit progress
                    progress_callback.emit(self.now_counter)
                    time.sleep(5)

                else:

                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Alert!")
                    dlg.setText("One or more parameter are empty")
                    dlg.exec_()

        # without csv
        else:
            pass
    def result_function(self):
        print('result_function')
        return
    def finish_function(self):
        print('finish_function')

        self.timer.stop()
        self.recurring_function()
        return
    def update_progress_view(self, n):
        print('update_progress_view')

        # Update main progress bar
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setValue(n)

        # set the previous row in green
        self.color_row_in_green(self.now_counter-1)

        if self.now_counter+1<=len(self.csv_files):
            # set the next row in yellow
            self.color_row_in_yellow(self.now_counter)

        ## ending simulation task

        ## Basic task

        # export data
        print("*"*140)
        self.endind_simulation_data_export()

        # Cleanup

        # Additionnal task


        return




    ## Ending simulation task related
    def endind_simulation_data_export(self):
        print('endind_simulation_data_export')

        ## copy data
        name = os.path.abspath(self.param['csv_file']).split(os.sep)[-1].replace('.csv', '')
        data_source_folder = self.param['data_source_folder']
        data_destination_folder = self.param['data_destination_folder']

        txt = f"data exported from {data_source_folder}\n to {data_destination_folder}"
        tmp = QFCP()
        element = {'progress_bar': None, 'label': QLabel(txt)}

        self.subwindows_init['progress_view']['widget'].add_element(element=element, name=name)
        tmp.copy_files(scr=data_source_folder, dest=data_destination_folder)

        return True

    def color_row_in_green(self, rowIndex):
        print('color_row_in_green')
        table = self.subwindows_init['csv_file_table']['widget']
        Configuration1.setColortoRow(table,rowIndex,QBrush(QColor.fromRgb(52,222,52)))

    def color_row_in_yellow(self, rowIndex):
        print('color_row_in_yellow')
        table = self.subwindows_init['csv_file_table']['widget']
        Configuration1.setColortoRow(table,rowIndex,QBrush(QColor.fromRgb(249,250,180)))


    # Progress bar related
    def local_progress_bar_update(self):
        # print('local_progress_bar_update')
        time_data = self.simulation_on_the_way.time_data
        day_, hour_, min_, sec_ = time_data['day'], time_data['hour'], time_data['min'], time_data['sec']

        if day_ >= 0 and hour_ >= 0 and min_ >= 0 and sec_ >= 0:
            self.subwindows_init['progress_view']['widget'].element['local_']['label'].setText(
                f"Estimated time before finishing {day_} day {hour_} hour {min_} min {round(sec_)} sec")
    def global_progress_bar_update(self):
        # print('global_progress_bar_update')
        arguments = [
            self.start_time,
            time.time(),
            self.now_counter,
            (self.param['counter_end'] - self.simulation_on_the_way.now_counter) * (
                        len(self.csv_files) - self.now_counter)
        ]
        time_data = Configuration1.estimated_time(*arguments)
        day_, hour_, min_, sec_ = time_data['day'], time_data['hour'], time_data['min'], time_data['sec']

        if day_ >= 0 and hour_ >= 0 and min_ >= 0 and sec_ >= 0:
            self.subwindows_init['progress_view']['widget'].element['global_']['label'].setText(
                f"Estimated time before finishing {day_} day {hour_} hour {min_} min {round(sec_)} sec")
    def recurring_function(self):
        # print('recurring_function')
        ## update time
        try:
            # Overall progress bar update
            self.global_progress_bar_update()

            # Current simulation progress bar update
            self.local_progress_bar_update()

        except:
            pass
    @staticmethod
    def estimated_time(start_time, end_time, now_value, end_value):
        # print('estimated_time')
        delta_time = abs(end_time - start_time)
        delta_step = abs(end_value - now_value)

        total_time = delta_time * delta_step
        day_ = total_time//(60*60*24)
        hour_ = round(total_time - 60*60*60*day_)//(60*60)
        min_ = round(total_time - 60*60*hour_) // 60
        sec_ = round(total_time - 60 * min_)

        return {'sec': sec_, 'min': min_, 'hour': hour_, 'day':day_}


    ## Config
    @staticmethod
    def subwindows_dictionary():
        print('subwindows_dictionary')
        dictionary = {
            'media_viewer':
                {
                    'widget': QTabWidget(),
                    'layout': None
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
            'progress_view':
                {
                    'widget': MultipleProgressBar('local_', 'global_'),
                    'layout': None
                },
        }
        # Specify layout
        dictionary['progress_view']['layout'] = dictionary['progress_view']['widget'].layout
        return dictionary
    @staticmethod
    def simulation_config_widget_dictionary():
        print('simulation_config_widget_dictionary')
        dictionary = {
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
            "csv_file": QPushButton('click to choose'),
        }
        return dictionary
    @staticmethod
    def option_command_dictionary():
        print('option_command_dictionary')
        dictionary = {
            "special_csv_scan": QPushButton('click to choose'),
            "run_simulation": QPushButton('click to choose'),
            "convert_scan_to_csv": QPushButton('click to run'),
            "print_XML_CHANGES": QPushButton('click to run'),
            'test_copy': QPushButton('click to run'),
        }
        return dictionary
    @staticmethod
    def media_viewer_dictionary():
        dictionary = {'svg_viewer':svg(option=False)}
        return dictionary


    # Parameters for test
    @staticmethod
    def test_param_dictionnary():
        print('test_param_dictionary')
        param = {
            'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
            'project_name': "gbm-ov-tmz-immune-stroma-patchy-sample",
            'executable_name': "gbm_ov_tmz_immune_stroma_patchy.exe",
            'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
            'data_destination_folder': r"C:\Users\VmWin\Pictures\test\gbm_ov_tmz_immune_stroma_patchy_sample_2022-08-03T09_42_54",
            'suffix': "2022-08-03T09_42_54",
            'xml_template_file': r"C:\Users\VmWin\Pictures\test\template.xml",
            'csv_file': r"C:\Users\VmWin\Pictures\test\Segmentation\Project 1 ICI glioma IMC\20200617\OneDrive_10_7-7-2020-1\Pano 01_Col2-3_1_ROI 05_X17-343-B2_5\05_X17-343-B2_5.csv",#                         r"C:\Users\VmWin\Pictures\test\Segmentation\Project 3 SOC glioma IMC (McGill)\20200702\OneDrive_5_7-14-2020\Pano 01_Col5-13_1_ROI 10_NP14-1026-2A_10\10_NP14-1026-2A_10.csv"],
            'configuration_files_destination_folder':r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov_tmz_immune_stroma_patchy\config",
            'counter_end': 144
        }
        return param
    @staticmethod
    def empty_param_dictionnary():
        print('empty_param_dictionnary')
        param = {
            'program_path': None,
            'project_name': None,
            'executable_name': None,
            'data_source_folder': None,
            'data_destination_folder': None,
            'suffix': None,
            'xml_template_file':None,
            'csv_file': None,
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


class MultipleProgressBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.layout = QFormLayout()
        # self.layout.setSpacing(0)

        # self.layout.setContentsMargins(0, 0, 0, 0)
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


# # Simple progress bar
# class SimulationProgress(QProgressDialog):
#
#     def __init__(self, parent=None, counter_end=144, data_source_folder=None, *args, **kwargs):
#         super().__init__(parent)
#
#         self.start_time = 0
#
#         self.end_time = 0
#         self.time_delta = []
#
#         self.counter = 0
#         self.counter_end = counter_end
#
#         self.data_source_folder = data_source_folder
#
#         # Ordered ending task list
#         if not "end_task_list" in kwargs.keys():
#             self.end_task_list = [lambda: None]
#         else:
#             self.end_task_list = kwargs['end_task_list']
#
#         # Ordered recuring task list
#         if not "recuring_task_list" in kwargs.keys():
#             self.recuring_task_list = [lambda: None]
#         else:
#             self.recuring_task_list = lambda: kwargs['recuring_task_list']()
#
#         self.setRange(0, self.counter_end)
#         self.setWindowTitle("Simulation progress")
#
#
#         self.timer = QTimer()
#         self.timer.setInterval(500)
#
#         self.timer.timeout.connect(self.recurring_function)
#         self.timer.timeout.connect(self.update_estimating_time)
#         self.timer.start()
#         self.show()
#
#     # TODO : make it usuable outside of this specific situation
#     def recurring_function(self):
#
#         if self.wasCanceled():
#             self.timer.stop()
#             self.close()
#             return
#
#         if not QFile.exists(os.path.join(self.data_source_folder,"final.svg")):
#
#             # check for the lastest every sec svg file and took is number
#             n = self.counter + 1
#             filename = 'snapshot' + "%08i" % n + '.svg'
#
#             if QFile.exists(os.path.join(self.data_source_folder, filename)):
#                 self.counter += 1
#                 self.end_time = time.time()
#                 self.update_estimating_time()
#
#                 self.start_time = time.time()
#
#                 self.setValue(self.counter)
#                 # TODO : plot1
#
#                 QCoreApplication.processEvents()
#             self.update_estimating_time()
#
#
#         else:
#             self.timer.stop()
#             self.close()
#             self.end_function()
#
#     def end_function(self):
#         for task in self.end_task_list:
#             task()
#         return "DONE"
#
#     def update_estimating_time(self):
#
#         delta_time = abs(self.end_time - self.start_time)
#         delta_step = abs(self.counter_end - self.counter)
#         total_time = delta_time * delta_step
#
#         min = round(total_time) // 60
#         sec = round(abs(total_time - 60 * min))
#
#         if min > 0 and sec > 0:
#             self.setLabelText(f"Estimated time before finishing {min} min {round(sec)} sec")