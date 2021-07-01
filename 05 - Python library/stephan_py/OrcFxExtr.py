"""
This module contains plot functions used in the project
"""
import OrcFxAPI
import statistics as stat

# Extract time history
class TH(object):
    
    def __init__(self, OrcFxobject, variableName, period, objectExtra):
        self.OrcFxobject = OrcFxobject
        self.variableName = variableName
        self.period = period
        self.objectExtra = objectExtra
        self.THvalues = self.OrcFxobject.TimeHistory(self.variableName, self.period, self.objectExtra)
        self.var_details = self.OrcFxobject.varDetails(OrcFxAPI.rtTimeHistory, self.objectExtra)
        
    def getTH(self):
        return self.THvalues
    
    def getUnit(self):
        for j in range(len(self.var_details)):
            if self.var_details[j].VarName == self.variableName:
                unit = self.var_details[j].VarUnits
        return unit
    
    def getTHmax(self):
        return max(self.THvalues)
    
    def getTHmin(self):
        return min(self.THvalues)
    
    def getTHavg(self):
        return sum(self.THvalues)/len(self.THvalues)
    
    def getTHabsmax(self):
        return max(abs(self.getTHmax()), abs(self.getTHmin()))
    
    def getTHstddev(self):
        return stat.stdev(self.THvalues)
        
        
# Extract Rainflow half-cycles
class RF_HC(object):
    
    def __init__(self, OrcFxobject, variableName, period, objectExtra):
        self.OrcFxobject = OrcFxobject
        self.variableName = variableName
        self.period = period
        self.objectExtra = objectExtra
        self.RFHCvalues = self.OrcFxobject.RainflowHalfCycles(self.variableName, self.period, self.objectExtra)
        
    def getRFHC(self):
        return self.RFHCvalues
        
        
# Extract Rainflow half-cycles
class RF_AssocMean(object):
    
    def __init__(self, OrcFxobject, variableName, period, objectExtra):
        self.OrcFxobject = OrcFxobject
        self.variableName = variableName
        self.period = period
        self.objectExtra = objectExtra
        self.RFAMvalues = self.OrcFxobject.RainflowAssociatedMean(self.variableName, self.period, self.objectExtra)
        
    def getRF_AM(self):
        return self.RFAMvalues       
