import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
from numpy import diff
from scipy.misc import derivative
from pyMCDS import pyMCDS
import numpy as np
data_path = r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus"

directory_of_interest = []
for root, dirs, files in os.walk(data_path, topdown=False):

    for name in dirs:
        # print(os.path.join(root, name))
        directory_of_interest.append(name)

directory_of_interest.sort(key=lambda x: int(x.split('gbm-tmz-ov')[0]))


fig = plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 30))
data = []
legend = []
plt.style.use('ipynb')
for exp_name, color in zip(directory_of_interest,colors):
    real_path = os.path.join(root, exp_name)
    source = os.path.join(real_path,'Thsd_1500_p5X.dat')
    df = pd.read_csv(source, header=None)

    # cancer column
    time = df.iloc[:,0]
    cancer = df.iloc[:,2]

    derivative = diff(cancer)/diff(time)
    plt.plot(time, cancer, color=color)
    legend.append(f"{exp_name}")


plt.gca().set_aspect('equal')
plt.legend(legend,edgecolor="black", bbox_to_anchor=(1.04,0.5), loc='center left', borderaxespad=0)
plt.show()

# fig = plt.figure()
# colors = cm.rainbow(np.linspace(0, 1, 30))
# data = []
# legend = []
# plt.style.use('ipynb')
# for exp_name, color in zip(directory_of_interest,colors):
#     real_path = os.path.join(root, exp_name)
#     source = os.path.join(real_path,'Thsd_1500_p5X.dat')
#     df = pd.read_csv(source, header=None)
#
#     # cancer column
#     time = df.iloc[:-2,0]
#     cancer = df.iloc[:,2]
#
#     dxdx = list(map(lambda item: (item[1]-item[0])/30, zip(cancer[:-2:],cancer[1:-1:])))
#     print(dxdx)
#     plt.plot(np.array(dxdx), color=color)
#     legend.append(f"{exp_name}")
#
# plt.gca().set_aspect('equal')
# plt.legend(legend,edgecolor="black", bbox_to_anchor=(1.04,0.5), loc='center left', borderaxespad=0)
# plt.show()

# get cell data over time
# def cells_over_time(path):
#     counter_end = 144
#     source = path
#     data = [] # (time, th, gbm, ctl, stromal)
#     for n in range(0, counter_end + 1):
#         filename = 'output' + "%08i" % n + '.xml'
#
#         mcds = pyMCDS(filename, source)
#         time = mcds.get_time()
#
#         cx = mcds.data['discrete_cells']['position_x']
#         cy = mcds.data['discrete_cells']['position_y']
#
#
#         cell_type = mcds.data['discrete_cells']['cell_type']
#         cell_type = cell_type.astype(int)
#
#         cycle = mcds.data['discrete_cells']['cycle_model']
#         cycle = cycle.astype(int)
#
#         val = np.argwhere((cell_type == 1) & (cycle < 100)).flatten()
#         TH_val = len(cx[val])
#
#         val = np.argwhere((cell_type == 2) & (cycle < 100)).flatten()
#         cancer_val = len(cx[val])
#
#         val = np.argwhere((cell_type == 3) & (cycle < 100)).flatten()
#         CTL_val = len(cx[val])
#
#         val = np.argwhere((cell_type == 4) & (cycle < 100)).flatten()
#         stroma_val = len(cx[val])
#
#     data.append((time,TH_val,cancer_val,CTL_val,stroma_val))
#     return data
# cells_over_time(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus\1gbm-tmz-ov_2022-08-11T13_26_18")
# # macrophage_val = np.zeros( last_index+1 )
# # neutrophil_val = np.zeros( last_index+1 )
#
# for n in range(0, counter_end + 1):
#     filename = 'output' + "%08i" % n + '.xml'
#
#     mcds = pyMCDS(filename, source)  # 'output')
#     times[n] = mcds.get_time()
#
#     cx = mcds.data['discrete_cells']['position_x']
#     cy = mcds.data['discrete_cells']['position_y']
#
#     cell_type = mcds.data['discrete_cells']['cell_type']
#     cell_type = cell_type.astype(int)
#
#     cycle = mcds.data['discrete_cells']['cycle_model']
#     cycle = cycle.astype(int)
#
#     val = np.argwhere((cell_type == 1) & (cycle < 100)).flatten()
#     TH_val[n] = len(cx[val])
#
#     val = np.argwhere((cell_type == 2) & (cycle < 100)).flatten()
#     cancer_val[n] = len(cx[val])
#
#     val = np.argwhere((cell_type == 3) & (cycle < 100)).flatten()
#     CTL_val[n] = len(cx[val])
#
#     val = np.argwhere((cell_type == 4) & (cycle < 100)).flatten()
#     stroma_val[n] = len(cx[val])
#
#     # val=np.argwhere((cell_type==5) & (cycle < 100)).flatten()
#     # macrophage_val[n] = len(cx[val])
#
#     # val=np.argwhere((cell_type==6) & (cycle < 100)).flatten()
#     # neutrophil_val[n] = len(cx[val])
#
#     # data_list=[]
#     writer.writerow([times[n], TH_val[n], cancer_val[n], CTL_val[n], stroma_val[n]])  # ,macrophage_val[n]])
#
# # print(cancer_val[last_index])
# fi.close()
# fig = plt.figure()
# plt.clf()
# plt.plot(times, cancer_val, '-o', color='purple')
# plt.plot(times, TH_val, 'r-o')
# plt.plot(times, CTL_val, 'b-o')
# plt.plot(times, stroma_val, '-o', color='pink')
#
# arguments = [times, cancer_val, '-o', 'purple', times, TH_val, 'r-o', times, CTL_val, 'b-o', times, stroma_val, '-o',
#              'pink']
# # plt.plot( times, macrophage_val, 'g-o' )
# # plt.plot( times, neutrophil_val, '-o', color='orange' )
#
# # export path
# figure_path = os.path.join(destination, f"{figure_name}.png")
# plt.savefig(figure_path)
# # plt.show()
#
# # plt.clf()
# # plt.plot( cx[val], cy[val], 'ro' )
# # plt.show()
#
# return figure_path, fig, arguments