import os

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from extra_function import Config

# information
def get_name_sorted(path, key):
    directory_of_interest = []
    for root, dirs, files in os.walk(path, topdown=False):

        for name in dirs:
            # print(os.path.join(root, name))
            directory_of_interest.append(name)

    directory_of_interest.sort(key=lambda x: int(x.split(key)[0]))
    return root, directory_of_interest
def basic_information_cell_time(path, key):
    root, directory_of_interest = get_name_sorted(path, key)
    table = {}

    for exp_name in directory_of_interest:

        # retrieving path
        real_path = os.path.join(root, exp_name)

        # reading data
        source = os.path.join(real_path, 'Thsd_1500_p5X.dat')

        # convert to datafram
        df = pd.read_csv(source, header=None)

        # time
        time_= df.iloc[:,0].tolist()

        # th cells number columns
        th = df.iloc[:, 1].tolist()

        # cancer cells number column
        cancer = df.iloc[:, 2].tolist()

        # ctl cells number column
        ctl = df.iloc[:, 3].tolist()

        # stromal
        stromal = df.iloc[:, 4].tolist()

        # Retrieving csv file name from xml file
        configuration = Config.xml2dict(os.path.join(real_path, 'PhysiCell_settings.xml'))
        arguments = ['PhysiCell_settings', 'initial_conditions', 'cell_positions', 'filename']
        patient_name = Config.get2dict(*arguments, dictionary=configuration).replace('.csv', '')

        arguments = ['PhysiCell_settings', 'user_parameters','xhi','#text']
        cell_density = float(Config.get2dict(*arguments, dictionary=configuration))



        table[patient_name] = {'name':patient_name,'time':time_,'th':th, 'cancer':cancer, 'ctl':ctl, 'stromal':stromal,'cell_density':cell_density}
    return table

# figure
def batch_cell_over_time(path, key):

    # Figure
    plt.style.use('ipynb')
    fig = plt.figure(figsize=(10,5))

    # Colors
    root, directory_of_interest = get_name_sorted(path, key)
    # print(*directory_of_interest, sep='\n')
    colors = cm.rainbow(np.linspace(0, 1, len(directory_of_interest)))

    legend = []

    for exp_name, color in zip(directory_of_interest, colors):
        real_path = os.path.join(root, exp_name)
        source = os.path.join(real_path, 'Thsd_1500_p5X.dat')
        df = pd.read_csv(source, header=None)

        # cancer column
        time_ = df.iloc[:, 0]
        cancer = df.iloc[:, 2]

        # Plotting
        plt.scatter(time_, cancer,linewidth=2, color=color,  marker='.',s=8)#, markersize=5)

        # Labels
        plt.xlabel("Temps (min)",fontsize=16)
        plt.ylabel("Nombre de cellules cancéreuses",fontsize=16)

        # Ticks
        plt.ticklabel_format(useOffset=False, style='plain', axis='y')
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        legend.append(f"{exp_name}")

    plt.savefig(os.path.join(path,'batch_cell_over_time.pdf'))
    plt.close()
def batch_discrete_differential(path, key):

    # Figure
    plt.style.use('ipynb')
    fig = plt.figure(figsize=(10,4))

    # Colors
    root, directory_of_interest = get_name_sorted(path, key)

    colors = cm.rainbow(np.linspace(0, 1, len(directory_of_interest)))

    legend = []
    for exp_name, color in zip(directory_of_interest,colors):
        real_path = os.path.join(root, exp_name)
        source = os.path.join(real_path,'Thsd_1500_p5X.dat')
        df = pd.read_csv(source, header=None)

        # cancer column
        time = df.iloc[:,0]
        cancer = np.array(df.iloc[:,2].tolist(),dtype=float)

        # data
        dcdt = np.gradient(cancer, time[0])

        # Plotting
        plt.scatter(time, dcdt, linewidth=1,color=color, marker='.', s=3)

        # Ticks
        plt.ticklabel_format(useOffset=False, style='plain', axis='y')
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        # Labels
        plt.xlabel("Temps (min)",fontsize=16)
        plt.ylabel("Taux de rétrécissement",fontsize=16)

        legend.append(f"{exp_name}")

    plt.savefig(os.path.join(path,'batch_discrete_differential.pdf'))
