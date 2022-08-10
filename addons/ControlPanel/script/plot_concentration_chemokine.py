import os
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pyMCDS import pyMCDS

script_path = os.path.realpath(__file__)
script_name = 'plot_concentration_chemokine'

def plot_concentration_chemokine(data_source_folder, data_destination_folder, figure_name, *args, **kwargs):
    plt.style.use('ipynb')
    source = data_source_folder
    destination = data_destination_folder
    mcds = pyMCDS('final.xml', source)
    mcds.get_substrate_names()

    chemokineval = mcds.get_concentrations('chemokine')
    X,Y = mcds.get_2D_mesh()

    #print(ICIval[2,149,0])

    # plt.clf()
    # plt.contourf(X,Y,tmzval[:,:,0]);
    # plt.show()

    # plt.clf()
    # plt.contourf(X,Y,wallval[:,:,0]);
    # plt.show()

    # plt.clf()
    # plt.contourf(X,Y,chemokineval[:,:,0]);
    # plt.show()

    # plt.clf()
    # plt.contourf(X,Y,ICIval[:,:,0]);
    # plt.show()

    fig = plt.figure()
    plt.clf()
    ax = plt.subplot()
    im = plt.contourf(X,Y,chemokineval[:,:,0])

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)

    figure_path = os.path.join(destination, f"{figure_name}.png")
    plt.savefig(figure_path)
    return figure_path, fig
    # plt.show()

if __name__ == "__main__":
    print(*sys.argv, sep='\n')
    plot_concentration_chemokine(*sys.argv[1::])


