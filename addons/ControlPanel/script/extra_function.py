import os
import shutil
# export result
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileDialog, QInputDialog, QLineEdit


def export(source, destination):


    pass

def clear():
    os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
def run_simulation(project_name, exe_file_name):
    os.system(f'start cmd /k  "make {project_name} & make & .\{exe_file_name}"')
def make_gif():
    os.system('start cmd /c "make gif"')


functions = {
    "Export" : lambda s, d : export(s,d),
    "Clear" : lambda : clear(),
    "gbm-ov-immune-stroma-patchy-sample-old" : lambda p='gbm-ov-immune-stroma-patchy-sample-old', n='gbm_ov_immune_stroma_patchy_old.exe' : run_simulation(p,n),
    "gbm-ov-immune-stroma-patchy-sample-old-new" : lambda p='gbm-ov-immune-stroma-patchy-sample-old-new', n='gbm_ov_immune_stroma_patchy_old_new.exe' : run_simulation(p,n),
    "gbm-ov-immune-stroma-patchy-sample" : lambda p='gbm-ov-immune-stroma-patchy-sample', n='gbm_ov_immune_stroma_patchy.exe' : run_simulation(p,n),
    "Make gif" : lambda : make_gif()
}
# gbm_ov_immune_stroma_patchy_old_new
# gbm_ov_immune_stroma_patchy_old
# gbm_ov_immune_stroma_patchy