def factor_vs_cancer_growth(path, key, combined=True):
    # Search information
    basic_information = basic_information_cell_time(path, key)
    data = []
    for patient_name, patient_data in basic_information.items():

        total_initial = sum([patient_data['cancer'][0],patient_data['ctl'][0],patient_data['th'][0],patient_data['stromal'][0]])
        cancer_growth =100*(patient_data['cancer'][-1] - patient_data['cancer'][0])/patient_data['cancer'][0]

        th_initial_proportion = 100*patient_data['th'][0]/total_initial
        cancer_initial_proportion = 100*patient_data['cancer'][0]/total_initial
        ctl_initial_proportion = 100*patient_data['ctl'][0]/total_initial
        stromal_initial_proportion =100* patient_data['stromal'][0]/total_initial
        immune_cell_initial_proportion = th_initial_proportion+ctl_initial_proportion
        cell_density = patient_data['cell_density']

        data.append((immune_cell_initial_proportion,th_initial_proportion,cancer_initial_proportion,ctl_initial_proportion,stromal_initial_proportion,cell_density,cancer_growth))

    df = pd.DataFrame(data, columns=['immune_cell_initial_proportion','th_initial_proportion','cancer_initial_proportion','ctl_initial_proportion','stromal_initial_proportion','cell_density','cancer_growth'])

    if not combined:
        return df


    # Figure
    plt.style.use('ipynb')
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8.5, 11))
    subplots = (ax1, ax2, ax3, ax4)

    # In general
    plt.ticklabel_format(useOffset=False,style='plain', axis='y')
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    # fig.suptitle('Horizontally stacked subplots')

    # Sorting value
    df1 = df.sort_values(by=['immune_cell_initial_proportion'], ascending=False)
    df2 = df.sort_values(by=['cancer_initial_proportion'], ascending=False)
    df3 = df.sort_values(by=['stromal_initial_proportion'], ascending=False)
    df4 = df.sort_values(by=['cell_density'], ascending=False)

    # Plotting
    ax1.scatter(df1['immune_cell_initial_proportion'],df1['cancer_growth'],s=8)
    ax2.scatter(df2['cancer_initial_proportion'],df2['cancer_growth'],s=8)
    ax3.scatter(df3['stromal_initial_proportion'], df3['cancer_growth'],s=8)
    ax4.scatter(df4['cell_density'], df4['cancer_growth'],s=8)

    # x Labels
    ax1.set_xlabel('Proportion initiale de cellules immunitaires', fontsize=12)
    ax2.set_xlabel('Proportion initiale de cellules cancéreuses', fontsize=12)
    ax3.set_xlabel('Proportion initiale de cellules stromales', fontsize=12)
    ax4.set_xlabel('Densité initiale de cellules', fontsize=12)

    # x ticks
    ax1.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax3.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax4.ticklabel_format(useOffset=False, style='plain', axis='x')

    # y ticks
    ax1.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
    ax2.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
    ax3.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
    ax4.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.

    ax1.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax3.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax4.ticklabel_format(useOffset=False, style='plain', axis='y')

    # grid
    ax1.grid(True, axis='y')
    ax2.grid(True, axis='y')
    ax3.grid(True, axis='y')
    ax4.grid(True, axis='y')

    # y label
    fig.text(0.02, 0.5, f"Pourcentage de croissance du cancer après traitement ({key.strip('gbm-')})", va='center', rotation='vertical',fontsize=15)

    # x label
    fig.text(0.4, -0.02, 'Facteurs initiaux', va='center', rotation='horizontal', fontsize=15)


    fig.tight_layout()
    plt.subplots_adjust(left=0.12525,
                        bottom=0.05,
                        hspace=0.3)

    # plt.show()
    plt.savefig(os.path.join(path,'factor_vs_cancer_growth.pdf'))
    plt.close()
