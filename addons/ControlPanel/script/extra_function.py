import os
# export result
def export(source, destination):
    pass
def clear():
    os.system('start cmd /c "make reset & make reset & make data-cleanup & make clean"')
def run_simulation(project_name, exe_file_name):
    os.system(f'start cmd /k  "make {project_name} & make & .\{exe_file_name}"')
def make_gif():
    os.system('start cmd /c make "make gif"')


functions = {
    "Export" : lambda s, d : export(s,d),
    "Clear" : lambda : clear(),
    "Run Simulation" : lambda p='gbm-ov-immune-stroma-patchy-sample-old', n='gbm_ov_immune_stroma_patchy_old.exe' : run_simulation(p,n),
    "Make gif" : lambda : make_gif()
}
# gbm_ov_immune_stroma_patchy_old_new
# gbm_ov_immune_stroma_patchy_old
# gbm_ov_immune_stroma_patchy
