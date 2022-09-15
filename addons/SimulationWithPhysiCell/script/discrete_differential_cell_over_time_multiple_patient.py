#############
## Package ##
#############
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyqtgraph.examples.colorMaps import cm



def discrete_differential_cell_over_time_multiple_patient(sorted_data_source_folder_list,
                                                            data_destination_folder,
                                                            sorted_legend_name_list,
                                                            column=2,
                                                            figure_name="batch_cell_over_time",
                                                            saved=True):
    """
    :param sorted_data_source_folder_list: list of folders that contain Thsd_1500_p5X.dat file
    :param sorted_data_destination_folder_list:
    :param sorted_figure_name_list:
    :param column:
    :param saved:
    :return:
    """

    # Basic information
    source = None
    destination = data_destination_folder

    # Figure
    plt.style.use('ipynb')
    fig = plt.figure(figsize=(10, 4))

    # Colors
    colors = cm.rainbow(np.linspace(0, 1, len(sorted_data_source_folder_list)))

    for path, color in zip(sorted_data_source_folder_list, colors):

        # Basic information
        source = os.path.join(path, 'Thsd_1500_p5X.dat')

        # Data
        df = pd.read_csv(source, header=None)
        # time column
        time_ = df.iloc[:, 0]
        # cell column
        cell = df.iloc[:, column]
        # discrete differential
        dcdt = np.gradient(cell, time_[1])

        # Plotting
        plt.scatter(time_, dcdt, linewidth=1, color=color, marker='.', s=3)

    # Ticks
    plt.ticklabel_format(useOffset=False, style='plain', axis='y')
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    # Labels
    plt.xlabel("Temps (min)", fontsize=16)
    plt.ylabel("Taux de rétrécissement", fontsize=16)

    if saved:
        figure_path = os.path.join(destination, f"{figure_name}.png")
        plt.savefig(figure_path)
        plt.close()
        return figure_path

    else:
        plt.show()

if __name__ == "__main__":
    print(*sys.argv, sep='\n')
    discrete_differential_cell_over_time_multiple_patient(*sys.argv[1::])