def selected_factor_vs_cancer_growth(path, key,factor='immune_cell_initial_proportion'):
    # Data
    df = factor_vs_cancer_growth(path, key, combined=False)

    # Sorting value
    df1 = df.sort_values(by=[f'{factor}'], ascending=False)

    # Figure
    plt.style.use('ipynb')
    fig1 = plt.figure(figsize=(10, 5))

    # In general
    plt.ticklabel_format(useOffset=False,style='plain', axis='y')
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')


    # Plotting
    plt.scatter(df1[factor], df1['cancer_growth'],marker='.',s=8)

    title = {'immune_cell_initial_proportion': 'Proportion initiale de cellules immunitaires',
     'cancer_initial_proportion': 'Proportion initiale de cellules cancéreuses',
     'stromal_initial_proportion': 'Proportion initiale de cellules stromales',
     'cell_density': 'Densité initiale de cellules'}

    # x label
    plt.xlabel(title[factor], fontsize=15,labelpad=10)

    # x ticks
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    # y ticks
    plt.yticks(np.arange(-30, 60, step=10))  # Set label locations.
    plt.ticklabel_format(useOffset=False, style='plain', axis='y')

    # grid
    plt.grid(True, axis='y')

    # y label
    plt.ylabel(f"Pourcentage de croissance du cancer\n après traitement ({key.strip('gbm-')})", va='center', rotation='vertical',fontsize=15,labelpad=20)

    plt.savefig(os.path.join(path, f'{factor}_vs_cancer_growth.pdf'))
    plt.close()
