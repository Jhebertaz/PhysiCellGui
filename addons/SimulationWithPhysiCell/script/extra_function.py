import os
FILENAME = 'extra_function.py'
PATH = os.path.realpath(__file__).strip(FILENAME)

#############
## Package ##
#############

import sys
import time

# Data Science
import math
import pandas as pd
import pyqtgraph as pg

## PySide
from PySide6.QtCore import QFile, QTimer, QDir, QDateTime, Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QTableWidget, QFormLayout, QLineEdit, QLabel,\
    QPushButton, QAbstractItemView, QTableWidgetItem, QHeaderView, QTabWidget


# Custom import
from .tool_data_management import *
from .tool_simulation import *

sys.path.insert(1, os.path.join(PATH ,'..','..','SvgViewer'))
from ADDON_SvgViewer import SvgViewer as svg

sys.path.insert(1, os.path.join(PATH, '..', '..', '..', 'scr', 'python', 'custom'))
from ViewTree import *
from ScrollableFormWidget import *
from MultipleProgressBar import *
from SearchComboBox import *


class Configuration1:

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args

        self.counter = 1
        self.redundancy_counter = 0
        self.time_gap = [0, 0]

    def init_configuration_1(self):

        # Dictionnary for creating subwindows
        self.subwindows_init = Configuration1.subwindows_dictionary()

        # Creating a dictionary to contain every widget appearing on the media_viewer
        self.media_viewer_tab_dict = Configuration1.media_viewer_dictionary()

        # Customize media_viewer
        self.subwindows_init['media_viewer']['widget'].setTabsClosable(True)
        self.subwindows_init['media_viewer']['widget'].tabCloseRequested.connect(self.delete_Tab)
        self.subwindows_init['media_viewer']['widget'].addTab(self.media_viewer_tab_dict['svg_viewer'], 'svg_viewer')


        # Initiate parameters to be editable in a future sub-windows
        self.param = Configuration1.empty_param_dictionary()
        self.original_data_destination_folder = Configuration1.empty_param_dictionary()['data_destination_folder']

        self.csv_files = []

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
        qpushbutton_key_list = list(self.option_command.keys())

        for k ,v in self.simulation_config_widget.items():
            if type(v) == type(QPushButton()):
                qpushbutton_key_list.append(k)

        for key, value in {**self.simulation_config_widget, **self.option_command}.items():

            if key in qpushbutton_key_list:
                def updater():
                    pass

                if key == 'csv_files_source':
                    def updater():
                        file_ = Data.loadFiles()
                        if file_:
                            self.csv_files = file_
                            self.update_csv_file_table()

                # if key == 'special_csv_scan':
                #     def updater():
                #         source_ = QFileDialog.getExistingDirectory(None, "Find Directory",".")
                #         if source_:
                #             self.csv_files = Data.scan_csv_file(source=source_)
                #             self.update_csv_file_table()

                if key == 'xml_template_file':
                    def updater():
                        filter = "XML (*.xml)"
                        file_name = QFileDialog()
                        file_name.setFileMode(QFileDialog.ExistingFiles)
                        xml_file_, filter = file_name.getOpenFileName(None, "Find xml_template_file", ".", filter)

                        if xml_file_:
                            self.param['xml_template_file'] = xml_file_
                            short = QDir.toNativeSeparators(xml_file_).split(os.sep)[-1]
                            self.simulation_config_widget['xml_template_file'].setText(short)
                            self.init_minimal_xml_setup()
                if key == 'csv_file':
                    def updater():
                        filter = "CSV (*.csv)"
                        file_name = QFileDialog()
                        file_name.setFileMode(QFileDialog.ExistingFiles)
                        csv_file_, filter = file_name.getOpenFileName(None, "Find csv_file",".", filter)

                        if csv_file_:
                            self.param['xml_template_file'] = csv_file_
                            short = QDir.toNativeSeparators(csv_file_).split(os.sep)[-1]
                            self.simulation_config_widget['csv_file'].setText(short)
                            # self.init_minimal_xml_setup()


                if key == 'run_simulation':
                    def updater():
                        [self.option_command[k].setEnabled(False) for k in self.option_command.keys()]
                        self.foo()

                fun = updater

                # if key == 'convert_scan_to_csv':
                #     temp_dict = Configuration1.type_dict()
                #     fun = lambda:Data.data_conversion_segmentation_celltypes(self.param["csv_files_source"], r"C:\Users\VmWin\Pictures\test", type_dict=temp_dict)

                # if key == 'ten_ten_ten':
                #     fun = self.test_ten_ten_ten_on_table
                # if key == 'tmz_ov_simulation_launcher':
                #     fun = self.tmz_ov_simulation_launcher
                # if key == 'tmz_simulation_launcher':
                #     fun = self.tmz_simulation_launcher
                # if key == 'ov_simulation_launcher':
                #     fun = self.ov_simulation_launcher
                if key == 'general_launcher':
                    fun = self.general_launcher
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

    # Shows the xml in subwindow
    def init_minimal_xml_setup(self):

        short = self.subwindows_init['minimal_xml_setup']['widget']
        short.clear()
        value = Config.xml2dict(self.param['xml_template_file'])
        short.fill_item(short.invisibleRootItem(), value)

    # Simulation related
    def foo(self):
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

        # Coloring previous in green
        i=1
        while self.counter-i>0:
            self.color_row_in_green(self.counter-i-1)
            i += 1
        i = None

        self.color_row_in_yellow(self.counter-1)
        self.init_minimal_xml_setup()

        # configure local progress bar
        self.subwindows_init['progress_view']['widget'].element['local_']['progress_bar'].setMinimum(0)
        self.subwindows_init['progress_view']['widget'].element['local_']['progress_bar'].setMaximum(self.param['counter_end'])

        # configure global progress bar
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

        # Automatic suffix for uniqueness
        self.param['suffix'] = Configuration1.now_time_in_str()
        self.param['data_destination_folder'] = self.export_folder_naming_rule()
        self.param['csv_file'] = self.csv_files[self.counter-1]

        # copy csv to the right destination
        csv_file_name = self.param['csv_file'].split(os.sep)[-1]
        csv_copy_path = os.path.join(self.param['configuration_files_destination_folder'], csv_file_name)

        QFile.copy(self.param['csv_file'], csv_copy_path)
        if not QFile.copy(self.param['csv_file'], csv_copy_path):
            QFile.remove(csv_copy_path)
            QFile.copy(self.param['csv_file'], csv_copy_path)
            print(csv_copy_path)

        # Maybe a condition to disable it
        # Automatic change to xml
        if self.automatic_change_to_config():

            # create xml config file from the template and from the changes
            self.create_xml_from_template_change(**self.param)

        # Return configured simulation object
        for k, v in self.param.items():
            print(f"{k}{'.' * (100 - len(k))}{v}")

    # update parameters on subwindow
    def show_param_on_widget(self):

        # show param value on screen
        for k, v in self.param.items():
            if not type(self.simulation_config_widget[k]) == type(QPushButton()):
                print(f"{k}{'-' * (90 - len(k))}{v}")
                self.simulation_config_widget[k].setText(str(self.param[k]))

    @staticmethod
    def now_time_in_str():
        return str(QDateTime.currentDateTime().toString(Qt.ISODate)).replace(':', '_')

    @staticmethod
    def estimated_time(start_time, end_time, now_value, end_value):
        delta_time = abs(end_time - start_time)
        delta_step = abs(end_value - now_value)

        total_time = delta_time * delta_step
        day_ = total_time//(60*60*24)
        hour_ = round(total_time - 60*60*24*day_)//(60*60)
        min_ = round(total_time - 60*60*hour_- 60*60*24*day_)//60
        sec_ = round(total_time - 60 * min_ - 60*60*hour_ - 60*60*24*day_)

        return {'sec': sec_, 'min': min_, 'hour': hour_, 'day':day_}
    def export_folder_naming_rule(self):
        return os.path.join(self.param['data_destination_folder'], str(self.counter)+self.param['project_name'] + '_' + self.param['suffix'])
    def create_xml_from_template_change(self, *args, **kwargs):
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
        xml_file = self.param['xml_template_file']
        csv_file = self.param['csv_file']

        if xml_file:
            xml_dict = Config.xml2dict(xml_file)

        if csv_file and xml_file:

            # read csv
            df = pd.read_csv(csv_file, header=None)
            df.columns = ['x', 'y', 'z', 'type']
            cell_type_concern = list(map(float, range(1, 5)))
            sub = df.loc[
                df['type'].isin(cell_type_concern)
            ]

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
            rr_ = math.sqrt(x_**2+y_**2)               # tumour_radius
            tumour_radius = round((max(x_,y_)+rr_)/2)  # rr

            #  A_frag
            # a_frag = round(tumour_radius**2 * math.pi * (10**(-3))**2,3)
            a_frag = round(abs((x_max - x_min) * (y_max - y_min)), 3)

            # cell_density
            cell_density = round(total_cell/(a_frag), 5) # the number of digit HERE is a sensitive parameter

            # unit conversion
            a_frag = round(abs((x_max - x_min) * (y_max - y_min))*(10**(-3))**2, 3)

            # K_v
            k_V_star = round(tumour_radius * 1.58 * (10**(14))/1270)

            # k_C
            k_C_star = round(4.76 * (10**(6)) * tumour_radius/1270)

            # Change tumour radius
            self._XML_CHANGES.append({'path':['PhysiCell_settings','user_parameters','R','#text'], 'value':f'{tumour_radius}'})

            length = min(1.5*tumour_radius*(1+self.redundancy_counter*(15/100)), 1510)

            # Change domain
            for item, value in zip(['x_max','x_min', 'y_max', 'y_min'],[length,-length,length,-length]):
                self._XML_CHANGES.append({'path':['PhysiCell_settings','domain', item], 'value':f'{int(round(value))}'})
            # Change cell density
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'xhi', '#text'], 'value': f'{cell_density}'})
            # Change tumour surface A_frag
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'A_frag', '#text'], 'value': f'{a_frag}'})
            # Change K_v
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'K_V', '#text'], 'value': f'{k_V_star}'})
            # Change K_v
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'user_parameters', 'K_C', '#text'], 'value': f'{k_C_star}'})
            # Change max time based on param
            self._XML_CHANGES.append({'path': ['PhysiCell_settings', 'overall', 'max_time', '#text'], 'value': f'{self.param["counter_end"]*30}'})
            # Change path to csv
            self._XML_CHANGES.append({'path': ['PhysiCell_settings','initial_conditions','cell_positions','filename'], 'value':os.path.abspath(csv_file).split(os.sep)[-1]})

            # Verify that the option is enable
            if not Config.get2dict(*['PhysiCell_settings','initial_conditions','cell_positions','@enabled'], dictionary=xml_dict):
                self._XML_CHANGES.append({'path': ['PhysiCell_settings','initial_conditions','cell_positions','@enabled'], 'value':'"true"'})
            return True

        return False

    # Recurrent function
    def is_current_simulation_finish(self):

        if self.current_simulation.finish == None:
            # Restart and increase lenght
            self.redundancy_counter +=1

            # skip this file
            if self.redundancy_counter == 15:
                # self.counter += 1
                self.timer.stop()
                self.param['csv_file'] = self.csv_files[self.counter - 1]
                self.param['data_destination_folder'] = self.original_data_destination_folder
                self.param['data_destination_folder'] = self.export_folder_naming_rule()

                # reset redundancy counter
                redundancy_counter = 0
                self.current_simulation.finish = True

            self.param['data_destination_folder'] = self.export_folder_naming_rule()
            self.foo()

        if self.current_simulation.finish and self.counter!=len(self.csv_files):
            self.time_gap = [self.start_time,time.time()]

            self.counter+=1

            self.timer.stop()
            self.param['csv_file'] = self.csv_files[self.counter-1]
            self.param['data_destination_folder'] = self.original_data_destination_folder

            # reset redundancy counter
            redundancy_counter = 0

            # next csv_file
            self.foo()

        # end up simulation
        elif self.current_simulation.finish and self.counter==len(self.csv_files):
            self.counter+=1
            self.current_simulation_progress_update()
            self.timer.stop()

        # end up simulation
        elif self.counter>len(self.csv_files):
            self.counter += 1
            self.current_simulation_progress_update()
            self.timer.stop()

    # Progress view
    def current_simulation_progress_update(self):
        # get progress from simulation
        self.subwindows_init['progress_view']['widget'].element['local_']['progress_bar'].setValue(self.current_simulation_progress)
        self.subwindows_init['progress_view']['widget'].element['global_']['progress_bar'].setValue(self.counter-1)
        self.update_local_label()
        self.update_global_label()
    def update_global_label(self):
        arguments = [self.time_gap[0], time.time(), (self.counter-1),len(self.csv_files)]
        time_data = Configuration1.estimated_time(*arguments)
        day_, hour_, min_, sec_ = time_data['day'], time_data['hour'], time_data['min'], time_data['sec']

        if day_ >= 0 and hour_ >= 0 and min_ >= 0 and sec_ >= 0:
            self.subwindows_init['progress_view']['widget'].element['global_']['label'].setText(
                f"Estimated time before finishing {day_} day {hour_} hour {min_} min {round(sec_)} sec")
    def update_local_label(self):
        arguments = [0,self.current_simulation_step_delta_time,self.current_simulation_progress,self.param['counter_end']]
        time_data = Configuration1.estimated_time(*arguments)
        day_, hour_, min_, sec_ = time_data['day'], time_data['hour'], time_data['min'], time_data['sec']
        if day_ >= 0 and hour_ >= 0 and min_ >= 0 and sec_ >= 0:
            self.subwindows_init['progress_view']['widget'].element['local_']['label'].setText(
                f"Estimated time before finishing {day_} day {hour_} hour {min_} min {round(sec_)} sec")

    ## Ending simulation task related
    def endind_simulation_data_export(self):

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

        return dictionary
    @staticmethod
    def simulation_config_widget_dictionary():
        # For set up object in minimal_simulation_information subwindow
        info_type, object_type = Configuration1.default_info_type(), Configuration1.default_object_type()
        dictionary={}
        for k ,v in info_type.items():
            dictionary[k] = object_type[v]()
        return dictionary
    @staticmethod
    def option_command_dictionary():
        # Extra button or option in mininal_simulation_information sub window
        dictionary = {
            # "special_csv_scan": QPushButton('click to choose'),
            # "run_simulation": QPushButton('click to choose'),
            'general_launcher':QPushButton('click to run'),
            # 'tmz_ov_simulation_launcher':QPushButton('click to run'),
            # 'tmz_simulation_launcher':QPushButton('click to run'),
            # 'ov_simulation_launcher':QPushButton('click to run')
        }
        return dictionary
    @staticmethod
    def media_viewer_dictionary():
        dictionary = {'svg_viewer':svg(option=False)}
        return dictionary



    # test simualion
    # def tmz_ov_simulation_launcher(self):
    #     self.param = Configuration1.test_param_dictionary()#tmz_ov_param_dictionary()
    #     self.original_data_destination_folder = Configuration1.test_param_dictionary()['data_destination_folder'] #tmz_ov_param_dictionary()['data_destination_folder']
    #
    #     # update xml window (just to see it)
    #     self.init_minimal_xml_setup()
    #
    #     # load csv_file
    #     source_ = self.param["csv_files_source"] #r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV\Segmentation"
    #
    #
    #     # self.test_ten_ten_ten_on_table()
    #     # choose csv files
    #     self.test_ten_ten_ten_density_on_table()
    #     # self.test_ten_ten_ten_on_table()
    #
    #     # run simulation
    #     # self.foo()
    # def tmz_simulation_launcher(self):
    #     self.param = Configuration1.tmz_param_dictionary()
    #     self.original_data_destination_folder = Configuration1.tmz_param_dictionary()['data_destination_folder']
    #
    #     # update xml window (just to see it)
    #     self.init_minimal_xml_setup()
    #
    #     # load csv_file
    #     source_ = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV\Segmentation"
    #     # self.csv_files = Data.scan_csv_file(source=source_)
    #
    #     # choose csv files
    #     # self.test_ten_ten_ten_density_on_table()
    #     # self.test_ten_ten_ten_on_table()
    #
    #     self.test_on_table()
    #     # run simulation
    #     # self.foo()
    # def ov_simulation_launcher(self):
    #     self.param = Configuration1.ov_param_dictionary()
    #     self.original_data_destination_folder = Configuration1.ov_param_dictionary()['data_destination_folder']
    #
    #
    #     # update xml window (just to see it)
    #     self.init_minimal_xml_setup()
    #
    #     # load csv_file
    #     source_ = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV\Segmentation"
    #     # self.csv_files = Data.scan_csv_file(source=source_)
    #
    #     # choose csv files
    #     # self.test_ten_ten_ten_density_on_table()
    #
    #     # self.test_ten_ten_ten_on_table()
    #     self.test_on_table()
    #     # run simulation
    #     # self.foo()

    def general_launcher(self):
        self.param = Configuration1.test_param_dictionary()
        self.original_data_destination_folder = self.param['data_destination_folder']

        self.show_param_on_widget()
            #Configuration1.empty_param_dictionary['data_destination_folder'] #test_param_dictionary()['data_destination_folder']

        # update xml window (just to see it)
        self.init_minimal_xml_setup()

        # How many csv files
        if len(self.csv_files)>1:
            # default
            self.general_selection()
            # self.ten_ten_ten_general(self.ten_ten_ten)
        else:
            self.csv_files.append(self.param['csv_file'])
            self.general_selection()
            print('one csv file')



        # run simulation
        self.foo()


    # def test_on_table(self):
    #
    #     source_ = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV\Segmentation"
    #     csv_files = Data.scan_csv_file(source=source_)
    #     data = Configuration1.tuple_csv_file_freq(csv_files)
    #
    #     self.csv_files = list(map(lambda item: item[0], data))[-2::]
    #     name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv', ''), sum(item[1::]), *item[1::])
    #     data = list(map(name, data))
    #
    #     self.insert_data_in_csv_table(data)
    #
    # # Special selection
    # def test_ten_ten_ten_on_table(self):
    #
    #     ten_min, ten_mean, ten_max = self.ten_ten_ten()
    #     data = (*ten_min, *ten_mean, *ten_max)
    #     self.csv_files = list(map(lambda item: item[0], data))
    #     name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv',''),sum(item[1::]), *item[1::])
    #     data = list(map(name, data))
    #
    #
    #     self.insert_data_in_csv_table(data)
    # def ten_ten_ten(self):
    #
    #     csv_files = Data.scan_csv_file(source=self.param['csv_files_source'])
    #     tuple_for_table = Configuration1.tuple_csv_file_freq(csv_files)
    #
    #     start = 0
    #     stop = min(len(tuple_for_table), 10)
    #     ten_min = [item for item in tuple_for_table[start:stop:]]
    #
    #     half_position = len(tuple_for_table)//2
    #     start = max(10,half_position-5)
    #     stop = min(len(tuple_for_table),half_position+5)
    #     ten_mean = [item for item in tuple_for_table[start:stop:]]
    #
    #     start = max(0, len(tuple_for_table)-10)
    #     stop = len(tuple_for_table)
    #     ten_max = [item for item in tuple_for_table[start:stop:]]
    #     return ten_min, ten_mean, ten_max
    # def ten_ten_ten_density(self):
    #
    #     csv_files = Data.scan_csv_file(source=r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\data\CSV")
    #     tuple_for_table = Configuration1.tuple_csv_file_density(csv_files)
    #
    #     start = 0
    #     stop = min(len(tuple_for_table),10)
    #     ten_min = [item for item in tuple_for_table[start:stop:]]
    #     # print(*ten_min,sep='\n')
    #     half_position = len(tuple_for_table)//2
    #     start = max(10,half_position-5)
    #     stop = min(len(tuple_for_table),half_position+5)
    #     ten_mean = [item for item in tuple_for_table[start:stop:]]
    #
    #     start = max(0, len(tuple_for_table)-10)
    #     stop = len(tuple_for_table)
    #     ten_max = [item for item in tuple_for_table[start:stop:]]
    #
    #     return ten_min, ten_mean, ten_max
    # def test_ten_ten_ten_density_on_table(self):
    #
    #     ten_min, ten_mean, ten_max = self.ten_ten_ten_density()
    #     data = (*ten_min, *ten_mean, *ten_max)
    #     self.csv_files = list(map(lambda item: item[0], data))
    #     name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv',''), sum(item[2::]), *item[1::])
    #     data = list(map(name, data))
    #     # print(*data,sep='\n')
    #
    #
    #     self.insert_data_in_csv_table(data)


    def general_selection(self, function=None):
        print("general_selection")

        if function == None:
            # general selection function
            function = lambda csv_files: Configuration1.tuple_csv_files(csv_files)


        selection = function(self.csv_files)    # must return a list (or tuple) of tuple (csv path, #cell1,#cell2,...,#celln, other, other, other)
        # if your function exclude some csv_file we have to refresh csv_files list
        self.csv_files = list(map(lambda item: item[0], selection))

        # given one item :
        #                   (csv name, total cells, other, other, other...)
        name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv', ''), sum(item[2::]), *item[1::])
        data = list(map(name, selection))
        print(data)
        self.insert_data_in_csv_table(data)

    # def ten_ten_ten_general(self, function):
    #     ten_min, ten_mean, ten_max = function()
    #     data = (*ten_min, *ten_mean, *ten_max)
    #     self.csv_files = list(map(lambda item: item[0], data))
    #
    #     name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv', ''), sum(item[2::]), *item[1::])
    #     data = list(map(name, data))
    #     # print(*data,sep='\n')
    #
    #     self.insert_data_in_csv_table(data)

    # Parameters for test
    # @staticmethod
    # def tmz_ov_param_dictionary():
    #
    #     param = {
    #         'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
    #         'project_name': "gbm-tmz-ov",
    #         'executable_name': "gbm_tmz_ov.exe",
    #         'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
    #         'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus",
    #         'suffix': "",
    #         'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\tmz_virus.xml",
    #         'csv_file': "",
    #         'configuration_files_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_tmz_ov\config",
    #         'counter_end': 144
    #     }
    #     return param
    # @staticmethod
    # def tmz_param_dictionary():
    #     param = {
    #         'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
    #         'project_name': "gbm-tmz",
    #         'executable_name': "gbm_tmz.exe",
    #         'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
    #         'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz",
    #         'suffix': "",
    #         'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\tmz.xml",
    #         'csv_file': "",
    #         'configuration_files_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_tmz\config",
    #         'counter_end': 144
    #     }
    #     return param
    # @staticmethod
    # def ov_param_dictionary():
    #     param = {
    #         'program_path': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1",
    #         'project_name': "gbm-ov",
    #         'executable_name': "gbm_ov.exe",
    #         'data_source_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output",
    #         'data_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\ov",
    #         'suffix': "",
    #         'xml_template_file': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\template\virus.xml",
    #         'csv_file': "",
    #         'configuration_files_destination_folder': r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\sample_projects\gbm_ov\config",
    #         'counter_end': 144,
    #         'csv_files_source':"/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1/",
    #     }
    #     return param
    # @staticmethod
    # def test_param_dictionary():
    #     param = {
    #         'program_path': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1",
    #         'project_name': "gbm-tmz-ov",
    #         'executable_name': "gbm_tmz_ov",
    #         'data_source_folder': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1/output",
    #         'data_destination_folder': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Simulation/result/tmz_virus",
    #         'suffix': "2022-08-03T09_42_54",
    #         'xml_template_file': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Simulation/template/tmz_virus.xml",
    #         'csv_file': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Simulation/data/CSV/Segmentation/Project 1 ICI glioma IMC/20200617/OneDrive_11_7-7-2020-2/Pano 01_Col2-3_1_ROI 17_X17-526-B2_17/17_X17-526-B2_17.csv",
    #         'configuration_files_destination_folder':"/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1/sample_projects/gbm_tmz_ov/config",
    #         'counter_end': 10,
    #         'csv_files_source': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Simulation/data/CSV/Segmentation",
    #     }
    #     return param

    @staticmethod
    def empty_param_dictionary():
        param = {
            'program_path': None,  # path of the physicell program
            'project_name': None,  # string of on specific physicell program EG :gbm-tmz-ov
            'executable_name': None,  # string of the executable associated with the project_name
            'data_source_folder': None,  # path of the program output: it is not the path where you want your data to be
            'data_destination_folder': None,  # path where you want your data to be after each simulation
            'suffix': None,  #
            'xml_template_file': None,  # absolute path to the file
            'csv_file': None,  # absolute path to one csv file
            'configuration_files_destination_folder': None,
            # absolute path where your template file and your cvs file are needed
            'counter_end': 0,
            # specific parameter of the number of step your simulation run (eg 144 time 30 min for 4320 min)
            'csv_files_source': None,
        }

        return param

    @staticmethod
    def test_param_dictionary():
        param = {
            'program_path': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1",  # path of the physicell program
            'project_name': "gbm-tmz-ov",  # string of on specific physicell program EG :gbm-tmz-ov
            'executable_name': "gbm-tmz-ov",  # string of the executable associated with the project_name
            'data_source_folder': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1/output",  # path of the program output: it is not the path where you want your data to be
            'data_destination_folder': "/home/fiftyfour/Music",  # path where you want your data to be after each simulation
            'suffix': None,  #
            'xml_template_file': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Simulation/template/tmz_virus.xml",  # absolute path to the file
            'csv_file': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Simulation/data/CSV/Segmentation/Project 4 SOC glioma IMC (UofT)/20200810/OneDrive_8_8-18-2020/Pano 01_S1_B2_1_ROI 03_16-000288_3/03_16-000288_3.csv",  # absolute path to one csv file
            'configuration_files_destination_folder': "/home/fiftyfour/Documents/University/Bachelor/Ete2022/Stage/Code/Working/PhysiCell_V.1.10.1/sample_projects/gbm_tmz_ov/config",
            # absolute path where your template file and your cvs file are needed
            'counter_end': 144,
            # specific parameter of the number of step your simulation run (eg 144 time 30 min for 4320 min)
            'csv_files_source': None,
        }

        return param
    @staticmethod
    def default_info_type():
        info_type = {
            'program_path':         'path',
            'project_name':         'string',
            'executable_name':      'string',
            'data_source_folder':   'path',
            'data_destination_folder':  'path',
            'suffix':                   'string',
            'xml_template_file':        'file',
            'csv_file':                 'file',
            'configuration_files_destination_folder':   'path',
            'counter_end':                              'integer',
            'csv_files_source':                         'list',
        }
        return info_type
    @staticmethod
    def default_object_type():
        object_type = {
            'path': lambda: SearchComboBox(),  # this a custom object
            'file':lambda: QPushButton('click to choose'), # custom action associated
            'string': lambda:QLineEdit(),
            'integer': lambda:QLineEdit(),
            'list': lambda: QPushButton('click to choose')
        }
        return object_type
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

        # data from self.csv_files
        data = Configuration1.tuple_csv_files(self.csv_files)
        name = lambda item: (os.path.abspath(item[0]).split(os.sep)[-1].replace('.csv', ''), sum(item[2::]), *item[1::])
        data = list(map(name, data))
        self.reset_csv_table()
        self.insert_data_in_csv_table(data)
    def reset_csv_table(self):

        short = self.subwindows_init['csv_file_table']['widget']

        # short.setRowCount(0)
        # short.setColumnCount(0)
        short.clearContents()
        # short.clear()
        for i in range(short.rowCount()):
            short.removeRow(i)

        if short.columnCount() == 0:
            temp_dict2 = Configuration1.reverse_type_dict()
            columns = ['file_name', 'total_cell', 'cell_density'] + list(temp_dict2.values())
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
        table = self.subwindows_init['csv_file_table']['widget']
        Configuration1.setColortoRow(table,rowIndex,QBrush(QColor.fromRgb(52,222,52)))
    def color_row_in_yellow(self, rowIndex):
        table = self.subwindows_init['csv_file_table']['widget']
        Configuration1.setColortoRow(table,rowIndex,QBrush(QColor.fromRgb(249,250,180)))
    @staticmethod
    def setColortoRow(table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)

    def insert_plot_in_media_viewer(self,csv_file):
        csv_file_name = os.path.abspath(csv_file).split(os.sep)[-1].replace('.csv', '')
        if not csv_file_name in self.media_viewer_tab_dict.keys():

            # get plot
            self.media_viewer_tab_dict[csv_file_name] = widget = pg.PlotWidget()

            widget.setBackground('w')
            plot_item = pg.ScatterPlotItem(pxMode=False)

            df = pd.read_csv(csv_file, header=None)
            freq = df.iloc[:, 3].value_counts().to_dict()
            i = 1
            for k in freq.keys():
                sub = df.loc[df.iloc[:, 3] == k]
                spots = []
                x = sub[0].tolist()
                y = sub[1].tolist()
                plot_item.addPoints(x=x, y=y, size=10, brush=pg.intColor(i * 10, i * 10))

                i += 1
            i = None
            widget.addItem(plot_item)
            self.subwindows_init['media_viewer']['widget'].addTab(widget, csv_file_name)
            self.subwindows_init['media_viewer']['widget'].setCurrentWidget(self.media_viewer_tab_dict[csv_file_name])

    def double_click_csv_table(self, event):
        csv_file = self.csv_files[event.row()]
        self.insert_plot_in_media_viewer(csv_file)
        csv_file_name = os.path.abspath(csv_file).split(os.sep)[-1].replace('.csv','')

        # if not csv_file_name in self.media_viewer_tab_dict.keys():
        #
        #     # get plot
        #     self.media_viewer_tab_dict[csv_file_name] = widget = pg.PlotWidget()
        #
        #     widget.setBackground('w')
        #     plot_item = pg.ScatterPlotItem(pxMode = False)
        #
        #     df = pd.read_csv(csv_file, header=None)
        #     freq = df.iloc[:, 3].value_counts().to_dict()
        #     i=1
        #     for k in freq.keys():
        #         sub = df.loc[df.iloc[:, 3] == k]
        #         spots = []
        #         x = sub[0].tolist()
        #         y = sub[1].tolist()
        #         plot_item.addPoints(x=x,y=y, size=10, brush=pg.intColor(i * 10, i *10))
        #
        #
        #         i+=1
        #     i=None
        #     widget.addItem(plot_item)



        #   self.subwindows_init['media_viewer']['widget'].addTab(widget, csv_file_name)

        self.subwindows_init['media_viewer']['widget'].setCurrentWidget(self.media_viewer_tab_dict[csv_file_name])

    @staticmethod
    def tuple_csv_file(csv_file):

        n = 15
        try:
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
            x_ = max(x_max, abs(x_min))
            y_ = max(y_max, abs(y_min))
            rr_ = math.sqrt(x_ ** 2 + y_ ** 2)
            tumour_radius = round((max(x_, y_) + rr_) / 2)

            # cell_density
            cell_density = round(total_cell / (tumour_radius ** 2), 5)

            # Cell frequency count
            freq = df.iloc[:, 3].value_counts().to_dict()

            item = [0 for _ in range(n)]
            for key in sorted(freq.keys()):
                item[int(key)] = freq[key]

            return (csv_file, cell_density, *item[1::])


        except pd.errors.EmptyDataError:
            print('empty csv')
    @staticmethod
    def tuple_csv_files(csv_files):

        # gather every csv file
        csv_number = []
        for csv_file in csv_files:
            csv_number.append(Configuration1.tuple_csv_file(csv_file))

        return csv_number


        # filter with condition
        # condition = lambda k: k[2] > 5 and k[3] > 100 and k[4] > 5 and k[5] > 5
        # condition = lambda k: True if k else False
        # new_list = list(filter(condition, csv_number))

        # Sort
        # new_list.sort(key=lambda item: item[3])
        # return new_list

    @staticmethod
    def tuple_csv_file_freq(csv_files):

        # gather every csv file
        csv_number = []
        n = 15
        for csv_file in csv_files:

            try:
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
                x_ = max(x_max, abs(x_min))
                y_ = max(y_max, abs(y_min))
                rr_ = math.sqrt(x_ ** 2 + y_ ** 2)
                tumour_radius = round((max(x_, y_) + rr_) / 2)

                # cell_density
                cell_density = round(total_cell / (tumour_radius ** 2), 5)

                # Cell frequency count
                freq = df.iloc[:, 3].value_counts().to_dict()

                item = [0 for _ in range(n)]
                for key in sorted(freq.keys()):
                    item[int(key)] = freq[key]

                csv_number.append((csv_file, cell_density, *item[1::]))


            except pd.errors.EmptyDataError:
                print('empty csv')

        # filter with condition
        condition = lambda k: k[2] > 5 and k[3] > 100 and k[4] > 5 and k[5] > 5
        # condition = lambda k: True if k else False
        new_list = list(filter(condition, csv_number))

        # Sort
        new_list.sort(key=lambda item: item[3])
        return new_list
    @staticmethod
    def tuple_csv_file_density(csv_files):

        # gather every csv file
        csv_number = []
        n = 15
        for csv_file in csv_files:

            try:
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
                x_ = max(x_max, abs(x_min))
                y_ = max(y_max, abs(y_min))
                rr_ = math.sqrt(x_ ** 2 + y_ ** 2)
                tumour_radius = round((max(x_, y_) + rr_) / 2)

                # cell_density
                cell_density = round(total_cell / (tumour_radius ** 2), 5)

                #  A_frag
                a_frag = round(tumour_radius ** 2 * math.pi * (10 ** (-3)) ** 2, 3)

                # K_v
                k_V_star = round(tumour_radius * 1.58 * (10 ** (14)) / 1270)

                # k_C
                k_C_star = round(4.76 * (10 ** (6)) * k_V_star / (1.58 * (10 ** (14)) / 1270))

                # Cell frequency count
                freq = df.iloc[:, 3].value_counts().to_dict()

                item = [0 for _ in range(n)]
                for key in sorted(freq.keys()):
                    item[int(key)] = freq[key]

                csv_number.append((csv_file, cell_density, *item[1::]))

            except pd.errors.EmptyDataError:
                print('empty csv')

        # filter with condition
        condition = lambda k: k[2] > 5 and k[3] > 100 and k[4] > 5 and k[5] > 5
        # condition = lambda k: True if k else False
        new_list = list(filter(condition, csv_number))
        # Sort
        new_list.sort(key=lambda item: item[1])
        # print(*new_list, sep='\n')
        return new_list




