import csv
from pyMCDS import pyMCDS
import numpy as np
import matplotlib.pyplot as plt
import sys



def plot_time_cell_number(scr, dest, figure_name):
    plt.style.use('ipynb')
    source = scr
    destination = dest

    fi = open(f"{destination}\Thsd_1500_p5X.dat", "w")
    writer = csv.writer(fi)

    last_index = 144 # TODO automatic index last finder
    times = np.zeros(last_index + 1)
    TH_val = np.zeros(last_index + 1)
    cancer_val = np.zeros(last_index + 1)
    CTL_val = np.zeros(last_index + 1)
    stroma_val = np.zeros(last_index + 1)

    # macrophage_val = np.zeros( last_index+1 )
    # neutrophil_val = np.zeros( last_index+1 )

    for n in range( 0,last_index+1 ):
        filename='output'+"%08i"%n+'.xml'

        mcds=pyMCDS(filename, source)#'output')
        times[n]= mcds.get_time()

        cx = mcds.data['discrete_cells']['position_x']
        cy = mcds.data['discrete_cells']['position_y']

        cell_type=mcds.data['discrete_cells']['cell_type']
        cell_type=cell_type.astype(int)

        cycle = mcds.data['discrete_cells']['cycle_model']
        cycle = cycle.astype( int )

        val=np.argwhere((cell_type==1) & (cycle < 100)).flatten()
        TH_val[n] = len(cx[val])

        val=np.argwhere((cell_type==2) & (cycle < 100)).flatten()
        cancer_val[n] = len(cx[val])

        val=np.argwhere((cell_type==3) & (cycle < 100)).flatten()
        CTL_val[n] = len(cx[val])

        val=np.argwhere((cell_type==4) & (cycle < 100)).flatten()
        stroma_val[n] = len(cx[val])

        # val=np.argwhere((cell_type==5) & (cycle < 100)).flatten()
        # macrophage_val[n] = len(cx[val])

        #val=np.argwhere((cell_type==6) & (cycle < 100)).flatten()
        #neutrophil_val[n] = len(cx[val])

        # data_list=[]
        writer.writerow([times[n],TH_val[n],cancer_val[n],CTL_val[n],stroma_val[n]]) #,macrophage_val[n]])

    # print(cancer_val[last_index])
    fi.close()
    plt.clf()
    plt.plot( times, cancer_val, '-o', color='purple' )
    plt.plot( times, TH_val, 'r-o' )
    plt.plot( times, CTL_val, 'b-o' )
    plt.plot( times, stroma_val, '-o', color='pink')

    # plt.plot( times, macrophage_val, 'g-o' )
    #plt.plot( times, neutrophil_val, '-o', color='orange' )

    # export path
    figure_path = os.path.join(destination,f"{figure_name}.png")
    plt.savefig(figure_path)
    # plt.show()

    # plt.clf()
    # plt.plot( cx[val], cy[val], 'ro' )
    # plt.show()

    return figure_path

if __name__ == "__main__":
    print(sys.argv)
    plot_time_cell_number(sys.argv[1], sys.argv[2], sys.argv[3])