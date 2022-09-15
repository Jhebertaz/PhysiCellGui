#############
## Package ##
#############
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyqtgraph.examples.colorMaps import cm



def cell_over_time_one_patient(data_source_folder,
                               data_destination_folder,
                               figure_name,
                               column=2,
                               saved=True):
    """
    :param data_source_folder: path to folder that contain Thsd_1500_p5X.dat file
    :param data_destination_folder:
    :param figure_name:
    :param column:
    :param saved:
    :return:
    """

    # Basic information
    source = os.path.join(data_source_folder, 'Thsd_1500_p5X.dat')
    destination = data_destination_folder

    # Figure
    plt.style.use('ipynb')
    fig = plt.figure(figsize=(10,5))

    # Data
    df = pd.read_csv(source, header=None)
    # time column
    time_ = df.iloc[:, 0]
    # cell column
    cell = df.iloc[:, column]

    # Plotting
    plt.scatter(time_, cell, linewidth=2,  marker='.', s=8)

    # Labels
    plt.xlabel("Temps (min)", fontsize=16)
    plt.ylabel("Nombre de cellules cancéreuses",fontsize=16)

    # Ticks
    plt.ticklabel_format(useOffset=False, style='plain', axis='y')
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    if saved:
        figure_path = os.path.join(destination, f"{figure_name}.png")
        plt.savefig(figure_path)
        plt.close()
        return figure_path

    else:
        plt.show()

if __name__ == "__main__":
    print(*sys.argv, sep='\n')
    cell_over_time_one_patient(*sys.argv[1::])
