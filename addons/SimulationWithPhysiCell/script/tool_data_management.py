#############
## Package ##
#############
import os
import shutil

# Data Science
import numpy as np
import scipy.io

# Parser
import xmltodict

## PySide
from PySide6.QtWidgets import QFileDialog


class Config:
    def __init__(self, *args, **kwargs):

        self.kwargs = kwargs
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.args = args
        self.dict_from_xml = self.dict_form()
        self.xml_from_dict = self.xml_form()

    def xml_form(self):
        if 'data' in self.kwargs:
            # From conversion of dict to xml
            self.dict_from_xml = Config.dict2xml(self.kwargs['data'])

            return self.xml_from_dict
        else:
            return False
    def dict_form(self):
        if 'file' in self.kwargs:
            # From conversion of xml to dict
            self.dict_from_xml = Config.xml2dict(self.kwargs['file'])
            return self.dict_from_xml
        else:
            return False
    def list_user_parameters(self):
        if self.dict_from_xml == {}:
            self.dict_form()

        arguments = ['PhysiCell_settings', 'user_parameters']
        karguments = {'dictionary': self.dict_from_xml}

        return Config.get2dict(*arguments, **karguments)
    def list_cell(self):
        if self.dict_from_xml == {}:
            self.dict_form()

        arguments = ['PhysiCell_settings', 'cell_definitions', 'cell_definition']
        karguments = {'dictionary': self.dict_from_xml}

        return list(map(lambda p: p['@name'], Config.get2dict(*arguments, **karguments)))
    def change_user_parameters(self, *args, new_value=None):
        # subnode possibility:
        # '@type'
        # '@units'
        # '@description'
        # '#text'

        arguments = ['PhysiCell_settings', 'user_parameters'] + list(args)
        karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
        Config.edit2dict(*arguments, **karguments)
        return
    def change_microenvironment_physical_parameter_set(self, *args, name=None, new_value=None):
        idx = Config.find_variable_index(data=self.dict_from_xml, name=name)
        if idx:
            arguments = ['PhysiCell_settings', 'microenvironment_setup', 'variable', idx,
                         'physical_parameter_set'] + list(args)
            karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
            Config.edit2dict(*arguments, **karguments)
            return True
        else:
            return False
    def change_cell_definition_phenotype(self, *args, name=None, new_value=None):
        idx = Config.find_cell_index(data=self.dict_from_xml, name=name)
        if idx:
            arguments = ['PhysiCell_settings', 'cell_definitions', 'cell_definition', idx, 'phenotype'] + list(args)
            karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
            Config.edit2dict(*arguments, **karguments)
            return True
        else:
            return False
    def change_cell_definition_custom_data(self, *args, name=None, new_value=None):
        idx = Config.find_cell_index(data=self.dict_from_xml, name=name)
        if idx:
            arguments = ['PhysiCell_settings', 'cell_definitions', 'cell_definition', idx, 'custom_data'] + list(args)
            karguments = {'dictionary': self.dict_from_xml, 'new_value': new_value}
            Config.edit2dict(*arguments, **karguments)
        else:
            return False


    @staticmethod
    def xml2dict(xml_file, *args, **kwargs):
        xml = open(xml_file, "r")
        org_xml = xml.read()
        tree = xmltodict.parse(org_xml, process_namespaces=True)
        return tree
    @staticmethod
    def dict2xml(data, destination, xml_file_name, *args, **kwargs):
        out = xmltodict.unparse(data, pretty=True)
        with open(os.path.join(destination,f"{xml_file_name}.xml"), 'w') as f:
            f.write(out)
    @staticmethod
    def find_variable_index(data, name):
        i = 0
        for var in data['PhysiCell_settings']['microenvironment_setup']['variable']:
            if not var['@name'] == name:
                i += 1
            else:
                return i
        return False
    @staticmethod
    def find_cell_index(data, name):
        i = 0
        for var in data['PhysiCell_settings']['cell_definitions']['cell_definition']:
            if not var['@name'] == name:
                i += 1
            else:
                return i
        return False
    @staticmethod
    def get2dict(*args, **kwargs):
        """From every argument, retrieve the value in the dictionary"""
        dictionary = kwargs['dictionary']
        if len(args) == 0:
            return

        if len(args) == 1:
            return dictionary[args[0]]
        else:
            return Config.get2dict(*args[1::], **{'dictionary': dictionary[args[0]]})
    @staticmethod
    def edit2dict(*args, **kwargs):
        """

        :param args: str, str, ....
        :param kwargs: dictionary=dict, new_value=...

        Example we want to change dicto['un']['deux1']['quatre']['cinq1'] to 13
        dicto = {'un': {'deux1':{'trois1':31,'quatre':{'cinq1':51,'six1':61}},'deux2':22}, 'deux':{'trois1':31,'quatre':{'cinq1':51,'six1':61}},'deux2':22}
        arc = ['un','deux1','quatre','cinq1']

        edit2dict(*arc, **{'dictionary':dicto, 'new_value':13})

        Before
        ------------------------------------------------------------------------------------------------------------------------
        {'un': {'deux1': {'trois1': 31, 'quatre': {'cinq1': 51, 'six1': 61}}, 'deux2': 22}, 'deux': {'trois1': 31, 'quatre': {'cinq1': 51, 'six1': 61}}, 'deux2': 22}
        ------------------------------------------------------------------------------------------------------------------------
        After
        ------------------------------------------------------------------------------------------------------------------------
        {'un': {'deux1': {'trois1': 31, 'quatre': {'cinq1': 13, 'six1': 61}}, 'deux2': 22}, 'deux': {'trois1': 31, 'quatre': {'cinq1': 51, 'six1': 61}}, 'deux2': 22}
        """
        dictionary = kwargs['dictionary']
        new_value = kwargs['new_value']
        if len(args) == 0:
            return
        if len(args) == 1:
            dictionary[args[-1]] = new_value
            return
        else:
            tmp = Config.get2dict(*args[:-1:], **{'dictionary': dictionary})
            tmp[args[-1]] = new_value
            Config.edit2dict(*args[:-1:], **{'dictionary': dictionary, 'new_value': tmp})
    @staticmethod
    def unit_test():
        file = r'C:\Users\VmWin\Pictures\test\PhysiCell_settings.xml'
        unit = {}
        print_test = lambda txt, cdn: print(f"{txt}{'-' * (90 - len(txt))}{str(cdn)}")

        # load xml file
        test = Config(file=file)

        parameters_list = ["random_seed", "kappa", "c_s", "epsilon", "xhi",  "proportion", "p_max", "pbar_max", "rho_max", "f_F", "c_j_ccr", "A_frag", "R", "sigma", "mu", "eta", "K_V", "K_C", "r_10", "V_N_CD4", "N_CD4", "R_CD4", "r_01_CD4", "S_chemokine_CD4", "TH_prolif_increase_due_to_stimulus", "V_N_GBM", "R_GBM", "beta", "u_g", "N_GBM_sparse", "N_GBM_dense", "V_N_CD8", "N_CD8", "R_CD8", "r_01_CD8", "d_attach", "nu_max", "tau", "b_CD8", "CTL_prolif_increase_due_to_stimulus", "V_N_stromal", "R_stromal", "nu", "u_s", "N_stroma_sparse", "N_stroma_dense", "lambda_virus", "D_virus", "alpha", "delta_V", "gamma", "m_half", "rho_star_virus", "V_0", "lambda_chemokine", "D_chemokine", "nu_star", "rho_star_chemokine",  "lambda_tmz", "D_tmz", "IC50"]

        # list_user_parameters
        unit["list_user_parameters"] =  list(filter(lambda t: t[0]!=t[1], zip(test.list_user_parameters(), parameters_list))) == []

        # list_cell
        unit['list_cell'] = test.list_cell() == ['default','th', 'cancer', 'ctl', 'stromal']

        # change_user_parameters
        test.change_user_parameters('kappa', '#text', new_value=3223)
        unit['change_user_parameters'] = test.dict_from_xml['PhysiCell_settings']['user_parameters']['kappa']['#text'] == 3223

        # find_variable_index
        unit['find_variable_index'] = Config.find_variable_index(test.dict_from_xml, name='tmz') == 3

        # change_microenvironment_physical_parameter_set
        test.change_microenvironment_physical_parameter_set('diffusion_coefficient', '#text', name='tmz', new_value=46.1)
        unit['change_microenvironment_physical_parameter_set'] = test.dict_from_xml['PhysiCell_settings']['microenvironment_setup']['variable'][3]['physical_parameter_set']['diffusion_coefficient']['#text'] == 46.1

        # find_cell_index
        unit['find_cell_index'] = Config.find_cell_index(test.dict_from_xml, name='stromal') == 4

        # change_cell_definition_phenotype
        test.change_cell_definition_phenotype('cycle', 'phase_transition_rates', 'rate', '#text', name='stromal', new_value=1)
        unit['change_cell_definition_phenotype'] = test.dict_from_xml['PhysiCell_settings']['cell_definitions']['cell_definition'][4]['phenotype']['cycle']['phase_transition_rates']['rate']['#text'] == 1

        # change_cell_definition_custom_data
        test.change_cell_definition_custom_data('sample', '#text', name='stromal', new_value=2)
        unit['change_cell_definition_custom_data'] = test.dict_from_xml['PhysiCell_settings']['cell_definitions']['cell_definition'][4]['custom_data']['sample']['#text'] == 2

        for k, v in unit.items():
            print_test(k, v)
        return

