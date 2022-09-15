#############
## Package ##
#############
import os
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Modified version of pyMCDS
from pyMCDS import pyMCDS

script_path = os.path.realpath(__file__)
script_name = 'plot_concentration_substrate'

def plot_concentration_substrate(data_source_folder, data_destination_folder, figure_name, moment, substrate, saved=True):
    # MatPlotLib plot style
    plt.style.use('ipynb')

    # Basic information
    source = data_source_folder
    destination = data_destination_folder

    # Get data from simulation for a specific snapshot moment output
    mcds = pyMCDS(moment, source)
    mcds.get_substrate_names()

    # Value
    substrateval = mcds.get_concentrations(substrate)

    # Position
    X,Y = mcds.get_2D_mesh()

    # Figure
    fig = plt.figure()
    ax = plt.subplot()
    im = plt.contourf(X,Y,substrateval[:,:,0])

    # Options
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)

    if saved:
        figure_path = os.path.join(destination, f"{figure_name}.png")
        plt.savefig(figure_path)
        plt.close()
        return figure_path

    else:
        plt.show()

if __name__ == "__main__":
    print(*sys.argv, sep='\n')
    plot_concentration_substrate(*sys.argv[1::])


