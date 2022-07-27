import os
import sys
import time
from PySide6.QtCore import QFile, QCoreApplication, QTimer, QDateTime, Qt
from PySide6.QtWidgets import QFileDialog, QInputDialog, QProgressDialog

import statistics

# basic info
filename = 'extra_function.py'
path = os.path.realpath(__file__).strip(filename)

sys.path.insert(1,path+"../../../scr/python/custom")
from FileCopyProgress import QFileCopyProgress as QFCP


def clear(program_path):
    # os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
    os.system(f'start cmd /c make -C {program_path} reset & make -C {program_path} reset & make -C {program_path} data-cleanup & make -C {program_path} clean"')
def run_simulation(project_name, exe_file_name):
    os.system(f'start cmd /c  "make {project_name} & make & .{os.sep}{exe_file_name}"') # to keep cmd open --> cmd /c
def make_gif():
    os.system('start cmd /c "make gif"')
def specific_export_output(parent,source=None,destination=None,project_name=None):

    if not source:
        source = QFileDialog.getExistingDirectory(parent, "Select Directory Source")
    if not destination:
        destination = QFileDialog.getExistingDirectory(parent, "Select Directory Destination")
    if not project_name:
        project_name, ok3 = QInputDialog.getText(parent, 'Name form', 'Project Name:')
    else:
        ok3 = True

    if ok3 and source and destination:
        dest_fold = f"{destination}/{project_name}"
        time_ = QDateTime.currentDateTime().toString(Qt.ISODate).replace(":","_")
        dest_fold += time_
        # Should be created else where

        insta = QFCP(parent=parent)
        insta.copy_files(scr=source, dest=dest_fold)

    return dest_fold, project_name, time_


functions = {
    "Clear" : lambda : clear(),
    # "gbm-ov-immune-stroma-patchy-sample-old" : lambda p='gbm-ov-immune-stroma-patchy-sample-old', n='gbm_ov_immune_stroma_patchy_old.exe' : run_simulation(p,n),
    # "gbm-ov-immune-stroma-patchy-sample-old-new" : lambda p='gbm-ov-immune-stroma-patchy-sample-old-new', n='gbm_ov_immune_stroma_patchy_old_new.exe' : run_simulation(p,n),
    # "gbm-ov-immune-stroma-patchy-sample" : lambda p='gbm-ov-immune-stroma-patchy-sample', n='gbm_ov_immune_stroma_patchy.exe' : run_simulation(p,n),
    # "Make gif": lambda : make_gif()
}


class SimulationProgress(QProgressDialog):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent

        self.counter_time = 0
        self.start_time = 0
        self.end_time = 0
        self.time_delta = []

        self.counter = 0
        self.counter_end = 144

        # Ordered ending task list
        if not "end_task_list" in kwargs.keys():
            self.end_task_list = [lambda:None]
        else:
            self.end_task_list = kwargs['end_task_list']

        # Ordered ending task list
        if not "recuring_task_list" in kwargs.keys():
            self.recuring_task_list = [lambda: None]
        else:
            self.recuring_task_list = lambda parent_=self:kwargs['recuring_task_list'](parent_)

        self.setRange(0, self.counter_end)
        self.setWindowTitle("Simulation progress")
        self.show()

        self.timer = QTimer()
        self.timer.setInterval(500)


        self.timer.timeout.connect(self.recurring_function)
        self.timer.timeout.connect(self.update_estimating_time)
        # self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

    # TODO : make it usuable outside of this specific situation
    def recurring_function(self):
        # Search for new file
        # def convert_in_str(x):
        #     xs = str(x)
        #     base = list("00000000")
        #     for n in range(len(str(xs))):
        #         base[-len(xs) + n] = xs[n]
        #     return ''.join(base)

        if self.wasCanceled():
            self.timer.stop()
            self.close()
            return


        if not QFile.exists(r"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output\final.svg"):

            # check for the lastest every sec svg file and took is number
            n = self.counter + 1
            filename = 'snapshot' + "%08i" % n + '.svg'
            if QFile.exists(rf"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output\{filename}"):
                self.counter += 1
                self.end_time = time.time()
                self.update_estimating_time()
                self.counter_time = 0


                # self.setLabelText(f"Estimated time before finishing {} min {}")
                self.start_time = time.time()

                self.setValue(self.counter)
                # TODO : plot1

                QCoreApplication.processEvents()
            self.update_estimating_time()


        else:
            self.timer.stop()
            self.close()
            self.end_function()

    def recurring_timer(self):
        self.counter += 1
        print("Counter: %d" % self.counter)

    def end_function(self):
        for task in self.end_task_list:
            task()
        return "DONE"
    def update_estimating_time(self):

        delta_time = abs(self.end_time - self.start_time)

        # self.time_delta.append(delta_time)

        # delta_time = statistics.mean(self.time_delta)
        delta_step = abs(self.counter_end - self.counter)
        total_time = delta_time * delta_step

        min = round(total_time) // 60
        sec = round(abs(total_time - 60 * min))

        # self.counter_time += 1
        # time_pass = self.counter_time
        #
        #
        # if time_pass>60:
        #     min -= round(time_pass)//60

        # else:
        #     if sec+time_pass>60:
        #         min += round(sec+time_pass)//60
        #         sec = sec+time_pass - round(sec+time_pass)*60
        #     else:
        #         sec += time_pass-(time_pass//60) * 60
        #         print(sec)

        if min>0 and sec>0:
            self.setLabelText(f"Estimated time before finishing {min} min {round(sec)} sec")

# gbm_ov_immune_stroma_patchy_old_new
# gbm_ov_immune_stroma_patchy_old
# gbm_ov_immune_stroma_patchy
