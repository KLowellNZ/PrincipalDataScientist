# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 08:29:33 2018

@author: Kim Earl Lowell
"""

#%%
# This program will calculate regressions for each KPI across
# 2013, 14, 15, 16, and 17.  It outputs the slope, intercept, RMSE, and r^2
# for each KPI for each credit union. The overarching goal is to be able to 
# see if slopes for KPIs are stable (i.e., low RMSE, high r^2) and if slopes
# and intercepts across all CUs have high or low variablity.
################ MAIN BODY OF PROGRAM #####################################
import pandas as pd
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

# Read in the file that has all KPIs for all years. This was produced by a
# utility program with a name like Join_2013_14_15_16_17_KPIs.py.
#path='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Output/'
path='C:/Analytics/DATA911/Arkatechture/FDIC_Data/FDIC_KPIs/'
infile='NCUA_and_Banks_KPIs.csv'
outfile='KPI_Regressions_CUs_and_Banks.csv'
outcols=['Bank_CU','FI_Number','Name','City','State','Zip','Deposits',
         'Loans_Leases']
# Read everything as a string.  Then check if a field is numbers. If not,
# convert to blank and then make the necessary columns float.
dfin=pd.read_csv(path+infile, dtype=str)
for i in range(8,dfin.shape[1]):
    dfin.iloc[:,i] = dfin.iloc[:,i].apply(pd.to_numeric, errors='coerce')
# Get list of columns from the df.       
colslist=list(dfin)
# Set up output dataframe by copying FI identification info to output df.
dfout=pd.DataFrame(columns=outcols)
for var in outcols:
    dfout[var]=dfin[var]
# Now loop across all 13 KPIs amd get regressions for each credit union.
# We set up years as the X variable, and then Y is the value of the KPI
# we are working on.
suffixes=['_intr','_slop','_RMSE','_invrsq']
X=[[2013],[2014],[2015],[2016],[2017]]
#X=[2013,2014,2015,2016,2017]
for i in range(12):
    print('Now working on KPI',i+1)
# New KPI.  Get KPI prefix and add empty columns to the dataframe.
    prefix=colslist[8+i*5][:-3]
    for suff in suffixes:
        dfout[prefix+suff]=''
    for j in range(dfin.shape[0]):
        Y=[]
        Xnew=[]
        for k in range(5):
            if not pd.isnull(dfin.iloc[j,8+i*5+k]):
                Y.append(dfin.iloc[j,8+i*5+k])
                Xnew.append(X[k])
# Only do regression if there are more than three observations for this CU.
        if len(Y) > 2:
            reg = linear_model.LinearRegression()
# Despite best efforts, some rows cause the regression to bomb. Simply do not
# calculate for those.
            try:
                reg.fit(Xnew,Y)
                y_pred=reg.predict(Xnew)
                RMSE= mean_squared_error(Y,y_pred)**0.5
                r2=1-r2_score(Y,y_pred)
#        if i==0 and j==1:
#            print('Xnew Y',Xnew,Y, '\nint slop RMSE r2',reg.intercept_,reg.coef_,RMSE,r2)
                dfout.ix[j,prefix+'_intr']=round(reg.intercept_,1)
                dfout.ix[j,prefix+'_slop']=round(reg.coef_[0],3)
                dfout.ix[j,prefix+'_RMSE']=round(RMSE,3)
                dfout.ix[j,prefix+'_invrsq']=round(r2,3)  
            except:
                dfout.ix[j,prefix+'_intr']=''
                dfout.ix[j,prefix+'_slop']=''
                dfout.ix[j,prefix+'_RMSE']=''
                dfout.ix[j,prefix+'_invrsq']='' 
# Values calculated. Now add them to output dataframe.
        else:
            dfout.ix[j,prefix+'_intr']=''
            dfout.ix[j,prefix+'_slop']=''
            dfout.ix[j,prefix+'_RMSE']=''
            dfout.ix[j,prefix+'_invrsq']='' 
#    if i>0:
#        break
# Write output file
dfout.to_csv(path_or_buf=path+outfile, index=False)