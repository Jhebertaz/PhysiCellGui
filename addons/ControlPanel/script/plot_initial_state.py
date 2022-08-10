import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm




script_path = os.path.realpath(__file__)
script_name = 'plot_initial_state'

# https://www.statology.org/pandas-select-rows-based-on-column-values/
# script_path = os.path.realpath(__file__)
def plot_initial_state(data_source_folder, data_destination_folder=None, figure_name=None, *args, **kwargs):
    # Data source must specify an csv file path with x,y,z,type as column
    source = data_source_folder
    destination = data_destination_folder

    # read csv
    df = pd.read_csv(source)
    freq = df.iloc[:, 3].value_counts().to_dict()

    if 'type_dict' in kwargs:
        # key:type_name, value : (point, frequency count)

        dt = {}
        for k, v in freq.items():
            sub = df.loc[df.iloc[:, 3] == k]
            dt[kwargs['type_dict'][int(k)]] = {'x': sub.iloc[:, 0], 'y': sub.iloc[:, 1], 'count': v}

    else:
        # key:type_number, value : (point, frequency count)
        dt = {}
        for k, v in freq.items():
            sub = df.loc[df.iloc[:,3] == k]
            dt[k] = {'x':sub.iloc[:,0],'y':sub.iloc[:,1],'count':v}

    # Create plot
    fig = plt.figure()
    colors = cm.rainbow(np.linspace(0, 1, len(dt)))
    legend = []
    for k,v,c in zip(dt.keys(), dt.values(), colors):
        plt.scatter(v['x'], v['y'], marker='.',s=20, color=c)
        legend.append(f"{k}\n {v['count']}")
        arguments = [v['x'], v['y'],'.',20, c]

    plt.gca().set_aspect('equal')
    plt.legend(legend,edgecolor="black", bbox_to_anchor=(1.04,0.5), loc='center left', borderaxespad=0)

    if destination and figure_name:
        figure_path = os.path.join(destination, f"{figure_name}.png")
        plt.savefig(figure_path)

    return figure_path


if __name__ == "__main__":
    print(*sys.argv, sep='\n')
    plot_initial_state(*sys.argv[1::])