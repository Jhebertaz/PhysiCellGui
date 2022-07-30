import os

from pyMCDS import pyMCDS
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.style.use('ipynb')

def plot_concentration_chemokine(scr, dest, figure_name):
    plt.style.use('ipynb')
    source = scr
    destination = dest
    mcds= pyMCDS('final.xml', source)
    mcds.get_substrate_names()

    chemokineval = mcds.get_concentrations('chemokine')

    X,Y = mcds.get_2D_mesh();

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


    plt.clf()
    ax = plt.subplot()
    im=plt.contourf(X,Y,chemokineval[:,:,0])

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)

    figure_path = os.path.join(destination,f"{figure_name}.png")
    plt.savefig(figure_path)
    # plt.show()