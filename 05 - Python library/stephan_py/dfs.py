"""
This module contains functions operating dataframes
"""
import pandas as pd
import numpy as np

def CreateDFs(sim_files, GenVariableNames, time_defs, cols):

    t_start_res = time_defs[0]
    t_end_res = time_defs[1]
    time_step = time_defs[2]
    
    # Creates basic dataframes for data extraction
    
    # Stat values
    # dataframe details
    base_df = pd.DataFrame(index=np.arange(len(sim_files)) ,columns=cols)
    
    # TH dataframe
    time = np.linspace(t_start_res, t_end_res, int((t_end_res-t_start_res)/time_step+1))
    time_ser = pd.Series(['Units'])
    time_ser = pd.concat([time_ser, pd.Series(time)], axis = 0).reset_index(drop = True)
  
    TH_base_df = pd.DataFrame(index=np.arange(len(time)+1),columns=GenVariableNames)
    TH_base_df = pd.concat([time_ser, TH_base_df], axis = 1)
    TH_base_df = TH_base_df.rename(columns={0: 'Time [s]'})
    TH_base_df['Time [s]'][1:] = TH_base_df['Time [s]'][1:].astype(float).round(decimals=1)
    TH_base_df
    
    return [base_df, TH_base_df]