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
global PATH
# basic info
filename = 'extra_function.py'
PATH = os.path.realpath(__file__).strip(filename)


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(PATH,'..','..','..','out','debug_extra_function.log'))
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# file_handler2 = logging.FileHandler(os.path.join(path,'..','..','..','out','debug_extra_function.log'))
# file_handler2.setLevel(logging.DEBUG)
# file_handler2.setFormatter(formatter)


# sys.path.insert(1, PATH)
# from .plot_initial_state import plot_initial_state as pis
# from .plot_time_cell_number import plot_time_cell_number as ptcn
# from .plot_concentration_chemokine import plot_concentration_chemokine as pcc

# import svg viewer from addons
sys.path.insert(1, os.path.join(PATH ,'..','..','SvgViewer'))
from ADDON_SvgViewer import SvgViewer as svg

# import from custom
sys.path.insert(1, os.path.join(PATH, '..', '..', '..', 'scr', 'python', 'custom'))
from FileCopyProgress import * #FileCopyProgress as QFCP
from SearchComboBox import *
from ScrollableFormWidget import *


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
                # logger.debug(*([i]+cell_position), sep='\t\t\t\t')
                yield cell_position

    @staticmethod
    def convert_to_csv(destination, filename, data):
        np.savetxt(os.path.join(destination, f"{filename}.csv"), data, delimiter=",", fmt='%s')

    @staticmethod
    def create_dirtree_without_files(src, dst):
        logger.debug('create_dirtree_without_files')
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
        logger.debug('data_conversion_segmentation_celltypes')
        try:
            dest = os.path.join(destination, source.split(os.sep)[-1])
            Data.create_dirtree_without_files(source, dest)

        except:
            logger.debug("overwriting")
            shutil.rmtree(destination)
            Data.create_dirtree_without_files(source, destination)

        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(source):
            path = root.split(os.sep)

            for file in files:
                if 'nuclei_multiscale.mat' in file:
                    f_path = os.path.join(*([f"C:{os.sep}"] + path[1::] + [file]))
                    # logger.debug(f_path)
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
                    logger.debug(f"{os.path.join(dst, filename)}")

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



