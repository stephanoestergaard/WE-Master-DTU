"""
This module contains calculation functions
"""
import pandas as pd
import rainflow
import numpy as np
import math


def CalcDEL(TH_series,m):
    """
    This function calculates the damage equivalent load for a time history for a given exponent 'm'
    Except the final part raising to the power of 1/m.
    """
    
    # DEL of time history
    Neq = 1.e7
    
    DEL = 0.0
    
    # Converst pd.Series to list
    TH = pd.to_numeric(TH_series, errors='coerce')
    
    # Do the rainflow counting
    for rng, mean, mult, i_start, i_end in rainflow.extract_cycles(TH):
        DEL = DEL + np.power(rng, m) * mult

    DEL = DEL / Neq
    
    return DEL 


def FreqtoN10mins(yr, freq):
    """
    This function returns the count multiplier for n years and a given frequency
    """
    
    return float(yr) * 365. * 24. * 6. * float(freq)
    
    
def THtoWH(TH, delta_t):
    """
    This function returns the Wh's for a 600 s time history
    Parameters
    ----------
    TH : pd.Series
        List of generator power values (kW)

    Returns
    -------
    float
        Wh
    """
    
    # Trim series
    TH = TH[1:].astype(float)
    
    Wh = TH.sum() * delta_t / 3600. * 1000.
    
    return Wh
    
def WeibullMean(weib):
    """
    This function returns calcuates mean wind speed for a Weibull distribution
    Parameters
    ----------
    weib : Weibull parameters

    Returns
    -------
    float
        Umean, mean wind speed
    """
    
    # Calcuate mean wind speed for 

    
    Umean = weib["A"] * math.gamma(1+1/weib["k"])
    
    return Umean