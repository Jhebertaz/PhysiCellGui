#############
## Package ##
#############
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm




script_path = os.path.realpath(__file__)
script_name = 'plot_initial_state'


def plot_initial_state(data_source_path, data_destination_folder=None, figure_name=None, cell_type_dictionary=None, saved=True):
    """
    :param data_source_path: Data source must specify an csv file path with x,y,z, type as column without header
    :param data_destination_folder:
    :param figure_name:
    :param cell_type_dictionary:
    :return:
    """

    # Basic information
    source = data_source_path
    destination = data_destination_folder

    # Data
    df = pd.read_csv(source, header=None)
    freq = df.iloc[:, 3].value_counts().to_dict()

    if cell_type_dictionary:
        # key:type_name, value : (point, frequency count)
        dt = {}
        for k, v in freq.items():
            sub = df.loc[df.iloc[:, 3] == k]
            dt[cell_type_dictionary[int(k)]] = {'x': sub.iloc[:, 0], 'y': sub.iloc[:, 1], 'count': v}

    else:
        # key:type_number, value : (point, frequency count)
        dt = {}
        for k, v in freq.items():
            sub = df.loc[df.iloc[:,3] == k]
            dt[k] = {'x':sub.iloc[:,0],'y':sub.iloc[:,1],'count':v}


    # Figure
    fig = plt.figure()

    # Colors
    colors = cm.rainbow(np.linspace(0, 1, len(dt)))
    legend = []
    for k, v, c in zip(dt.keys(), dt.values(), colors):
        plt.scatter(v['x'], v['y'], marker='.',s=20, color=c)
        legend.append(f"{k}\n {v['count']}")
        arguments = [v['x'], v['y'],'.',20, c]

    # Make it squared
    plt.gca().set_aspect('equal')

    # Set up legend
    plt.legend(legend, edgecolor="black", bbox_to_anchor=(1.04,0.5), loc='center left', borderaxespad=0)

    if saved:
        figure_path = os.path.join(destination, f"{figure_name}.png")
        plt.savefig(figure_path)
        return figure_path

    else:
        plt.show()
    
if __name__ == "__main__":
    print(*sys.argv, sep='\n')
    plot_initial_state(*sys.argv[1::])