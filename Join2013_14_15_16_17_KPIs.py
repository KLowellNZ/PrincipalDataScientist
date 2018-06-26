# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 08:29:33 2018

@author: Kim Earl Lowell
"""

#%%
# This is a utility program to join yearly NCUA files so that the KPIs can
# be examined as a temporal sequence. Read NCUA KPI files for 2013, 14, 15,
# 16, and 17. Then produce output file that has CU ID info, all dates for
# KPI 1, then all dates for KPI 2, etc.
################ JoinKPI ##################################################
# This function joins KPIs from different years to each other.
def JoinKPI(dfout,dfyear,i,year):
    colnames=list(dfyear)
    colnames=[colnames[0],colnames[i+1]]
    dftemp=pd.DataFrame(columns=colnames)
    dftemp['CU_NUMBER']=dfyear['CU_NUMBER']
    dftemp.iloc[:,1]=dfyear.iloc[:,i+1]
    newname=colnames[1]+ year
    dftemp.rename(columns={colnames[1]:newname},inplace=True)
    dfout=pd.merge(left=dfout, right=dftemp, how='left', left_on='CU_NUMBER',
                   right_on='CU_NUMBER')
    return dfout
################ MAIN BODY OF PROGRAM #####################################
import pandas as pd
# Read in the files for the 5 different years containing KPIs for all CUs.
# Match everything to 2017 -- i.e., CUs that existed in 2013 but that do not exist
# in 2017 will not be in the final database. However, CUs that existed in 2017
# but not in 2013 WILL be in the database.
path='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Database/'
file2013='201312_KPIs_PYE_Output.csv'
file2014='201412_KPIs_PYE_Output.csv'
file2015='201512_KPIs_PYE_Output.csv'
file2016='201612_KPIs_PYE_Output.csv'
file2017='201706_KPIs_PYE_Output.csv'
outfile='KPIs_2013-17.csv'
outcols=['CU_NUMBER','JOIN_NUMBER','CU_NAME','CITY','STATE','ZIP_CODE',
         'Members','NetWorth','Assets','LoansLeases','DeposShars','FeeInc']
df2013=pd.read_csv(path+file2013)
df2014=pd.read_csv(path+file2014)
df2015=pd.read_csv(path+file2015)
df2016=pd.read_csv(path+file2016)
df2017=pd.read_csv(path+file2017)
# Drop 2013 duplicate columns
df2013=df2013.drop(['JOIN_NUMBER','CU_NAME','CITY','STATE','ZIP_CODE',
                    'Members','NetWorth','Assets','LoansLeases','DeposShars',
                    'FeeInc'],axis=1)
df2014=df2014.drop(['JOIN_NUMBER','CU_NAME','CITY','STATE','ZIP_CODE',
                    'Members','NetWorth','Assets','LoansLeases','DeposShars',
                    'FeeInc'],axis=1)
df2015=df2015.drop(['JOIN_NUMBER','CU_NAME','CITY','STATE','ZIP_CODE',
                    'Members','NetWorth','Assets','LoansLeases','DeposShars',
                    'FeeInc'],axis=1)
df2016=df2016.drop(['JOIN_NUMBER','CU_NAME','CITY','STATE','ZIP_CODE',
                    'Members','NetWorth','Assets','LoansLeases','DeposShars',
                    'FeeInc'],axis=1)
# Set up output dataframe by copying CU identification info to output df.
dfout=pd.DataFrame(columns=outcols)
for var in outcols:
    dfout[var]=df2017[var]
# Now get each of the KPIs for each year, and append to the output dataframe.
for i in range(13):
    dfout=JoinKPI(dfout, df2013, i,'_13')
    dfout=JoinKPI(dfout, df2014, i,'_14')
    dfout=JoinKPI(dfout, df2015, i,'_15')
    dfout=JoinKPI(dfout, df2016, i,'_16')
    dfout=JoinKPI(dfout,df2017,i+11,'_17')
    dfout.rename(columns={'Members':'Membs17','NetWorth':'NtWrth17',
                          'Assets':'Asst17','LoansLeases':'LonLes17',
                          'DeposShars':'DepSrs17','FeeInc':'FeeInc17'},
                          inplace=True)
# Write output file
dfout.to_csv(path_or_buf=path+outfile, index=False)