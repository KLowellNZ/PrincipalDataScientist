# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 18:07:04 2018

@author: Kim Earl Lowell
"""

#%%
# This code reformats NCUA_Bank KPI data to be suitable for Tableau. It transposes
# information for each KPI for each CU from "horizontal" to "vertical" and
# assigns a date.
############## MAIN BODY OF PROGRAM #############
import pandas as pd
import numpy as np
#inpath = "C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Output/"
inpath='C:/Analytics/DATA911/Arkatechture/FDIC_Data/FDIC_KPIs/'
#outpath = "C:/Analytics/DATA911/Arkatechture/ArkaTechVisualisations/"
outpath='C:/Analytics/DATA911/Arkatechture/FDIC_Data/FDIC_KPIs/'
#infile='KPIs_2013-17_5CUs.csv'
#outfile='KPIs_2013-17_5CUs_Transpose.csv'
infile='NCUA_and_Banks_KPIs.csv'
outfile='NCUA_and_Banks_KPIs_Transpose.csv'
# Read input file. Get column names. Set up list of first 8 to be used as 
# identifiers. Then set up output dataframe.
dfin=pd.read_csv(inpath+infile)
incols=dfin.columns.values
idcols=[]
for i in range(8):
    idcols.append(incols[i])
idcols.append('year')
# Create list of out columns so we can return the df columns to their original
# order.
dfout=pd.DataFrame(columns=idcols)
yearlist=['2013','2014','2015','2016','2017']
# Now loop through each row transposing -- knowing that years represented are
# 2013-2017.
for i in range(dfin.shape[0]):
    if i%500==0:
        print('Now working on FI:',i)
# Add five rows with identifiers to the dataframe -- one for each of the 
# 5 years.
    dftemp=pd.DataFrame(index=[0,1,2,3,4],columns=idcols)
# Now fill the rows with identifier information
    for j in range(5):
        for k in range(8):
            dftemp.iloc[j,k]=dfin.iloc[i,k]
        dftemp.iloc[j,8]=yearlist[j]
# Identifier information added to data frame. Now set up KPIs. Store KPI
# names for realphabetising.
    KPInames=[]    
    for j in range(12):
        KPIlist=[]
        KPI_name=incols[8+j*5].split('_')[0]
        KPInames.append(KPI_name)
        for k in range(5):
            KPIlist.append(dfin.iloc[i,(8+j*5+k)])
        dftemp[KPI_name]=KPIlist
# Now add this to the output dataframe.
    dfout=dfout.append([dftemp],ignore_index=True)
for KPIname in KPInames:
    idcols.append(KPIname)
dfout=dfout[idcols]
dfout.to_csv(path_or_buf=outpath+outfile, index=False)