class Simulation2:
    def __init__(self, *args, **kwargs):
        self.parent = kwargs['parent']
        del kwargs['parent']

        self.args = args
        self.kwargs = kwargs

        self.finish = False
        self.start_time = time.time()
        self.end_time = time.time()


    def setup_thread(self):
        logger.debug("setup_thread")

        # Threadpool for simulation in background
        self.threadpool = QThreadPool()


        # start simulation in cmd tab

        # Pass the function to execute
        worker = Worker(self.worker_function)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.result_function)
        worker.signals.finished.connect(self.finish_function)
        worker.signals.progress.connect(self.update_progress)

        # verification
        if Simulation2.verification(**self.kwargs):

            # Execute
            self.threadpool.start(worker)
        else:
            print("Not Executed")

    def update_progress(self, n):
        logger.debug('update_progress')

        # update progress bar
        self.parent.current_simulation_progress = n
        self.parent.current_simulation_step_delta_time = time.time()-self.start_time
        self.start_time = time.time()

    def result_function(self):
        logger.debug('result_function')

    def finish_function(self):
        logger.debug('finish_function')

        ## ending task
        name = os.path.abspath(self.kwargs['csv_file']).split(os.sep)[-1].replace('.csv', '')
        txt = f"data exported from {self.kwargs['data_source_folder']}\n to {self.kwargs['data_destination_folder']}"
        element = {'progress_bar': None, 'label': QLabel(txt)}
        self.parent.subwindows_init['progress_view']['widget'].add_element(element=element, name=name)

        Simulation2.specific_export_output(**self.kwargs)

        Simulation2.make_gif(data_source_folder=self.kwargs['data_destination_folder'], data_destination_folder=self.kwargs['data_destination_folder'])

        data_source_folder = self.kwargs['data_destination_folder']
        data_destination_folder = self.kwargs['data_destination_folder']

        # plot
        # cell vs time
        script_path = os.path.join(PATH, 'plot_time_cell_number.py')
        script_name = Plotting.get_script_name(script_path)
        figure_name = name+'_'+script_name
        counter_end = self.kwargs['counter_end']

        os.system(f"start cmd /c python {script_path} {data_source_folder} {data_destination_folder} {figure_name} {counter_end}""")

        # Chemokine concentration
        moments = ['output' + "%08i" % (self.kwargs['counter_end']//2) + '.xml','final.xml']
        for moment in moments:
            script_path = os.path.join(PATH, 'plot_concentration_chemokine.py')
            script_name = Plotting.get_script_name(script_path)
            figure_name = name + '_'+moment+'_'+ script_name

            os.system(f"start cmd /c python {script_path} {data_source_folder} {data_destination_folder} {figure_name} {moment}""")

        # for task in self.args:
        #     task()

        # call to do another simulation
        self.finish = True

    def worker_function(self, progress_callback):
        logger.debug('worker_function')
        # Cleanup
        Simulation2.cleanup(**self.kwargs)
        Simulation2.run_simulation(**self.kwargs)
        param = self.kwargs
        now_counter = 0

        # emit progress
        progress_callback.emit(now_counter)
        self.start_time = time.time()
        while not QFile.exists(os.path.join(param['data_source_folder'], "final.svg")):
            # wait one second
            time.sleep(1)

            # check for the lastest every sec svg file and took is number
            filename = 'snapshot' + "%08i" % now_counter + '.svg'

            if QFile.exists(os.path.join(param['data_source_folder'], filename)):
                now_counter += 1
                progress_callback.emit(now_counter)


    ## Function
    @staticmethod
    def cleanup(*args, **kwargs):
        logger.debug('cleanup')
        program_path = kwargs['program_path']
        # os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
        # os.system(f'start cmd /c make -C {program_path} reset & make -C {program_path} reset & make -C {program_path} data-cleanup & make -C {program_path} clean"')
        os.system(f'make -C {program_path} reset')
        time.sleep(1)
        os.system(f'make -C {program_path} reset')
        time.sleep(1)
        os.system(f'make -C {program_path} data-cleanup')
        time.sleep(1)
        os.system(f'make -C {program_path} clean')
        time.sleep(1)

        return True
    @staticmethod
    def run_simulation(*args, **kwargs):
        logger.debug('run_simulation')
        program_path = kwargs['program_path']
        project_name = kwargs['project_name']
        executable_name = kwargs['executable_name']

        executable_path = os.path.abspath(os.path.join(program_path, executable_name))
        # os.system(f'start cmd /c  "make -C {program_path} {project_name} & make -C {program_path} & cd {program_path} & {executable_path}"')  # to keep cmd open --> cmd /c and /c for closing after task
        os.system(
            f'start cmd /c "make -C {program_path} {project_name} & make -C {program_path} & cd {program_path} & {executable_path}"')  # to keep cmd open --> cmd /c and /c for closing after task
        return True
    @staticmethod
    def make_gif(*args, **kwargs):
        logger.debug('make_gif')
        data_source_folder = kwargs['data_source_folder']
        data_destination_folder = kwargs['data_destination_folder']
        os.system(f'start cmd /c "magick convert {data_source_folder}/s*.svg {data_destination_folder}/out.gif"')
        return f"{data_destination_folder}/out.gif"
    @staticmethod
    def specific_export_output(data_source_folder=None, data_destination_folder=None, *args, **kwargs):
            logger.debug('specific_export_output')
            logger.debug(f"data_source_folder{data_source_folder}")
            logger.debug(f"data_destination_folder{data_destination_folder}")
            if not data_source_folder:
                data_source_folder = QFileDialog.getExistingDirectory(None, "Select Directory Source")
            if not data_destination_folder:
                data_destination_folder = QFileDialog.getExistingDirectory(None, "Select Directory Destination")

            if data_source_folder and data_destination_folder:
                insta = FileCopyProgress()
                insta.copy_files(scr=data_source_folder, dest=data_destination_folder)

            return data_destination_folder
    @staticmethod
    def verification(*args, **kwargs):
        logger.debug('verification')
        ok_bool_list = [True]
        param = kwargs
        for k, v in param.items():
            if not v:
                if k in ['suffix', 'csv_file']:
                    ok_bool_list.append(True)
                else:
                    ok_bool_list.append(False)
        return not (False in ok_bool_list)


# Simulation instance to facilitate series of simulation
# class Simulation:
#     def __init__(self, *args, **kwargs):
#         #
#         self.is_finish = False
#         if 'progress_widget' in kwargs:
#             self.progress_widget = kwargs['progress_widget']
#
#             self.progress_bar = self.progress_widget['progress_bar']
#             self.progress_bar.setMinimum(0)
#             self.progress_bar.setMaximum(kwargs['counter_end'])
#
#         self.time_data = {'sec': None, 'min': None, 'hour': None, 'day':None}
#
#
#         # every param
#         self.kwargs = kwargs
#
#         # *args should be ending function in order
#         self.args = args
#
#         self.basic_task = []
#
#         if 'data_destination_folder' in kwargs and 'data_source_folder' in kwargs:
#             self.basic_task.append(lambda: Simulation.specific_export_output(**self.kwargs))
#             self.basic_task.append(lambda: Simulation.make_gif(**self.kwargs))
#
#         # if 'program_path' in kwargs:
#         #     self.basic_task.append(lambda:Simulation.cleanup(kwargs["program_path"]))
#
#     def start_simulation(self):
#
#         param = self.kwargs
#
#         # loop variable
#         self.now_counter = 0
#         end_counter = param['counter_end']
#
#         start_time = time.time()
#
#         # Cleanup
#         Simulation.cleanup(**param)
#         # Run
#         Simulation.run_simulation(**param)
#
#         self.progress_bar.setValue(self.now_counter)
#
#         while not QFile.exists(os.path.join(param['data_source_folder'], "final.svg")):
#             # wait one second
#             time.sleep(1)
#             self.time_data = Configuration1.estimated_time(start_time, time.time(), self.now_counter, end_counter)
#             # self.update(start_time, time.time(), now_counter, end_counter)
#
#
#
#             # check for the lastest every sec svg file and took is number
#             filename = 'snapshot' + "%08i" % self.now_counter + '.svg'
#
#             if QFile.exists(os.path.join(param['data_source_folder'], filename)):
#                 self.now_counter += 1
#
#
#                 self.progress_bar.setValue(self.now_counter)
#
#                 # update estimated time
#                 start_time = time.time()
#
#
#         # Other function from args
#         # for task in self.basic_task+list(self.args):
#         #     task()
#         # # Cleanup
#         # Simulation.cleanup(**param)
#         self.is_finish = True
#         logger.debug('finish')
#
#
#
#
#     def set_up_simulation(self):
#
#         # Automatic suffix for uniqueness
#         self.kwargs['suffix'] = Configuration1.now_time_in_str()
#         self.kwargs['data_destination_folder'] = self.export_folder_naming_rule()
#
#         # copy csv to the right destination
#         csv_file_name = self.kwargs['csv_file'].split(os.sep)[-1]
#         csv_copy_path = os.path.join(self.kwargs['configuration_files_destination_folder'], csv_file_name)
#
#         if not QFile.copy(self.kwargs['csv_file'], csv_copy_path):
#             logger.debug("overwriting current csv")
#             QFile.remove(csv_copy_path)
#             QFile.copy(self.kwargs['csv_file'], csv_copy_path)
#
#         # Maybe a condition to disable it
#         # Automatic change to xml
#         if self.automatic_change_to_config():
#             # create xml config file from the template and from the changes
#             self.create_xml_from_template_change(**self.kwargs)
#
#         # Return configured simulation object
#         for k, v in self.kwargs.items():
#             logger.debug(f"{k}{'.' * (100 - len(k))}{v}")
#
#
#
#     ## Function
#     @staticmethod
#     def cleanup(*args, **kwargs):
#         logger.debug('cleanup')
#         program_path = kwargs['program_path']
#         # os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
#         # os.system(f'start cmd /c make -C {program_path} reset & make -C {program_path} reset & make -C {program_path} data-cleanup & make -C {program_path} clean"')
#         os.system(f'make -C {program_path} reset')
#         time.sleep(1)
#         os.system(f'make -C {program_path} reset')
#         time.sleep(1)
#         os.system(f'make -C {program_path} data-cleanup')
#         time.sleep(1)
#         os.system(f'make -C {program_path} clean')
#         time.sleep(1)
#
#         return True
#     @staticmethod
#     def run_simulation(*args,**kwargs):
#         logger.debug('run_simulation')
#         program_path = kwargs['program_path']
#         project_name = kwargs['project_name']
#         executable_name = kwargs['executable_name']
#
#         executable_path = os.path.abspath(os.path.join(program_path,executable_name))
#         # os.system(f'start cmd /c  "make -C {program_path} {project_name} & make -C {program_path} & cd {program_path} & {executable_path}"')  # to keep cmd open --> cmd /c and /c for closing after task
#         os.system(f'start cmd /c "make -C {program_path} {project_name} & make -C {program_path} & cd {program_path} & {executable_path}"')  # to keep cmd open --> cmd /c and /c for closing after task
#         return True
#     @staticmethod
#     def make_gif(*args, **kwargs):
#         logger.debug('make_gif')
#         data_source_folder = kwargs['data_source_folder']
#         data_destination_folder = kwargs['data_destination_folder']
#         os.system(f'start cmd /c "magick convert {data_source_folder}/s*.svg {data_destination_folder}/out.gif"')
#         return f"{data_destination_folder}/out.gif"
#     @staticmethod
#     def specific_export_output(data_source_folder=None, data_destination_folder=None, *args, **kwargs):
#         logger.debug('specific_export_output')
#         logger.debug(f"data_source_folder{data_source_folder}")
#         logger.debug(f"data_destination_folder{data_destination_folder}")
#         if not data_source_folder:
#             data_source_folder = QFileDialog.getExistingDirectory(None, "Select Directory Source")
#         if not data_destination_folder:
#             data_destination_folder = QFileDialog.getExistingDirectory(None, "Select Directory Destination")
#
#         if data_source_folder and data_destination_folder:
#             insta = FileCopyProgress()
#             insta.copy_files(scr=data_source_folder, dest=data_destination_folder)
#
#         return data_destination_folder
#
#     @staticmethod
#     def verification(*args, **kwargs):
#         logger.debug('verification')
#         ok_bool_list = [True]
#         param = kwargs
#         for k, v in param.items():
#             if not v:
#                 if k in ['suffix', 'csv_file']:
#                     ok_bool_list.append(True)
#                 else:
#                     ok_bool_list.append(False)
#         return not (False in ok_bool_list)

# Plotting tool
class Plotting:
    def __init__(self, *args, **kwargs):

        # plot information
        self.kwargs = kwargs
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.args = args

    @staticmethod
    def get_script_name(script_path):
        """Retrieve script_name from path"""
        return os.path.abspath(script_path).split(os.sep)[-1].replace('.py', '')

    @staticmethod
    def get_figure_name(script_name, *args, **kwargs):
        """Figure naming schema : script_name_arg1_arg2..."""
        return script_name+"_".join(args)

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
        print_test = lambda txt, cdn: logger.debug(f"{txt}{'-' * (90 - len(txt))}{str(cdn)}")

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
            # logger.debug(ViewTree.current_item_path(qtreewidgetitem))
            return ViewTree.current_item_path_value_dict(qtreewidgetitem)
        else:
            logger.debug("selected item have one or multiple child")
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

        self.counter = 1
        self.time_gap = [0,0]

    def init_configuration_1(self):
        logger.debug('init_configuration_1')

        # Dictionnary for creating subwindows
        self.subwindows_init = Configuration1.subwindows_dictionary()

        # Creating a dictionary to contain every widget appearing on the media_viewer
        self.media_viewer_tab_dict = Configuration1.media_viewer_dictionary()

        # Customize media_viewer
        self.subwindows_init['media_viewer']['widget'].setTabsClosable(True)
        self.subwindows_init['media_viewer']['widget'].tabCloseRequested.connect(self.delete_Tab)
        self.subwindows_init['media_viewer']['widget'].addTab(self.media_viewer_tab_dict['svg_viewer'], 'svg_viewer')


        # Initiate parameters to be editable in a future sub-windows
        self.param = Configuration1.tmz_ov_param_dictionary()
        self.csv_files = []#[self.param['csv_file'], r"C:\Users\VmWin\Pictures\test\Segmentation\Project 3 SOC glioma IMC (McGill)\20200702\OneDrive_5_7-14-2020\Pano 01_Col5-13_1_ROI 10_NP14-1026-2A_10\10_NP14-1026-2A_10.csv"] # testing

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
        logger.debug('populate_minimal_simulation_information')
        qpushbutton_key_list = list(self.option_command.keys())

        for k ,v in self.simulation_config_widget.items():
            if type(v)==type(QPushButton()):
                qpushbutton_key_list.append(k)

        for key, value in {**self.simulation_config_widget, **self.option_command}.items():

            if key in qpushbutton_key_list:
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

                if key == 'run_simulation':
                    def updater():
                        [self.option_command[k].setEnabled(False) for k in self.option_command.keys()]
                        self.foo()

                fun = updater


                if key == 'convert_scan_to_csv':
                    temp_dict = Configuration1.type_dict()
                    fun = lambda:Data.data_conversion_segmentation_celltypes(
                        r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\Segmentation", r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV", type_dict=temp_dict)


                if key == 'ten_ten_ten':
                    fun = self.test_ten_ten_ten_on_table

                if key == 'tmz_ov_simulation_launcher':
                    fun = self.tmz_ov_simulation_launcher

                value.clicked.connect(fun)

            self.subwindows_init['minimal_simulation_information']['layout'].addRow(key, value)
    def delete_Tab(self, index):
        logger.debug('delete_Tab')
        widget = self.subwindows_init['media_viewer']['widget'].widget(index)
        if not widget == self.media_viewer_tab_dict['svg_viewer']:
            # Delete correspondence
            title = self.subwindows_init['media_viewer']['widget'].tabText(index)
            del self.media_viewer_tab_dict[title]
            # Remove tab
            self.subwindows_init['media_viewer']['widget'].removeTab(index)
    def init_minimal_xml_setup(self):
        logger.debug('init_minimal_xml_setup')
        short = self.subwindows_init['minimal_xml_setup']['widget']
        short.clear()
        value = Config.xml2dict(self.param['xml_template_file'])
        short.fill_item(short.invisibleRootItem(), value)


    # Simulation related
    def foo(self):
        logger.debug('foo')

        # for updating progress bar
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.current_simulation_progress_update)
        self.timer.timeout.connect(self.is_current_simulation_finish)

        # set up simulation
        self.set_up_simulation()

        # make gui change
        self.show_param_on_widget()
        self.update_csv_file_table()
        if self.counter-1>0:
            self.color_row_in_green(self.counter-2)
        self.color_row_in_yellow(self.counter-1)
        self.init_minimal_xml_setup()

        self.subwindows_init['progress_view']['widget'].element['local_']['progress_bar'].setMinimum(0)
        self.subwindows_init['progress_view']['widget'].element['local_']['progress_bar'].setMaximum(self.param['counter_end'])

        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setMinimum(0)
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setMaximum(len(self.csv_files))

        # start thread
        self.current_simulation_progress = 0
        self.current_simulation_step_delta_time = 0
        self.current_simulation = Simulation2(**{**self.param,**{'parent':self}})
        self.current_simulation.setup_thread()

        # start timer
        self.timer.start()
        self.start_time = time.time()

    def set_up_simulation(self):
        logger.debug('setup_simulation')

        # Automatic suffix for uniqueness
        self.param['suffix'] = Configuration1.now_time_in_str()
        self.param['data_destination_folder'] = self.export_folder_naming_rule()
        self.param['csv_file'] = self.csv_files[self.counter-1]

        # copy csv to the right destination
        csv_file_name = self.param['csv_file'].split(os.sep)[-1]
        csv_copy_path = os.path.join(self.param['configuration_files_destination_folder'], csv_file_name)

        QFile.copy(self.param['csv_file'], csv_copy_path)
        if not QFile.copy(self.param['csv_file'], csv_copy_path):
            logger.debug("overwriting current csv")
            QFile.remove(csv_copy_path)
            QFile.copy(self.param['csv_file'], csv_copy_path)

        # Maybe a condition to disable it
        # Automatic change to xml
        if self.automatic_change_to_config():

            # create xml config file from the template and from the changes
            self.create_xml_from_template_change(**self.param)

        # Return configured simulation object
        for k, v in self.param.items():
            logger.debug(f"{k}{'.' * (100 - len(k))}{v}")
    def show_param_on_widget(self):
        logger.debug('show_param_on_widget')
        # show param value on screen
        for k, v in self.param.items():
            if not type(self.simulation_config_widget[k]) == type(QPushButton()):
                logger.debug(f"{k}{'-' * (90 - len(k))}{v}")
                self.simulation_config_widget[k].setText(str(self.param[k]))

    @staticmethod
    def now_time_in_str():
        logger.debug('now_time_in_str')
        return str(QDateTime.currentDateTime().toString(Qt.ISODate)).replace(':', '_')
    @staticmethod
    def estimated_time(start_time, end_time, now_value, end_value):
        # logger.debug('estimated_time')
        delta_time = abs(end_time - start_time)
        delta_step = abs(end_value - now_value)

        total_time = delta_time * delta_step
        day_ = total_time//(60*60*24)
        hour_ = round(total_time - 60*60*24*day_)//(60*60)
        min_ = round(total_time - 60*60*hour_- 60*60*24*day_)//60
        sec_ = round(total_time - 60 * min_ - 60*60*hour_ - 60*60*24*day_)

        return {'sec': sec_, 'min': min_, 'hour': hour_, 'day':day_}
    def export_folder_naming_rule(self):
        logger.debug('export_folder_naming_rule')
        return os.path.join(self.param['data_destination_folder'], str(self.counter)+self.param['project_name'] + '_' + self.param['suffix'])
    def create_xml_from_template_change(self, *args, **kwargs):
        logger.debug('create_xml_from_template_change')
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
        logger.debug('automatic_change_to_config')
        xml_file = self.param['xml_template_file']
        csv_file = self.param['csv_file']

        if xml_file:
            xml_dict = Config.xml2dict(xml_file)

        if csv_file and xml_file:

            # read csv
            df = pd.read_csv(csv_file, header=None)
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
            x_ = max(x_max,abs(x_min))
            y_ = max(y_max, abs(y_min))
            rr_ = math.sqrt(x_**2+y_**2)
            tumour_radius = round((max(x_,y_)+rr_)/2)

            # cell_density
            cell_density = round(total_cell/(tumour_radius**2),3)

            #  A_frag
            a_frag = round(tumour_radius**2 * math.pi * (10**(-3))**2,3)

            # K_v
            k_V_star = round(tumour_radius * 1.58 * (10**(14))/1270)

            # k_C
            k_C_star = round(4.76 * (10**(6)) * k_V_star/(1.58 * (10**(14))/1270))


            # Change tumour radius
            self._XML_CHANGES.append({'path':['PhysiCell_settings','user_parameters','R','#text'], 'value':f'{tumour_radius}'})
            # Change domain
            for item, value in zip(['x_max','x_min', 'y_max', 'y_min'],[2.5*tumour_radius,-2.5*tumour_radius,2.5*tumour_radius,-2.5*tumour_radius]):
                self._XML_CHANGES.append({'path':['PhysiCell_settings','domain', item], 'value':f'{int(round(value))}'})
            # Change cell density
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'xhi', '#text'], 'value': f'{cell_density}'})
            # Change tumour surface A_frag
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'A_frag', '#text'], 'value': f'{a_frag}'})
            # Change K_v
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'K_V', '#text'], 'value': f'{k_V_star}'})
            # Change K_v
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'K_C', '#text'], 'value': f'{k_C_star}'})

            # Change path to csv
            self._XML_CHANGES.append({'path': ['PhysiCell_settings','initial_conditions','cell_positions','filename'], 'value':os.path.abspath(csv_file).split(os.sep)[-1]})

            # Verify that the option is enable
            if not Config.get2dict(*['PhysiCell_settings','initial_conditions','cell_positions','@enabled'], dictionary=xml_dict):
                self._XML_CHANGES.append({'path': ['PhysiCell_settings','initial_conditions','cell_positions','@enabled'], 'value':'"true"'})
            return True

        return False
    def current_simulation_progress_update(self):
        logger.debug('current_simulation_progress_update')

        # get progress from simulation
        self.subwindows_init['progress_view']['widget'].element['local_']['progress_bar'].setValue(self.current_simulation_progress)
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setValue(self.counter-1)
        self.update_local_label()
        self.update_global_label()

    def is_current_simulation_finish(self):
        logger.debug('is_current_simulation_finish')

        if self.current_simulation.finish and self.counter!=len(self.csv_files):
            self.time_gap = [self.start_time,time.time()]
            # set the previous row in green
            self.counter+=1

            self.timer.stop()
            self.param['csv_file'] = self.csv_files[self.counter-1]
            self.param['data_destination_folder'] = Configuration1.test_param_dictionary()['data_destination_folder']
            # next csv_file
            self.foo()

        elif self.current_simulation.finish and self.counter==len(self.csv_files):
            self.counter+=1
            self.current_simulation_progress_update()
            self.timer.stop()

        elif self.counter>len(self.csv_files):
            self.counter += 1
            self.current_simulation_progress_update()
            self.timer.stop()


    def update_global_label(self):
        logger.debug('update_global_label')

        arguments = [self.time_gap[0], time.time(), (self.counter-1),len(self.csv_files)]
        time_data = Configuration1.estimated_time(*arguments)
        day_, hour_, min_, sec_ = time_data['day'], time_data['hour'], time_data['min'], time_data['sec']

        if day_ >= 0 and hour_ >= 0 and min_ >= 0 and sec_ >= 0:
            self.subwindows_init['progress_view']['widget'].element['global_']['label'].setText(
                f"Estimated time before finishing {day_} day {hour_} hour {min_} min {round(sec_)} sec")
    def update_local_label(self):
        logger.debug('update_local_label')

        arguments = [0,self.current_simulation_step_delta_time,self.current_simulation_progress,self.param['counter_end']]
        time_data = Configuration1.estimated_time(*arguments)
        day_, hour_, min_, sec_ = time_data['day'], time_data['hour'], time_data['min'], time_data['sec']
        if day_ >= 0 and hour_ >= 0 and min_ >= 0 and sec_ >= 0:
            self.subwindows_init['progress_view']['widget'].element['local_']['label'].setText(
                f"Estimated time before finishing {day_} day {hour_} hour {min_} min {round(sec_)} sec")


    ## Ending simulation task related
    def endind_simulation_data_export(self):
        logger.debug('endind_simulation_data_export')

        ## copy data
        data_source_folder = self.param['data_source_folder']
        data_destination_folder = self.param['data_destination_folder']

        txt = f"data exported from {data_source_folder}\n to {data_destination_folder}"
        tmp = FileCopyProgress()
        element = {'progress_bar': None, 'label': QLabel(txt)}

        name = os.path.abspath(self.param['csv_file']).split(os.sep)[-1].replace('.csv', '')
        self.subwindows_init['progress_view']['widget'].add_element(element=element, name=name)
        tmp.copy_files(scr=data_source_folder, dest=data_destination_folder)

        return True


    ## Config interface
    @staticmethod
    def subwindows_dictionary():
        logger.debug('subwindows_dictionary')
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
                    'widget': ScrollableFormWidget(),
                    'layout': None
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
        dictionary['minimal_simulation_information']['layout'] = dictionary['minimal_simulation_information']['widget'].layout

        # tmp = ScrollableWidget()
        # tmp.layout.addWidget(dictionary['csv_file_table']['widget'])
        # dictionary['csv_file_table']['widget'] = tmp
        # dictionary['csv_file_table']['layout'] = dictionary['csv_file_table']['widget'].layout


        return dictionary
    @staticmethod
    def simulation_config_widget_dictionary():
        logger.debug('simulation_config_widget_dictionary')
        dictionary = {
            "program_path": SearchComboBox(),
            "project_name": QLineEdit(),
            'counter_end': QLineEdit(),
            "executable_name": QLineEdit(),
            "data_source_folder": SearchComboBox(),
            "data_destination_folder": SearchComboBox(),
            "suffix": QLineEdit(),
            # function
            "configuration_files_destination_folder": SearchComboBox(),
            "xml_template_file": QPushButton('click to choose'),
            "csv_file": QPushButton('click to choose'),
        }
        return dictionary
    @staticmethod
    def option_command_dictionary():
        logger.debug('option_command_dictionary')
        dictionary = {
            "special_csv_scan": QPushButton('click to choose'),
            "run_simulation": QPushButton('click to choose'),
            "convert_scan_to_csv": QPushButton('click to run'),
            "print_XML_CHANGES": QPushButton('click to run'),
            'test_copy': QPushButton('click to run'),
            'get_table_column':QPushButton('click to run'),
            'ten_ten_ten':QPushButton('click to run'),
            'tmz_ov_simulation_launcher':QPushButton('click to run')
        }
        return dictionary
    @staticmethod
    def media_viewer_dictionary():
        logger.debug('media_viewer_dictionary')
        dictionary = {'svg_viewer':svg(option=False)}
        return dictionary


    # test simualion
    def tmz_ov_simulation_launcher(self):
        logger.debug('tmz_ov_simulation_launcher')
        self.param = Configuration1.tmz_ov_param_dictionary()
        # self.param = Configuration1.tmz_param_dictionary()
        # self.param = Configuration1.ov_param_dictionary()
        # update xml window (just to see it)
        self.init_minimal_xml_setup()

        # load csv_file
        source_ = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV\Segmentation"
        # self.csv_files = Data.scan_csv_file(source=source_)

        # choose csv files
        self.test_ten_ten_ten_on_table()
        # run simulation
        self.foo()
    def test_ten_ten_ten_on_table(self):
        logger.debug('test_ten_ten_ten_on_table')

        ten_min, ten_mean, ten_max = self.ten_ten_ten()
        data = (*ten_min,*ten_mean,*ten_max)
        self.csv_files = list(map(lambda item: item[0], data))
        name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv',''),sum(item[1::]), *item[1::])
        data = list(map(name, data))


        self.insert_data_in_csv_table(data)
    def ten_ten_ten(self):
        logger.debug('ten_ten_ten')

        csv_files = Data.scan_csv_file(source=r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV")
        tuple_for_table = Configuration1.tuple_csv_file_freq(csv_files)

        start = 0
        stop = min(len(tuple_for_table),10)
        ten_min = [item for item in tuple_for_table[start:stop:]]

        half_position = len(tuple_for_table)//2
        start = max(10,half_position-5)
        stop = min(len(tuple_for_table),half_position+5)
        ten_mean = [item for item in tuple_for_table[start:stop:]]

        start = max(0, len(tuple_for_table)-10)
        stop = len(tuple_for_table)
        ten_max = [item for item in tuple_for_table[start:stop:]]

        return ten_min, ten_mean, ten_max


    # Parameters for test
    @staticmethod
    def tmz_ov_param_dictionary():
        logger.debug('tmz_ov_param_dictionary')

        param = {
            'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
            'project_name': "gbm-tmz-ov",
            'executable_name': "gbm_tmz_ov.exe",
            'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
            'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus",
            'suffix': "",
            'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\tmz_virus.xml",
            'csv_file': "",
            'configuration_files_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_tmz_ov\config",
            'counter_end': 144
        }
        return param
    @staticmethod
    def tmz_param_dictionary():
        logger.debug('tmz_ov_param_dictionary')

        param = {
            'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
            'project_name': "gbm_tmz",
            'executable_name': "gbm_tmz.exe",
            'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
            'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz",
            'suffix': "",
            'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\tmz.xml",
            'csv_file': "",
            'configuration_files_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_tmz\config",
            'counter_end': 144
        }
        return param
    @staticmethod
    def ov_param_dictionary():
        logger.debug('tmz_ov_param_dictionary')
        param = {
            'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
            'project_name': "gbm-ov",
            'executable_name': "gbm_ov.exe",
            'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
            'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz",
            'suffix': "",
            'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\virus.xml",
            'csv_file': "",
            'configuration_files_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov\config",
            'counter_end': 144
        }
        return param


    @staticmethod
    def test_param_dictionary():
        logger.debug('test_param_dictionary')
        param = {
            'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
            'project_name': "gbm-ov-tmz-immune-stroma-patchy-sample",
            'executable_name': "gbm_ov_tmz_immune_stroma_patchy.exe",
            'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
            'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus",
            'suffix': "2022-08-03T09_42_54",
            'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\tmz_virus.xml",
            'csv_file': r"C:\Users\VmWin\Pictures\test\Segmentation\Project 1 ICI glioma IMC\20200617\OneDrive_10_7-7-2020-1\Pano 01_Col2-3_1_ROI 05_X17-343-B2_5\05_X17-343-B2_5.csv",#                         r"C:\Users\VmWin\Pictures\test\Segmentation\Project 3 SOC glioma IMC (McGill)\20200702\OneDrive_5_7-14-2020\Pano 01_Col5-13_1_ROI 10_NP14-1026-2A_10\10_NP14-1026-2A_10.csv"],
            'configuration_files_destination_folder':r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov_tmz_immune_stroma_patchy\config",
            'counter_end': 10
        }
        return param
    @staticmethod
    def empty_param_dictionary():
        logger.debug('empty_param_dictionary')
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
            # 'Cl BMDM': 5,
            # 'Cl MG': 5,
            # 'Alt BMDM': 6,
            # 'Alt MG': 6,
            'Endothelial cell': 4
        }
        return temp_dict
    @staticmethod
    def reverse_type_dict():
        temp_dict2 = {
            1: 'Th',
            2: 'Cancer',
            3: 'Tc',
            # 5: 'Cl BMDM/MG',
            # 6: 'Alt BMDM/MG',
            4: 'Endothelial cell'
        }
        return temp_dict2


    # csv table method
    def update_csv_file_table(self):
        logger.debug('update_csv_file_table')

        # data from self.csv_files
        data = Configuration1.tuple_csv_file_freq(self.csv_files)
        name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv', ''), sum(item[1::]), *item[1::])
        data = list(map(name, data))
        self.reset_csv_table()
        self.insert_data_in_csv_table(data)
    def reset_csv_table(self):
        logger.debug('clear_table')

        short = self.subwindows_init['csv_file_table']['widget']

        # short.setRowCount(0)
        # short.setColumnCount(0)
        short.clearContents()
        # short.clear()
        for i in range(short.rowCount()):
            short.removeRow(i)

        if short.columnCount() == 0:
            temp_dict2 = Configuration1.reverse_type_dict()
            columns = ['file_name', 'total_cell'] + list(temp_dict2.values())
            # Desactivate edit mode
            short.setEditTriggers(QAbstractItemView.NoEditTriggers)

            # set number of columns before the table is populated
            for _ in range(len(columns)):
                short.insertColumn(short.columnCount())

            short.setColumnCount(len(columns))
            short.setHorizontalHeaderLabels(columns)

            # visual preference
            short.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            short.horizontalHeader().setSectionResizeMode(len(columns), QHeaderView.Stretch)

            short.doubleClicked.connect(self.double_click_csv_table)

        return True
    def insert_data_in_csv_table(self, data):
        logger.debug('insert_data_in_csv_table')

        temp_dict2 = Configuration1.reverse_type_dict()

        # csv file table
        # short name
        self.reset_csv_table()
        short = self.subwindows_init['csv_file_table']['widget']

        short.setRowCount(len(data))
        k = 0
        for row in data:
            # Insert row
            # short.removeRow(short.rowCount())
            # short.insertRow(k)
            for i in range(short.columnCount()):
                short.setItem(k, i, QTableWidgetItem(f"{row[i]}"))
            k += 1
    def get_table_column(self, columnIndex=0):
        logger.debug('get_table_column')

        table = self.subwindows_init['csv_file_table']['widget']
        column_list = []
        for row in range(table.rowCount()):
            it = table.item(row, columnIndex)
            text = it.text() if it is not None else ""
            if text:
                column_list.append(text)
            else:
                column_list.append(False)
        return column_list
    def color_row_in_green(self, rowIndex):
        logger.debug('color_row_in_green')
        table = self.subwindows_init['csv_file_table']['widget']
        Configuration1.setColortoRow(table,rowIndex,QBrush(QColor.fromRgb(52,222,52)))
    def color_row_in_yellow(self, rowIndex):
        logger.debug('color_row_in_yellow')
        table = self.subwindows_init['csv_file_table']['widget']
        Configuration1.setColortoRow(table,rowIndex,QBrush(QColor.fromRgb(249,250,180)))
    @staticmethod
    def setColortoRow(table, rowIndex, color):
        logger.debug('setColortoRow')
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)
    def double_click_csv_table(self, event):
        logger.debug('double_click_csv_table')
        csv_file = self.csv_files[event.row()]
        csv_file_name = os.path.abspath(csv_file).split(os.sep)[-1].replace('.csv','')
        if not csv_file_name in self.media_viewer_tab_dict.keys():
            # get plot
            self.media_viewer_tab_dict[csv_file_name] = widget = pg.PlotWidget()
            widget.setBackground('w')
            self.subwindows_init['media_viewer']['widget'].addTab(widget, csv_file_name)

        self.subwindows_init['media_viewer']['widget'].setCurrentWidget(self.media_viewer_tab_dict[csv_file_name])







    @staticmethod
    def tuple_csv_file_freq(csv_files):
        logger.debug('tuple_csv_file_freq')

        # gather every csv file
        csv_number = []
        n = 15
        for csv_file in csv_files:

            try:
                df = pd.read_csv(csv_file, header=None)

                # Cell frequency count
                freq = df.iloc[:, 3].value_counts().to_dict()

                item = [0 for _ in range(n)]
                for key in sorted(freq.keys()):
                    item[int(key)] = freq[key]

                csv_number.append((csv_file, *item[1::]))


            except pd.errors.EmptyDataError:
                print('empty csv')

        # filter with condition
        condition = lambda k: k[1] > 5 and k[2] > 100 and k[3] > 5 and k[4] > 5
        # condition = lambda k: True if k else False
        new_list = list(filter(condition, csv_number))

        # Sort
        new_list.sort(key=lambda item: item[2])
        return new_list


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