# Data from collaborators conversion and manipulation
class Data:
    def __init__(self):
        self.temp_dict = {
            'Th': 1,
            'Cancer': 2,
            'Tc': 3,
            'Cl BMDM': 5,
            'Cl MG': 5,
            'Alt BMDM': 6,
            'Alt MG': 6,
            'Endothelial cell': 4
        }
        pass

    @staticmethod
    def ind2sub(sz, ind):
        x, y = np.unravel_index(ind, sz, order='F')
        y = np.array([[yy[0] + 1] for yy in y])
        return x, y

    @staticmethod
    def median_ind2sub(sz, ind):
        x, y = Data.ind2sub(sz, ind)
        return np.median(x), np.median(y)

    @staticmethod
    def mean_ind2sub(sz, ind):
        x, y = Data.ind2sub(sz, ind)
        return np.mean(x), np.mean(y)

    @staticmethod
    def x_y_position_type(position_file, cell_type_file, center=500, type_dict=None):
        mat1 = scipy.io.loadmat(position_file)
        mat2 = scipy.io.loadmat(cell_type_file)

        cell_number = mat2['cellTypes'].size

        # shape of the matrix
        size = mat1['nucleiImage'].shape

        for i in range(cell_number):

            # cell type
            try:
                c_t = mat2['cellTypes'][i][0][0] #c_t for cell type

                if type_dict:
                    if c_t in type_dict.keys():
                        cell_type = type_dict[c_t]
                    else:
                        cell_type = None
            except:
                cell_type = None

            if cell_type:
                # ith cell's boundaries
                cell_boudaries = mat1['Boundaries'][0][i]


                # median position of the cell
                x, y = Data.mean_ind2sub(size, cell_boudaries)

                cell_position = [round(x - center,4), round(y - center,4), 0, cell_type]
                yield cell_position

    @staticmethod
    def convert_to_csv(destination, filename, data):
        np.savetxt(os.path.join(destination, f"{filename}.csv"), data, delimiter=",", fmt='%s')

    @staticmethod
    def create_dirtree_without_files(src, dst):
        # getting the absolute path of the source
        # directory
        src = os.path.abspath(src)

        # making a variable having the index till which
        # src string has directory and a path separator
        src_prefix = len(src) + len(os.path.sep)

        # making the destination directory
        os.makedirs(dst)

        # doing os walk in source directory
        for root, dirs, files in os.walk(src):
            for dirname in dirs:
                # here dst has destination directory,
                # root[src_prefix:] gives us relative
                # path from source directory
                # and dirname has folder names
                dirpath = os.path.join(dst, root[src_prefix:], dirname)

                # making the path which we made by
                # joining all of the above three
                os.mkdir(dirpath)

    ## The class you need to convert patient data into cvs file (recursivly0
    @staticmethod
    def data_conversion_segmentation_celltypes(source, destination, type_dict=None):
        try:
            dest = os.path.join(destination, source.split(os.sep)[-1])
            Data.create_dirtree_without_files(source, dest)

        except:
            shutil.rmtree(destination)
            Data.create_dirtree_without_files(source, destination)

        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(source):
            path = root.split(os.sep)

            for file in files:

                if 'nuclei_multiscale.mat' in file:
                    f_path = os.path.join(*([f"C:{os.sep}"] + path[1::] + [file])) #absolute path
                    position_file = f_path

                    # For each scan segmentation have a folder, not for celltypes
                    # we have one layer to substract
                    cell_type_file = os.path.join(*([f"C:{os.sep}"] + path[1::])).replace('Segmentation',
                                                                                          'CellTypes') + '.mat'





                    # data
                    data = np.asarray(
                        [
                            item for item in


                            Data.x_y_position_type(position_file,
                                                   cell_type_file,
                                                   type_dict=type_dict)
                        ]
                    )

                    # Construct destination path
                    idx = path.index('Segmentation')
                    relative_path = os.path.join(*(path[idx::]))
                    absolute_path = destination

                    dst = os.path.join(absolute_path, relative_path)

                    # filename
                    # filename = file.replace('.mat', '')
                    filename = path[-1].split(' ')[-1]

                    # convert_to_csv
                    Data.convert_to_csv(dst, filename, data)

    @staticmethod
    def scan_csv_file(source, name=None):
        file_list = []
        condition = None
        if name:
            condition = lambda f: (name in f) and ('.csv' in f)
        else:
            condition = lambda f: ('.csv' in f)
        for root, dirs, files in os.walk(source):
            path = root.split(os.sep)

            for file in files:
                if condition(file):
                    file_list.append(os.path.join(root,file))
        return file_list

    @staticmethod
    def loadFiles(start_directory=None):
        # filter = "TXT (*.txt);;PDF (*.pdf)"
        parent = None
        filter = "CSV (*.csv)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        names = file_name.getOpenFileNames(parent, "Open files", start_directory, filter)
        if not names[0]:
            return False

        return names[0]


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