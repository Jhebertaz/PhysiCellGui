import os
FILENAME = 'tool_simulation.py'
PATH = os.path.realpath(__file__).strip(FILENAME)

#############
## Package ##
#############
import sys
import time

## PySide
from PySide6.QtCore import QFile, QThreadPool
from PySide6.QtWidgets import QLabel, QFileDialog

# Custom import
# import from custom
sys.path.insert(1, os.path.join(PATH, '..', '..', '..', 'scr', 'python', 'custom'))
from MultiThread import *
from FileCopyProgress import *


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

        # update progress bar
        self.parent.current_simulation_progress = n
        self.parent.current_simulation_step_delta_time = time.time()-self.start_time
        self.start_time = time.time()

    def result_function(self):
        pass

    def finish_function(self):

        # verify that all file are there
        existe1 = QFile.exists(os.path.join(self.kwargs['data_source_folder'], "final.svg"))
        filename = 'snapshot' + "%08i" % self.kwargs['counter_end'] + '.svg'
        existe2 = QFile.exists(os.path.join(self.kwargs['data_source_folder'], filename))

        if not(existe1 and existe2):
            print('redundancy')
            self.finish = None
            return

        ## ending task
        name = os.path.abspath(self.kwargs['csv_file']).split(os.sep)[-1].replace('.csv', '')
        txt = f"data exported from {self.kwargs['data_source_folder']}\n to {self.kwargs['data_destination_folder']}"
        element = {'progress_bar': None, 'label': QLabel(txt)}
        self.parent.subwindows_init['progress_view']['widget'].add_element(element=element, name=name)

        # Export data
        Simulation2.specific_export_output(**self.kwargs)
        # Make gif
        Simulation2.make_gif(data_source_folder=self.kwargs['data_destination_folder'], data_destination_folder=self.kwargs['data_destination_folder'])

        data_source_folder = self.kwargs['data_destination_folder']
        data_destination_folder = self.kwargs['data_destination_folder']

        # Independant Analysis
        # # plot
        # # cell vs time
        # script_path = os.path.join(PATH, 'plot_time_cell_number.py')
        # script_name = Plotting.get_script_name(script_path)
        # figure_name = name+'_'+script_name
        # counter_end = self.kwargs['counter_end']
        #
        # os.system(f"start cmd /c python {script_path} {data_source_folder} {data_destination_folder} {figure_name} {counter_end}""")
        #
        # # Chemokine concentration
        # moments = ['output' + "%08i" % (self.kwargs['counter_end']//2) + '.xml','final.xml']
        # for moment in moments:
        #     script_path = os.path.join(PATH, 'plot_concentration_substrate.py')
        #     script_name = Plotting.get_script_name(script_path)
        #     figure_name = name + '_'+moment+'_'+ script_name
        #
        #     os.system(f"start cmd /c python {script_path} {data_source_folder} {data_destination_folder} {figure_name} {moment}""")

        # for task in self.args:
        #     task()

        # call to do another simulation
        self.finish = True

    def worker_function(self, progress_callback):
        # Cleanup
        Simulation2.cleanup(**self.kwargs)

        # Start simulation
        Simulation2.run_simulation(**self.kwargs)

        # Parameters of the simulation
        param = self.kwargs

        # Some counter
        now_counter = 0
        other_counter = -40

        # emit progress
        progress_callback.emit(now_counter)

        # Timer start
        self.start_time = time.time()


        while not QFile.exists(os.path.join(param['data_source_folder'], "final.svg")) and other_counter<10:
            # wait one second
            time.sleep(1)
            other_counter+=1

            # check for the lastest every sec svg file and took is number
            filename = 'snapshot' + "%08i" % now_counter + '.svg'

            if QFile.exists(os.path.join(param['data_source_folder'], filename)):
                now_counter += 1
                other_counter = 0
                progress_callback.emit(now_counter)

    ## Function
    @staticmethod
    def cleanup(*args, **kwargs):
        program_path = kwargs['program_path']
        os.system(f'make -C {program_path} reset')
        os.system(f'make -C {program_path} reset')
        os.system(f'make -C {program_path} data-cleanup')
        os.system(f'make -C {program_path} clean')
        return True
    @staticmethod
    def run_simulation(*args, **kwargs):
        program_path = kwargs['program_path']
        project_name = kwargs['project_name']
        executable_name = kwargs['executable_name']
        executable_path = os.path.abspath(os.path.join(program_path, executable_name))
        os.system(f'start cmd /c "make -C {program_path} {project_name} & make -C {program_path} & cd {program_path} & {executable_path}"')  # to keep cmd open --> cmd /c and /c for closing after task
        return True
    @staticmethod
    def make_gif(*args, **kwargs):
        data_source_folder = kwargs['data_source_folder']
        data_destination_folder = kwargs['data_destination_folder']
        os.system(f'start cmd /c "magick convert {data_source_folder}/s*.svg {data_destination_folder}/out.gif"')
        return f"{data_destination_folder}/out.gif"
    @staticmethod
    def specific_export_output(data_source_folder=None, data_destination_folder=None, *args, **kwargs):
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
        ok_bool_list = [True]
        param = kwargs
        for k, v in param.items():
            if not v:
                if k in ['suffix', 'csv_file']:
                    ok_bool_list.append(True)
                else:
                    ok_bool_list.append(False)
        return not (False in ok_bool_list)


