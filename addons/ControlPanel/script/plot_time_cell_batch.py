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
def basic_information_cell_time(path,key):
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
    fig = plt.figure(figsize=(15,10))

    # Colors
    colors = cm.rainbow(np.linspace(0, 1, 30))

    legend = []
    root, directory_of_interest = get_name_sorted(path, key)
    for exp_name, color in zip(directory_of_interest, colors):
        real_path = os.path.join(root, exp_name)
        source = os.path.join(real_path, 'Thsd_1500_p5X.dat')
        df = pd.read_csv(source, header=None)

        # cancer column
        time_ = df.iloc[:, 0]
        cancer = df.iloc[:, 2]

        # Plotting
        plt.plot(time_, cancer,linewidth=2, color=color,  marker='.', markersize=5)

        # Labels
        plt.xlabel("Temps (min)")
        plt.ylabel("Nombre de cellules cancéreuses")

        # Ticks
        plt.ticklabel_format(useOffset=False, style='plain', axis='y')
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')
        legend.append(f"{exp_name}")

    plt.savefig(os.path.join(path,'batch_cell_over_time.pdf'))
def batch_discrete_differential(path, key):

    # Figure
    plt.style.use('ipynb')
    fig = plt.figure(figsize=(15,10))

    # Colors
    colors = cm.rainbow(np.linspace(0, 1, 30))

    legend = []
    root, directory_of_interest = get_name_sorted(path, key)
    for exp_name, color in zip(directory_of_interest,colors):
        real_path = os.path.join(root, exp_name)
        source = os.path.join(real_path,'Thsd_1500_p5X.dat')
        df = pd.read_csv(source, header=None)

        # cancer column
        time = df.iloc[:,0]
        cancer = np.array(df.iloc[:,2].tolist(),dtype=float)

        # data
        dcdt = np.gradient(cancer,30)

        # Plotting
        plt.plot(time, dcdt, linewidth=1,color=color, marker='.',  markersize=5)

        # Ticks
        plt.ticklabel_format(useOffset=False, style='plain', axis='y')
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')

        # Labels
        plt.xlabel("Temps (min)",fontsize=14)
        plt.ylabel("Taux de rétrécissement",fontsize=14)

        legend.append(f"{exp_name}")

    plt.savefig(os.path.join(path,'batch_discrete_differential.pdf'))
def factor_vs_cancer_growth(path, key, combined=False):
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
    if combined:
        return df
    # Figure
    plt.style.use('ipynb')
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8.5, 11))

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
    ax1.plot(df1['immune_cell_initial_proportion'],df1['cancer_growth'])
    ax2.plot(df2['cancer_initial_proportion'],df2['cancer_growth'])
    ax3.plot(df3['stromal_initial_proportion'], df3['cancer_growth'])
    ax4.plot(df4['cell_density'], df4['cancer_growth'])

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
    fig.text(0.02, 0.5, f"Pourcentage de croissance de la tumeur après traitement ({key.strip('gbm-')})", va='center', rotation='vertical',fontsize=15)
    # x label
    fig.text(0.4, -0.02, 'Facteurs initials', va='center', rotation='horizontal', fontsize=15)


    fig.tight_layout()
    plt.subplots_adjust(left=0.12525,
                        bottom=0.05,
                        hspace=0.3)

    # plt.show()
    plt.savefig(os.path.join(path,'factor_vs_cancer_growth.pdf'))


