# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:51:26 2023

@author: lkear
"""
import os
import pandas as pd
import readGrawProfile_alg as rgp

print("######### Read From File and Convert Data ####################\n")
                 
dataSource = rgp.getUserInputFile("Select path to data input directory: ")
saveData   = rgp.getUserInputTF("Do you want to save output data?")

if saveData:
    savePrompt = rgp.getUserInputTF("Save to same directory?")
    if savePrompt: 
        savePath = dataSource
    elif saveData:
        savePath = rgp.getUserInputFile("Enter path to data output directory:")
    else:
        savePath = "NA"
else:
    savePath = "NA"
    
for path, subdirs,files, in os.walk(dataSource):
    for file in os.listdir(path):
        try:
            profile = rgp.readProfile(dataSource,subdirs,path,file)
            if profile is not None:
                data = profile[0]
                saveName = profile[2]
                datetime = profile[3]
                
                ##################################         
        except:
            print("Error Running " +saveName)
            pass

#Save File
if saveData:
    save_folder = r"C:\\Users\\nirau\\OneDrive\\Desktop\\U-of-I-NEBP\\Hodograph\\data"
    save_path = os.path.join(save_folder, "rawDataout.csv")
    data.to_csv(save_path)      
    print("Data Saved")


print("################## Conversion to csv done ###################\n")

print("Calculating.......")


# Detects and sets source and data directories, changes to source to import rest of program
ProgramDirectoryMain = os.getcwd()
SourceDirectory = os.path.join(ProgramDirectoryMain, 'C:\\Users\\nirau\\OneDrive\\Desktop\\U-of-I-NEBP\\Hodograph\\src')
DataDirectory = os.path.join(ProgramDirectoryMain, 'C:\\Users\\nirau\\OneDrive\\Desktop\\U-of-I-NEBP\\Hodograph\\data')
os.chdir(SourceDirectory)

#Custom Dependencies in source file
import OutputFormater as out
import InterpolateData as ID
import ButterworthFilter as BF
import CalculateUV as CUV
import CalculatePotentialTemp as PT
import CalculateCoriolisFrequency as CCF
import CalculateBruntVaisala as CBV
import PlotHodo as PH

#Setup debug
DoPrintOutput = True
out.txt('DoPrintOutput is TRUE',DoPrintOutput)
if(DoPrintOutput == True): out.OutputTest() #Testing output messages

os.chdir(DataDirectory) # set data directory

#Put Filenames Here
InputFileName = 'rawDataout' # name of input file
OutputFileName = str(InputFileName + '_Filtered.csv') # name of input file

#Load data File
InputFileName = str(InputFileName + '.csv')
data = pd.read_csv(InputFileName,index_col=0)
out.txt("Loaded {FileName}".format(FileName = InputFileName),DoPrintOutput)

def runFilterProgram(data):
    #Start filtering
    data = ID.InterpolateReIndex(data, "Time", "Alt", 5, DoPrintOutput) #Interpolate Data on altitude
    data = CUV.CalculateUV(data, DoPrintOutput) #Calculate U,V
    
    #Butterworth Filter Frequency from coriolis force
    LaunchLattitude = data['Lat'].iat[0] #Launch location lattitude from first data point
    FrequencyHigh,FrequencyLow = CCF.CalculateCoriolisFrequency(LaunchLattitude, DoPrintOutput)
    
    #Other butterworth filter variables
    fs = 1/5 #Frequency of samples in seconds per meter
    filterOrder = 3 # 3 is found to be the best for this application, but higher orders are usable
    
    #Butterworth Filter Data
    data['Ufiltered'] = BF.UVButterworth(data['U'],filterOrder,'hz',FrequencyHigh,FrequencyLow,fs,DoPrintOutput)
    data['Vfiltered'] = BF.UVButterworth(data['V'],filterOrder,'hz',FrequencyHigh,FrequencyLow,fs,DoPrintOutput)
    
    PotentialTempReferencePressure = 1000 #sets reference pressure for temp calculation
    data['Tpotential'] = PT.CalculatePotentialTemperature(data['T'], PotentialTempReferencePressure, data['P'], DoPrintOutput) #Calculate Potential Temperature
    data['bv2'] = CBV.CalculateBruntVaisalaSquared(data['Tpotential'],data['Alt'],DoPrintOutput) #Calculate Brunt-Vaisala Squared
    
    #Create filtered temperature
    data['TemperatureFiltered'] = BF.UVButterworth(data['T'],filterOrder,'hz',FrequencyHigh,FrequencyLow,fs,DoPrintOutput)
    
    return(data)

data = runFilterProgram(data)

#Save filtered data
data.to_csv((OutputFileName))   

#Plotting U,V to check filtering
#PH.macroHodo(data['Alt'], data['Ufiltered'], data['Vfiltered'])

#---------------TEST BELOW THIS LINE, NOT FINAL--------------
import matplotlib.pyplot as plt

# u = list(data['Ufiltered'])
# v = list(data['Vfiltered'])
# FilterTest,IntersectTest = IT.checkIntercept(u,v,DoPrintOutput)
# out.wrn(IntersectTest,DoPrintOutput)
# plt.figure()
# plt.scatter(list(FilterTest),list(FilterTest))
#TODO: Create functions for detecting ellipsis in hodograph

#---------------- tkinter code below -------------------------

# root = TK.Tk()

# TK.mainloop()