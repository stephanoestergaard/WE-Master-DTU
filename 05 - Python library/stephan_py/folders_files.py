"""
This module contains functions operating with sim_files
"""
import os
import glob
import pandas as pd

def list_simfiles(folder):
    
    """
    Function returns a list of sim_files for a given folder
    """

    os.chdir(folder)
    
    prefix = os.path.basename(os.path.normpath(folder)).split("-")[0].strip()
        
    # Make list of *.sim files
    sim_files_list = []
    sim_file_folders_list = []
    
    
    #for file in glob.glob("*.sim"):o
    for path, subdirs, files in os.walk(folder):
        for file in files:
            if file.find('.sim') > 0:
                sim_files_list.append(file)
                sim_file_folders_list.append(path)

    sim_files_list = sorted(sim_files_list)
    
    return [sim_files_list, sim_file_folders_list, prefix]
    

def read_vars_TH(sim_file_path):

    # Read variables and units from a time history csv file
    file_path = os.path.splitext(sim_file_path)[0] + "_TH.csv"

    TH_vars = pd.read_csv(file_path, index_col=0, nrows=0).columns.tolist()
    
    df_tmp = pd.read_csv(file_path)
    
    units = df_tmp.iloc[0][1:].tolist()
    
    return [TH_vars, units]
    

def checkTHvarsSimilar(selected_folders):

    # Check that numbers of sim files are the same for chosen folders and make a list 
    # of sim files for each folder.
    # Also check of extracted variabels in simfiles are the same
    
    
    # Read lists of sim files
    sim_files = []
    n_sim_files = []
    for folder in selected_folders:
    
        sim_files.append(list_simfiles(folder)[0])
        n_sim_files.append(len(list_simfiles(folder)[0]))
        
    # Read variables from first TH csv file in each folder and compare extracted variables
    GenVariableNames = []
    ResultsCheck = ''

    for j in range(len(selected_folders)):
    
        GenVariableNames_list, units = read_vars_TH(selected_folders[j] + '\\' + sim_files[j][0])
    
        GenVariableNames.append(GenVariableNames_list)
        
        # Check number of simfiles when running through folders
        if n_sim_files[0] != n_sim_files[j]:
                ResultsCheck = ResultsCheck + 'Number of sim files does not match different. \n'
    

    # check that extracted variables and number of simfiles are the same
    for i in range(len(GenVariableNames_list)):
    
        for j in range(len(selected_folders)-1):
        
            if GenVariableNames[0][i] != GenVariableNames[j+1][i]:
                ResultsCheck = ResultsCheck + 'Results extracted in folders are different. \n'
    
    if ResultsCheck == '':
            ResultsCheck = 'Results are of similar structure wrt. no. of simfiles and extracted variables.'
    
    return ResultsCheck
    

def StartDict(object_names, OrcFxVariableNames, GenVariableNames, objectExtras):
    
    # Create a new extraction dictionary and save to file
    # Variable examples
    '''
    object_names = ["15MW RWT", "15MW RWT"]
    OrcFxVariableNames = ["Root connection Ey moment", "Root connection Ex moment"]
    GenVariableNames = ["RootMxb1", "RootMyb1"]
    objectExtras = ['OrcFxAPI.oeTurbine(1)', 'OrcFxAPI.oeTurbine(1)']
    '''
    extraction_def = [[0 for i in range(3)] for j in range(len(GenVariableNames))]

    for i in range(len(GenVariableNames)):
        extraction_def[i][0] = OrcFxVariableNames[i]
        extraction_def[i][1] = object_names[i]
        extraction_def[i][2] = objectExtras[i]
    extraction_dict = dict(zip(GenVariableNames, extraction_def))
    
    with open('extraction_defs_new.json', 'w') as fp:
        json.dump(extraction_dict, fp, ensure_ascii=False, indent=4)

    # finally print to check and to copy-paste from
    pprint.pprint(extraction_dict, sort_dicts=False, width=150)   