def factor_vs_cancer_growth_combined(paths, keys):
    # Figure
    plt.style.use('ipynb')
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8.5, 11))

    # Colors
    colors = plt.cm.RdYlGn(np.linspace(0.3, 1, len(keys)))
    colors = colors[::-1]

    # Marker
    markers = ["D","^","H" ]

    # In general
    plt.ticklabel_format(useOffset=False)
    plt.ticklabel_format(style='plain', axis='y')
    plt.ticklabel_format(style='plain', axis='x')
    data={}
    for path, key, color, marker in zip(paths, keys,colors, markers):
        data['df'] = factor_vs_cancer_growth(path, key,True)

        # Sorting value
        data['df1'] = data['df'].sort_values(by=['immune_cell_initial_proportion'], ascending=False)
        data['df2'] = data['df'].sort_values(by=['cancer_initial_proportion'], ascending=False)
        data['df3'] = data['df'].sort_values(by=['stromal_initial_proportion'], ascending=False)
        data['df4'] = data['df'].sort_values(by=['cell_density'], ascending=False)

        # Plotting
        ax1.plot(data['df1']['immune_cell_initial_proportion'], data['df1']['cancer_growth'], label=key.strip('gbm-'), color=color,marker=marker)
        ax2.plot(data['df2']['cancer_initial_proportion'], data['df2']['cancer_growth'], label=key.strip('gbm-'), color=color,marker=marker)
        ax3.plot(data['df3']['stromal_initial_proportion'], data['df3']['cancer_growth'],label=key.strip('gbm-'), color=color,marker=marker)
        ax4.plot(data['df4']['cell_density'], data['df4']['cancer_growth'],label=key.strip('gbm-'), color=color,marker=marker)

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
    ax1.grid(True,axis='y')
    ax2.grid(True,axis='y')
    ax3.grid(True,axis='y')
    ax4.grid(True,axis='y')

    # Legend
    legend_item_plot = list(map(lambda x: x.strip('gbm-'), keys))
    plt.legend(legend_item_plot,fancybox=True, shadow=True, ncol=3,loc='lower center', bbox_to_anchor=(0.4, -.4255))

    # y label
    fig.text(0.02, 0.5, 'Pourcentage de croissance de la tumeur après traitement', va='center', rotation='vertical', fontsize=15)

    # x label
    fig.text(0.4, -0.03, 'Facteurs initials', va='center', rotation='horizontal', fontsize=15)

    fig.tight_layout()
    plt.subplots_adjust(left=0.12525,
                        bottom=0.05,
                        hspace=0.3)
    # plt.show()
    plt.savefig(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result", 'factor_vs_cancer_growth_combined.pdf'))

def reduction_comparison(paths, keys):

    # For plot 1
    data_ = table_reduction_combined(paths, keys)
    subdata = data_.iloc[:30:, :]
    # Label name
    columns = subdata['Patient'].values.tolist()
    subdata.set_index('Patient')

    # Value
    rows = subdata.columns.values.tolist()[1::]

    # For plot 2
    # retrieve cell count for each patient
    info = basic_information_cell_time(paths[0], keys[0])
    tmp_dict = []
    for key, value in info.items():
        total = sum([value['th'][0], value['cancer'][0], value['ctl'][0], value['stromal'][0]])
        tmp_dict.append((key, value['cancer'][0] / total, value['th'][0] / total, value['ctl'][0] / total, value['stromal'][0] / total))

    tmp_df = pd.DataFrame.from_records(tmp_dict, columns=['Patient', 'cancer', 'th', 'ctl', 'stromal'])

    # Colors
    colors = plt.cm.RdYlGn(np.linspace(0.3, 1, len(rows)))
    colors = colors[::-1]

    # Figure
    # plt.style.use('ipynb')
    fig, axes = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 4]},figsize=(9.5, 11))

    # Plotting
    plot2 = tmp_df.plot.barh(stacked=True, ax=axes[0],width=0.75)
    plot1 = subdata.plot.barh(stacked=False, color={k: c for k, c in zip(rows, colors)}, ax=axes[1], width=0.75)

    # y ticks
    plot2.set_yticklabels(columns, fontsize=12)
    # plot2.set_yticklabels([])
    plot1.set_yticks([])

    # x ticks
    # plot2.set_xticklabels([])
    # plot2.set_xticks([])

    # x labels
    plot1.set_xlabel("Pourcentage de croissance du cancer \n après 3 jours de traitment", fontsize=14)
    plot2.set_xlabel("Proportion initiale", fontsize=14)

    # y labels
    plot2.set_ylabel("Patient", fontsize=15)

    # Legend for plot 1
    legend_item_plot_1 = list(map(lambda x: x.strip('gbm-'), rows))
    legend_item_plot_2 = ['Cancéreuse', 'TH', 'CTL', 'Stromale']

    # legends
    plot1.legend(legend_item_plot_1, prop={'size': 12}, fancybox=True, shadow=True, loc='upper right' ) #bbox_to_anchor=(1.5, 1)
    plot2.legend(legend_item_plot_2, prop={'size': 12}, ncol=1, loc='upper right', fancybox=True, shadow=True, bbox_to_anchor=(5, 0.9))
    plot2.set_zorder(1)


    # Additionnal (not in legend)
    plot1.axvline(0, color='black', linewidth=0.2)  # Vertical bar


    # for i, v in zip(range(len(yy)),yy):
    #     plot2.text(1.1, i-0.2, f"{v[0]}% ; {v[1]}%", color='black')

    fig.tight_layout()
    plt.subplots_adjust(left=0.23, bottom=0.0725, wspace=0)
    plt.savefig(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result", 'reduction_comparison.pdf'))

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

    # Some interesting values
    tmp = df.describe()

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
        dataframe_dict[key].rename(columns={'Croissance': key}, inplace=True)

    tmp = pd.concat([dataframe_dict[keys[0]]['Patient']]+[dataframe_dict[key][key] for key in keys], ignore_index=False, sort=False, axis=1)
    with open(os.path.join(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result",'combined_reduction_table.tex'),'w') as file:
        file.write(tmp.to_latex(index=False))

    return tmp




paths = [
    r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz",
    r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\ov",
    r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus"
]
keys = ['gbm-tmz', 'gbm-ov','gbm-tmz-ov']


# Global

# Figure
table_reduction_combined(paths, keys)
# Table
reduction_comparison(paths, keys)
factor_vs_cancer_growth_combined(paths,keys)

# Individual
for path,key in zip(paths,keys):

    #Table
    table_reduction_percentage(path, key)

    # Figure
    batch_cell_over_time(path, key)
    batch_discrete_differential(path, key)
    factor_vs_cancer_growth(path, key)







from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

def svg_to_pdf(path):
    i=0
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            if '.svg' in file:
                print(os.path.join(root,file))
                if (not file in ['final.svg','initial.svg','legend.svg']) and i%5==0:

                    drawing = svg2rlg(os.path.join(root,file))
                    renderPDF.drawToFile(drawing, f"{file.split('.svg')[0]}.pdf")
                i+=1

# svg_to_pdf(r"C:\Users\VmWin\Documents\University\Ete2022\Stage\Simulation\result\tmz_virus\29gbm-tmz-ov_2022-08-17T07_27_13")
