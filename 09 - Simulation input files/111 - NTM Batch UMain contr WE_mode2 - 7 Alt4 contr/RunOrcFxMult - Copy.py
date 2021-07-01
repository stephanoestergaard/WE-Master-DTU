
import os
import multiprocessing
import OrcFxAPI

def worker(file_name, folder):
    
    os.chdir(folder)
    
    model = OrcFxAPI.Model()

    model.LoadData(file_name)

    model.RunSimulation()

    sim_name = os.path.splitext(file_name)[0] + ".sim"

    model.SaveSimulation(sim_name)


def folders_files(main_folder):


    #Create list of *.dat files that starts with 5 digits
    os.chdir(main_folder)

    dat_files_list = []
    folders_list = []

    for path, subdirs, files in os.walk(main_folder):
    #for file in glob.glob("*.dat"):
        for file in files:
            if file.find('.dat') > 0:
                if file.find('Base') == -1:
                    dat_files_list.append(file)
                    folders_list.append(path)
                    print(file)
                    print(path)
        
    dat_files_list = sorted(dat_files_list)
    
    return [dat_files_list, folders_list]



if __name__ == '__main__':

    main_folder = os.getcwd()
    
    dat_files_list, folders_list = folders_files(main_folder)

    n_threads = 4

    pool = multiprocessing.Pool(n_threads)
    for i in range(len(dat_files_list)):
        if i > 45:
            pool.apply_async(worker, args = (dat_files_list[i],folders_list[i]))
    pool.close()
    pool.join()
    
    x = input('Enter')