def factor_vs_cancer_growth_combined(paths, keys, combined=True):
    if combined:
        # Figure
        plt.style.use('ipynb')
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8.5, 11))
        # In general
        plt.ticklabel_format(useOffset=False, style='plain', axis='y')
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    # Colors
    colors = plt.cm.RdYlGn(np.linspace(0.3, 1, len(keys)))
    colors = colors[::-1]

    # Marker
    markers = ["D","^","H" ]


    data={}

    for path, key, color, marker in zip(paths, keys,colors, markers):
        data[key] = factor_vs_cancer_growth(path, key, False)

        # Sorting value
        data['df1'] = data[key].sort_values(by=['immune_cell_initial_proportion'], ascending=False)
        data['df2'] = data[key].sort_values(by=['cancer_initial_proportion'], ascending=False)
        data['df3'] = data[key].sort_values(by=['stromal_initial_proportion'], ascending=False)
        data['df4'] = data[key].sort_values(by=['cell_density'], ascending=False)

        if combined:
            # Plotting
            ax1.scatter(data['df1']['immune_cell_initial_proportion'], data['df1']['cancer_growth'], label=key.strip('gbm-'), color=color,marker=marker,s=8)
            ax2.scatter(data['df2']['cancer_initial_proportion'], data['df2']['cancer_growth'],label=key.strip('gbm-'), color=color,marker=marker,s=8)
            ax3.scatter(data['df3']['stromal_initial_proportion'], data['df3']['cancer_growth'],label=key.strip('gbm-'), color=color,marker=marker,s=8)
            ax4.scatter(data['df4']['cell_density'], data['df4']['cancer_growth'],label=key.strip('gbm-'), color=color,marker=marker,s=8)

        del data['df1']
        del data['df2']
        del data['df3']
        del data['df4']

    if not combined:
        return data


    # x Labels
    ax1.set_xlabel('(a) Proportion initiale de cellules immunitaires', fontsize=12)
    ax2.set_xlabel('(b) Proportion initiale de cellules cancéreuses', fontsize=12)
    ax3.set_xlabel('(c) Proportion initiale de cellules stromales', fontsize=12)
    ax4.set_xlabel('(d) Densité initiale de cellules', fontsize=12)

    # x ticks
    ax1.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax3.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax4.ticklabel_format(useOffset=False, style='plain', axis='x')

    # y ticks
    ax1.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
    ax2.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
    ax3.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
    ax4.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.

    ax1.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax3.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax4.ticklabel_format(useOffset=False, style='plain', axis='y')

    # grid
    ax1.grid(True,axis='y')
    ax2.grid(True,axis='y')
    ax3.grid(True,axis='y')
    ax4.grid(True,axis='y')

    # Legend
    legend_item_plot = list(map(lambda x: x.strip('gbm-'), keys))
    plt.legend(legend_item_plot,fancybox=True, shadow=True, ncol=3,loc='lower center', bbox_to_anchor=(0.4, -.4255))

    # y label
    fig.text(0.02, 0.5, 'Pourcentage de croissance du cancer après traitement', va='center', rotation='vertical', fontsize=15)

    # x label
    fig.text(0.4, -0.03, 'Facteurs initiaux', va='center', rotation='horizontal', fontsize=15)

    fig.tight_layout()
    plt.subplots_adjust(left=0.12525,
                        bottom=0.05,
                        hspace=0.3)
    # plt.show()
    plt.savefig(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1", 'factor_vs_cancer_growth_combined.pdf'))
    plt.close()
def selected_factor_vs_cancer_growth_combined(paths, keys, factor='immune_cell_initial_proportion'):
    # Figure
    plt.style.use('ipynb')
    fig1 = plt.figure(figsize=(10, 5))

    # In general
    plt.ticklabel_format(useOffset=False, style='plain', axis='y')
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    # Colors
    colors = plt.cm.RdYlGn(np.linspace(0.3, 1, len(keys)))
    colors = colors[::-1]

    # Marker
    markers = ["D", "^", "H"]

    title = {'immune_cell_initial_proportion': 'Proportion initiale de cellules immunitaires',
     'cancer_initial_proportion': 'Proportion initiale de cellules cancéreuses',
     'stromal_initial_proportion': 'Proportion initiale de cellules stromales',
     'cell_density': 'Densité initiale de cellules'}

    # Data
    data = factor_vs_cancer_growth_combined(paths, keys, combined=False)


    # Plotting
    for key, color,marker in zip(data.keys(), colors, markers):
        data[key] = data[key].sort_values(by=[f'{factor}'], ascending=False)

        plt.scatter(data[key][factor], data[key]['cancer_growth'],label=key.strip('gbm-'), color=color, marker=marker,s=8)

    # x label
    plt.xlabel(title[factor], fontsize=15, labelpad=30)

    # x ticks
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    # y ticks
    plt.yticks(np.arange(-30, 60, step=10))  # Set label locations.
    plt.ticklabel_format(useOffset=False, style='plain', axis='y')

    # grid
    plt.grid(True, axis='y')

    # y label
    plt.ylabel(f"Pourcentage de croissance du cancer \n après traitement", va='center', rotation='vertical', fontsize=15, labelpad=20)

    # Legend
    legend_item_plot = list(map(lambda x: x.strip('gbm-'), keys))
    plt.legend(legend_item_plot,fancybox=True, shadow=True, ncol=3, loc='lower center', bbox_to_anchor=(0.5, -.2))

    plt.savefig(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1", f'{factor}_vs_cancer_growth_combined.pdf'))
    plt.close()
def reduction_comparison(paths, keys):

    # For plot 1
    data_ = table_reduction_combined(paths, keys)
    root, directory_of_interest = get_name_sorted(paths[0], keys[0])

    subdata = data_.iloc[:len(directory_of_interest):, :]
    # Label name
    columns = subdata['Patient'].values.tolist()
    subdata.set_index('Patient')

    # Value
    rows = subdata.columns.values.tolist()[1::]

    # For plot 2
    # retrieve cell count for each patient
    info = basic_information_cell_time(paths[0], keys[0])
    tmp_dict = []
    cancer = []
    i=0
    for key, value in info.items():

        if i==0:
            cancer.append(int(value['cancer'][0]))
        total = sum([value['th'][0], value['cancer'][0], value['ctl'][0], value['stromal'][0]])
        tmp_dict.append((key, value['cancer'][0] / total, value['th'][0] / total, value['ctl'][0] / total, value['stromal'][0] / total))

    tmp_df = pd.DataFrame.from_records(tmp_dict, columns=['Patient', 'cancer', 'th', 'ctl', 'stromal'])

    # Colors
    colors = plt.cm.RdYlGn(np.linspace(0.3, 1, len(rows)))
    colors = colors[::-1]

    # Figure
    # plt.style.use('ipynb')
    fig, axes = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 4]},figsize=(10, 12))

    # x ticks
    plt.ticklabel_format(useOffset=False, style='plain', axis='x')

    # Plotting
    plot2 = tmp_df.plot.barh(stacked=True, ax=axes[0],width=0.75,)
    plot1 = subdata.plot.barh(stacked=False, color={k: c for k, c in zip(rows, colors)}, ax=axes[1], width=0.75)

    # y ticks
    plot2.set_yticklabels(columns, fontsize=12.5)
    # plot2.set_yticklabels()

    plot1.yaxis.tick_right()
    plot1.set_yticklabels(cancer)

    # x ticks
    # plot2.set_xticklabels([])
    # plot2.set_xticks([])

    # x labels
    plot1.set_xlabel("Pourcentage de croissance du cancer \n après traitement", fontsize=14)
    plot2.set_xlabel("Proportion initiale", fontsize=14)

    # y labels
    plot2.set_ylabel("Patient", fontsize=15,labelpad=10)
    plot1.yaxis.set_label_position("right")
    plot1.set_ylabel("Nombre initiale de cellules cancéreuses", fontsize=15, labelpad=15)

    # Legend for plot 1
    legend_item_plot_1 = list(map(lambda x: x.strip('gbm-'), rows))
    legend_item_plot_2 = ['Cancéreuse', 'TH', 'CTL', 'Stromale']

    # legends
    plot1.legend(legend_item_plot_1, prop={'size': 12.5}, fancybox=True, shadow=True, loc='upper right' ) #bbox_to_anchor=(1.5, 1)
    plot2.legend(legend_item_plot_2, prop={'size': 12.5}, ncol=1, loc='upper right', fancybox=True, shadow=True, bbox_to_anchor=(5, 0.9))
    plot2.set_zorder(1)


    # Additionnal (not in legend)
    plot1.axvline(0, color='black', linewidth=0.2)  # Vertical bar


    # for i, v in zip(range(len(yy)),yy):
    #     plot2.text(1.1, i-0.2, f"{v[0]}% ; {v[1]}%", color='black')

    fig.tight_layout()
    plt.subplots_adjust(left=0.23, bottom=0.0725, wspace=0)
    plt.savefig(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1", 'reduction_comparison.pdf'))
    plt.close()
def factor_vs_factor(path, key, combined=True):
    # Search information
    basic_information = basic_information_cell_time(path, key)
    data = []
    for patient_name, patient_data in basic_information.items():
        total_initial = sum(
            [patient_data['cancer'][0], patient_data['ctl'][0], patient_data['th'][0], patient_data['stromal'][0]])
        cancer_growth = 100 * (patient_data['cancer'][-1] - patient_data['cancer'][0]) / patient_data['cancer'][0]
        initial_cancer = patient_data['cancer'][0]
        th_initial_proportion = 100 * patient_data['th'][0] / total_initial
        cancer_initial_proportion = 100 * patient_data['cancer'][0] / total_initial
        ctl_initial_proportion = 100 * patient_data['ctl'][0] / total_initial
        stromal_initial_proportion = 100 * patient_data['stromal'][0] / total_initial
        immune_cell_initial_proportion = th_initial_proportion + ctl_initial_proportion
        cell_density = patient_data['cell_density']

        data.append((immune_cell_initial_proportion, th_initial_proportion, cancer_initial_proportion,
                     ctl_initial_proportion, stromal_initial_proportion, cell_density, cancer_growth,initial_cancer))

    df = pd.DataFrame(data,
                      columns=['immune_cell_initial_proportion', 'th_initial_proportion', 'cancer_initial_proportion',
                               'ctl_initial_proportion', 'stromal_initial_proportion', 'cell_density', 'cancer_growth','initial_cancer'])



    if not combined:
        return df

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    df4 = df.sort_values(by=['initial_cancer'], ascending=False)
    lenght=len(basic_information)
    colors = cm.rainbow(np.linspace(0, 1, len(basic_information)))
    # for zz,cc in zip(df4['cancer_growth'].tolist(),colors):
    #
    #     # Plot the bar graph given by xs and ys on the plane y=k with 80% opacity.
    #     ax.bar(df4['cell_density'], df4['cancer_initial_proportion'], zs=zz, zdir='y', color=cc, alpha=0.8)

    ax.bar3d(x=df4['initial_cancer'].tolist(),
             y=df4['cell_density'].tolist(),
             z=np.zeros(lenght),
             dz=np.zeros(lenght)*0.001,
             dx=np.ones(lenght)*0.0005,
             dy=np.ones(lenght)*0.0005, color=colors,alpha=0.8)


    ax.set_xlabel('cancer_initial')
    ax.set_ylabel('cell_density')
    ax.set_zlabel('cancer_growth')
    # ax.set_xticks(df4['cell_density'].tolist())
    # ax.set_yticks(df4['cancer_initial_proportion'].tolist())
    # ax.set_zticks(df4['cancer_growth'].tolist())
    # plt.show()
    plt.savefig(os.path.join(path, 'factor_vs_factor.pdf'))
    plt.close()



    if False:
        # Figure
        plt.style.use('ipynb')
        fig, (ax1, ax3, ax4) = plt.subplots(3, 1, figsize=(8.5, 11))
        subplots = (ax1, ax3, ax4)

        # In general
        plt.ticklabel_format(useOffset=False, style='plain', axis='y')
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')

        # fig.suptitle('Horizontally stacked subplots')

        # Sorting value
        df1 = df.sort_values(by=['immune_cell_initial_proportion'], ascending=False)
        # df2 = df.sort_values(by=['cancer_initial_proportion'], ascending=False)
        df3 = df.sort_values(by=['stromal_initial_proportion'], ascending=False)
        df4 = df.sort_values(by=['cell_density'], ascending=False)

        # Plotting
        ax1.scatter(df1['immune_cell_initial_proportion'], df1['cancer_initial_proportion'], s=8)
        # ax2.scatter(df2['cancer_initial_proportion'], df2['cancer_initial_proportion'], s=8)
        ax3.scatter(df3['stromal_initial_proportion'], df3['cancer_initial_proportion'], s=8)
        ax4.scatter(df4['cell_density'], df4['cancer_initial_proportion'], s=8)

        # x Labels
        ax1.set_xlabel('Proportion initiale de cellules immunitaires', fontsize=12)
        # ax2.set_xlabel('Proportion initiale de cellules cancéreuses', fontsize=12)
        ax3.set_xlabel('Proportion initiale de cellules stromales', fontsize=12)
        ax4.set_xlabel('Densité initiale de cellules', fontsize=12)

        # x ticks
        ax1.ticklabel_format(useOffset=False, style='plain', axis='x')
        # ax2.ticklabel_format(useOffset=False, style='plain', axis='x')
        ax3.ticklabel_format(useOffset=False, style='plain', axis='x')
        ax4.ticklabel_format(useOffset=False, style='plain', axis='x')

        # y ticks
        ax1.set_yticks(np.arange(0, 100, step=10))  # Set label locations.
        # ax2.set_yticks(np.arange(-30, 60, step=10))  # Set label locations.
        ax3.set_yticks(np.arange(0, 100, step=10))  # Set label locations.
        ax4.set_yticks(np.arange(0, 100, step=10))  # Set label locations.

        ax1.ticklabel_format(useOffset=False, style='plain', axis='y')
        # ax2.ticklabel_format(useOffset=False, style='plain', axis='y')
        ax3.ticklabel_format(useOffset=False, style='plain', axis='y')
        ax4.ticklabel_format(useOffset=False, style='plain', axis='y')

        # grid
        ax1.grid(True, axis='y')
        # ax2.grid(True, axis='y')
        ax3.grid(True, axis='y')
        ax4.grid(True, axis='y')

        # y label
        fig.text(0.02, 0.5, f"Proportion initiales de cellules cancéreuses", va='center',
                 rotation='vertical', fontsize=15)

        # x label
        fig.text(0.4, -0.02, 'Facteurs initiaux', va='center', rotation='horizontal', fontsize=15)

        fig.tight_layout()
        plt.subplots_adjust(left=0.12525,
                            bottom=0.05,
                            hspace=0.3)

        # plt.show()
        plt.savefig(os.path.join(path, 'factor_vs_factor.pdf'))
        plt.close()

# table
def table_reduction_percentage(path,key):
    root, directory_of_interest = get_name_sorted(path, key)
    table = []

    for exp_name in directory_of_interest:
        # retrieving path
        real_path = os.path.join(root, exp_name)

        # reading data
        source = os.path.join(real_path,'Thsd_1500_p5X.dat')

        # convert to datafram
        df = pd.read_csv(source, header=None)

        # th cells number columns
        th = df.iloc[:,1].tolist()

        # cancer cells number column
        cancer = df.iloc[:, 2].tolist()

        # ctl cells number column
        ctl = df.iloc[:,3].tolist()

        # stromal
        stromal = df.iloc[:,4].tolist()


        # Calculate reduction
        begin_, end_ = cancer[0], cancer[-1]
        reduction_percent = round(((end_-begin_)/begin_)*100,2)


        # Retrieving cell density from xml file
        configuration = Config.xml2dict(os.path.join(real_path,'PhysiCell_settings.xml'))
        arguments = ['PhysiCell_settings', 'user_parameters','xhi','#text']
        cell_density = float(Config.get2dict(*arguments, dictionary=configuration))

        # Retrieving csv file name from xml file
        arguments = ['PhysiCell_settings','initial_conditions','cell_positions','filename']
        patient_name = Config.get2dict(*arguments, dictionary=configuration).replace('.csv','')
        table.append((patient_name, begin_, end_, reduction_percent, cell_density))

    # Changing original column name
    df = pd.DataFrame.from_records(table, columns =['Patient', 'Initial', 'Final', 'Croissance', 'Densité initiale'])
    df = df.round({'Croissance': 2})
    # Some interesting values
    tmp = df.describe()
    tmp = tmp.round({'Croissance': 2})

    tmp.insert(0,'Patient', ['count','mean','std', 'min', '25%','50%','75%','max'])
    # tmp.assign(Patient=['count','mean','std', 'min', '25%','50%','75%','max'])

    # Concatenate original table for converting in latex
    tmp2 = pd.concat([df, tmp], ignore_index=True, sort=False)
    tmp2['Initial'] = tmp2['Initial'].round()
    tmp2['Final'] = tmp2['Final'].round()

    tmp2['Initial'] = tmp2['Initial'].astype(int)
    tmp2['Final'] = tmp2['Final'].astype(int)

    # tmp2['Initial'] = tmp2['Initial'].apply(np.ceil)
    # tmp2['Final'] = tmp2['Final'].apply(np.ceil)

    tmp2['Croissance'] = tmp2['Croissance'].round(decimals=3)
    tmp2['Densité initiale'] = tmp2['Densité initiale'].round(decimals=5)

    # Writing it to a tex file
    with open(os.path.join(path,'table.tex'),'w') as file:
        file.write(tmp2.to_latex(index=False))

    return tmp2
def table_reduction_combined(paths, keys):
    dataframe_dict = {key:None for key in keys}
    for path, key in zip(paths,keys):
        dataframe_dict[key] = table_reduction_percentage(path, key)
        dataframe_dict[key].rename(columns={'Croissance': key.strip('gbm-')}, inplace=True)
        dataframe_dict[key] = dataframe_dict[key].round({key.strip('gbm-'): 2})

    tmp = pd.concat([dataframe_dict[keys[0]]['Patient']]+[dataframe_dict[key][key.strip('gbm-')] for key in keys], ignore_index=False, sort=False, axis=1)
    with open(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1",'table.tex'),'w') as file:
        file.write(tmp.to_latex(index=False))

    return tmp


paths = [
    r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1\tmz",
    r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1\ov",
    r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1\tmz_virus"
]

title = {'immune_cell_initial_proportion': 'Proportion initiale de cellules immunitaires',
         'cancer_initial_proportion': 'Proportion initiale de cellules cancéreuses',
         'stromal_initial_proportion': 'Proportion initiale de cellules stromales',
         'cell_density': 'Densité initiale de cellules'}
keys = ['gbm-tmz', 'gbm-ov','gbm-tmz-ov']

factor_vs_factor(paths[1],keys[1])
# paths=[r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus"]
# keys=['gbm-tmz-ov']
# Global

# Figure
# table_reduction_combined(paths, keys)
# for tt in title.keys():
#     selected_factor_vs_cancer_growth_combined(paths, keys, tt)
#
# # Table
# reduction_comparison(paths, keys)
# factor_vs_cancer_growth_combined(paths,keys)
#
# # Individual
# for path,key in zip(paths,keys):
#     #Table
#     table_reduction_percentage(path, key)
#     #
#     # # Figure
#     batch_cell_over_time(path, key)
#     batch_discrete_differential(path, key)
#     factor_vs_cancer_growth(path, key)
#     for tt in title.keys():
#         selected_factor_vs_cancer_growth(path, key, tt)








from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from pdf2image import convert_from_path
def svg_to_pdf(path):
    i=0
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            if '.svg' in file:
                print(os.path.join(root,file))
                if (not file in ['final.svg','initial.svg','legend.svg']):


                    drawing = svg2rlg(os.path.join(root,file))
                    # renderPDF.drawToFile(drawing, f"{file.split('.svg')[0]}.pdf")
                    renderPDF.drawToFile(drawing, f"snapshot_{i}.pdf")

                    # pages = convert_from_path(f"{file.split('.svg')[0]}.pdf",150)
                    # for page in pages:
                    #     page.save(f"{file.split('.svg')[0]}.png", 'PNG')
                    i+=1

# svg_to_pdf(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\Save1\tmz_virus\29gbm-tmz-ov_2022-08-17T07_27_13")
