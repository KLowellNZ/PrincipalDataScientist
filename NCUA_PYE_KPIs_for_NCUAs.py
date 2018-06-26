# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 13:19:35 2018

@author: Kim Earl Lowell
"""

#%%
# This file will extract the variables needed for a NCUA KPI, calculate the 
# KPI for all credit unions, then output all 12 KPIs for the 6000ish credit
# unions. It also outputs some identifying info for each bank. Get the state
# in which a CU is headquartered from foicu.
# Read the file that has information aobut which files have which ACCTs:
#################################################
# Function calcKPI accepts a list of ACCT codes and a dictionary indicating
# the FS files within which the ACCTs are found. It then returns a df having
# those accts for each credit union. The acctlist that is passed will be a
# nested list.  The first element in a nested list is the ACCT required and
# the second is the period -- AC or PYE.
def KPIdfs(AC,acctlist,acctdict):
#    inpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/201706_Call-Report-Data/'
#    prefix='201703_'
    inpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Database/'
    PYE=str(int(AC[0:4])-1)+'12'
    prefix='PYE_'
# Now go through the account list and grab what we need for the appropriate
# time. Initially, this will grab all dates for all credit unions.
    for i,acct in enumerate(acctlist):
# It is convenient to make a temporary variable name that can be used w/o
# indexing.
        if 'AC' in acct:
            period='AC'
            tempacct=acct.replace('AC','')
        if 'PYE' in acct:
            period='PYE'
            tempacct=acct.replace('PYE','')
        filename=acctdict[tempacct][1]
# The following reads ACCTs whether they are Acct, ACCT, acct.
        try:
            dfin=pd.read_csv(inpath+prefix+filename+'.csv', 
                usecols=['CU_NUMBER','CYCLE_DATE',tempacct], 
                    dtype={'CYCLE_DATE':np.str}, skipinitialspace=True)
        except:
            try:
                tempacct=tempacct.upper()
                dfin=pd.read_csv(inpath+prefix+filename+'.csv', 
                     usecols=['CU_NUMBER','CYCLE_DATE',tempacct],
                     dtype={'CYCLE_DATE':np.str},skipinitialspace=True)
            except:
                tempacct=tempacct.replace('ACCT','Acct')
                dfin=pd.read_csv(inpath+prefix+filename+'.csv', 
                     usecols=['CU_NUMBER','CYCLE_DATE',tempacct],
                     dtype={'CYCLE_DATE':np.str},skipinitialspace=True)
# Make sure column names are standardised as ACCT_xxx.
        tempacct=tempacct.upper()
        dfin.columns=['CU_NUMBER','CYCLE_DATE',tempacct]
# Convert the date column to the format we need.
        dfin['CYCLE_DATE']=pd.to_datetime(dfin['CYCLE_DATE'])
        dfin['yearmonth']= dfin['CYCLE_DATE'].dt.year.astype(str) + \
            dfin['CYCLE_DATE'].dt.month.astype(str).str.zfill(2)
# Now select the dates we want from dfin and update column name appropriately.
        if period == 'AC':
            dfin = dfin.drop(dfin[dfin['yearmonth'] != AC].index)
        else:
            dfin = dfin.drop(dfin[dfin['yearmonth'] != PYE].index)
        newname=tempacct+period
        dfin=dfin.drop(['CYCLE_DATE','yearmonth'],axis=1)
        dfin.rename(columns={tempacct:newname},inplace=True)
# Make the first variable the base dataframe.
        if i == 0:
            dfout=dfin
            continue
# Otherwise join the new dataframe.
        dfout=pd.merge(left=dfout, right=dfin, how='outer', left_on='CU_NUMBER',
               right_on='CU_NUMBER')
    return dfout
############################################################
# Function KPI_stats will calculate the mean, standard deviation, and
# coeff of variation of the KPI we've calculated, and append this
# information to the output dataframe. 
def KPI_stats(dfoutKPI,dfaccts,descrip,KPInum,KPIclass):
    cvacct= dfaccts['KPI'].std()/dfaccts['KPI'].mean()*100  
    print('\nKPI',KPInum,':',KPIclass,'\n',KPIdescrip,
      '\n Mean:',dfaccts['KPI'].mean(),'\n StDev:',dfaccts['KPI'].std(),
      '\n CV:',cvacct,'\n Count:',dfaccts['KPI'].count())
# Append information to dataframe.
#tempdf=pd.DataFrame(columns=['KPI','KPI_Class','KPI_Mean','KPI_StDev',
#                             'KPI_CV','ACCTs'])
    tempseries = pd.Series(['','','','','','',''],
                index=['KPI','KPI_Class','KPI_Mean','KPI_StDev','KPI_CV',
                'KPI_Count','KPI_Descrip'])
    tempseries.ix['KPI']= KPInum
    tempseries.ix['KPI_Class']= KPIclass
    tempseries.ix['KPI_Mean']= dfaccts['KPI'].mean()
    tempseries.ix['KPI_StDev']= dfaccts['KPI'].std()
    tempseries.ix['KPI_CV']= cvacct
    tempseries.ix['KPI_Count']=dfaccts['KPI'].count()
    tempseries.ix['KPI_Descrip']=descrip
    dfoutKPI=dfoutKPI.append(tempseries,ignore_index=True)
    return dfoutKPI
############################################################
# Function JoinKPI joins the KPI calculated to the output
# dataframe with an appropriate name.
def JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict):
    KPIname=KPInamedict[KPIclass]+str(KPInum)
    dfaccts=dfaccts[dfaccts.columns[[0,dfaccts.shape[1]-1]]]
    dfaccts=dfaccts.rename(columns={'KPI':KPIname})
    dfout=pd.merge(left=dfout, right=dfaccts,how='left')
    return dfout

############## MAIN BODY OF PROGRAM #############
import pandas as pd
import numpy as np
# Establish output file.The foicu file information must be read and then 
# relevant fields used to establish the output dataframe.
fspath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Database/'
outpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Database/'
#prefix='201703_'
# AC is the current quarter and year, PYE is the end of the previous
# financial year.
########################### SPECIFY THE YEAR ANND QUARTER FOR WHICH
########### WE WANT KPIS  #############################
#AC='201706'
#AC='201612'
#AC='201512'
#AC='201412'
AC='201312'
##############################################################
ACprefix=AC+'_'
# The following gets the bank information for the current quarter of interest.
# Set up output csv file for summary KPI info.
#callreport='Call-Report-Data/'
dfout=pd.read_csv(fspath+ACprefix+'foicu.csv',
      usecols=['CU_NUMBER','JOIN_NUMBER','CU_NAME','CITY','STATE','ZIP_CODE'],
      skipinitialspace=True)
# Now set up a dataframe to output summary statistics.
dfstats=pd.DataFrame(columns=['KPI','KPI_Class','KPI_Mean','KPI_StDev',
                               'KPI_CV','KPI_Count','KPI_Descrip'],index=None)
outfile=outpath+ACprefix+'KPIs_PYE_Output.csv'
statsfile=outpath+ACprefix+'KPIs_PYE_Stats.csv'
# Set up input of dictionary file.  Dictionary will contain all ACCT-codes
# used in the KPIs as keys and the FS files in which they will be found as
# the look-up value.
KPIindex=0
inpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/PYE_Database/'
# Set up the dictionary to know from which files to grab ACCTs.  Infile 1 is
# the file that says which ACCTs are used to calculate which KPIs and
# also tells in which file an ACCT is located.
# THIS IS HARD CODED TO A SINGLE FILE WHICH MEANS THIS DICTIONARY IS USED
# FOR ALL YEARS.  THIS IS A PROBLEM ONLY IF ACCTS CHANGE FILES FROM ONE YEAR
# TO ANOTHER..
infile1='201706_TargetKPI_TargetAccts.csv'
dfdict=pd.read_csv(inpath+infile1, usecols=['Account','AcctName','TableName'],
                   skipinitialspace=True)
# Eliminate duplicate lines. Because some ACCTs are sought in the previous year,
# we have to eliminate duplicates.
dfdict=dfdict.drop_duplicates()
# For ease of searching, make all accounts lowercase.
dfdict['Account']=dfdict['Account'].str.lower()
# Make first two characters of file lowercase.
dfdict['TableName']=dfdict['TableName'].str.replace('FS','fs')
# Create empty dictionary for ACCT/file information.
acctdict={}
# Now loop through the file and set up the dictionary.
for i in range(dfdict.shape[0]):
    key=dfdict.iloc[i,0]
    keylist=[dfdict.iloc[i,1],dfdict.iloc[i,2]]
    acctdict[key]=keylist
# Dictionary now established.  Set up separate dictionary so output KPI names
# are a bit more descriptive.
KPInamedict = {'Capital Adequacy':'CapAdeq','Asset Quality':'AsstQual',
               'Earnings':'Earnngs','Asset/Liability Management':'AstLiaMgmt',
               'Productivity':'Product','Other Ratios':'OthRatio',
               'Other Delinquency Ratios':'OthDlqRat',
               'Real Estate Loan Delinquency':'RELnDeliq',
               'Miscellaneous Loan Loss Ratios':'MiscLnLsRat',
               'Specialized Lending Ratios':'SpecLndRat',
               'Real Estate Lending Ratios':'RELndRat',
               'Miscellaneous Ratios':'MiscRatio'}
# Get ACCTs that might be used in Arkatechture searches.These will be part of
# the output file. NOTE: WHEN SPECIFYING ACCTS TO GRAB, THE PERIOD FOR 
# WHICH THEY ARE DESIRED -- AC OR PYE -- MUST BE PART OF THE ACCT NAME.
acctlist=['acct_083AC','acct_997AC','acct_010AC','acct_025bAC','acct_018AC',
           'acct_131AC']
# AC is the current year and must be passed to KPIdfs
dfaccts=KPIdfs(AC, acctlist,acctdict)
dfaccts=dfaccts.rename(columns = {'ACCT_083AC':'Members','ACCT_997AC':'NetWorth',
          'ACCT_010AC':'Assets','ACCT_025BAC':'LoansLeases','ACCT_018AC':'DeposShars',
          'ACCT_131AC':'FeeInc'})
dfout=pd.merge(left=dfout, right=dfaccts,how='left')
# Get stats for these measures.
KPInum=0
KPIclass='CU Description'
KPIdescrip='Used for querying'
# Get stats for CU descriptors.
descrips=['Members','NetWorth','Assets','LoansLeases','DeposShars','FeeInc']
for query in descrips:
    KPIclass=query
    dfquery=pd.DataFrame(columns=[query])
    dfquery[query]=dfaccts[query]
    dfquery=dfquery.rename(columns={query:'KPI'})
    dfstats=dfstats=KPI_stats(dfstats,dfquery,KPIdescrip,KPInum,KPIclass)
# Now Get KPIs and attach them to the output file.
#......................................................
# KPI 1: Capital Adequacy: Get data frame with desired ACCTs. 997, 010
KPInum=1
KPIclass='Capital Adequacy'
KPIdescrip='Page 1 Net Worth/Total Assets'
# The following are the ACCTs needed and the period for which they are
# needed.  These should be lowercase.
acctlist=['acct_997AC','acct_010AC']
# NOTE: AC is the year/quarter for which we want KPIs
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
# Note everything is now upper case.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010AC'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=dfaccts['ACCT_997AC']/dfaccts['ACCT_010AC']*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 2: Capital Adequacy: 041B/997
KPInum=2
KPIclass='Capital Adequacy'
KPIdescrip='Page 1 Total Delinquent Loans/Net Worth'
acctlist=['acct_041bAC','acct_997AC']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997AC'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=dfaccts['ACCT_041BAC']/dfaccts['ACCT_997AC']*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 5: Delinquent Loans/Total Loans  041B, 025B
KPInum=5
KPIclass='Asset Quality'
KPIdescrip='Page 2 Delinquent Loans/Total Loans'
acctlist=['acct_041bAC','acct_025bAC']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025BAC'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041BAC']/dfaccts['ACCT_025BAC'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 9: Delinquent Loans / Assets  041B, 010
KPInum=9
KPIclass='Asset Quality'
KPIdescrip='Page 3 Delinquent Loans / Assets'
acctlist=['acct_041bAC','acct_010AC']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010AC'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041BAC']/dfaccts['ACCT_010AC'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 10: Return on Average Assets - 661A, 0101
KPInum=10
KPIclass='Earnings'
KPIdescrip='Page 3 Return on Average Assets'
acctlist=['acct_661aAC','acct_010AC','acct_010PYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010AC']+dfaccts['ACCT_010PYE']== 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_661AAC']/((dfaccts['ACCT_010AC']+dfaccts['ACCT_010PYE'])/2))*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 12: Gross Income / Average Assets - 115, 131, 659, 010
KPInum=12
KPIclass='Earnings'
KPIdescrip='Page 3 Gross Income / Average Assets'
acctlist=['acct_115AC','acct_131AC','acct_659AC','acct_010AC','acct_010PYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010AC']+dfaccts['ACCT_010PYE']== 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_115AC']+dfaccts['ACCT_131AC']+dfaccts['ACCT_659AC'])/
       ((dfaccts['ACCT_010AC']+dfaccts['ACCT_010PYE'])/2))*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 13: Yield on Average Loans - 110, 119, 025b
KPInum=13
KPIclass='Earnings'
KPIdescrip='Page 3 Yield on Average Loans'
acctlist=['acct_110AC','acct_119AC','acct_025bAC','acct_025bPYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025BAC']+dfaccts['ACCT_025BPYE']== 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_110AC']-dfaccts['ACCT_119AC']) /
       ((dfaccts['ACCT_025BAC']+dfaccts['ACCT_025BPYE'])/2))*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 15: Fee and Other Operating Income / Average Assets - 131, 659, 010
KPInum=15
KPIclass='Earnings'
KPIdescrip='Page 4 Fee and Other Operating Income / Average Assets'
acctlist=['acct_131AC','acct_659AC','acct_010AC','acct_010PYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010AC']+dfaccts['ACCT_010PYE']== 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_131AC']+dfaccts['ACCT_659AC']) /
       ((dfaccts['ACCT_010AC']+dfaccts['ACCT_010PYE'])/2))*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 26: Total Loans / Total Shares  025B, 018
KPInum=26
KPIclass='Asset/Liability Management'
KPIdescrip='Page 7 Total Loans / Total Shares'
acctlist=['acct_025bAC','acct_018AC']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_018AC'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_025BAC']/dfaccts['ACCT_018AC'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 27: Total Loans / Total Assets  025B, 010
KPInum=27
KPIclass='Asset/Liability Management'
KPIdescrip='Page 7 Total Loans / Total Assets'
acctlist=['acct_025bAC','acct_010AC']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010AC'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_025BAC']/dfaccts['ACCT_010AC'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 40: Market (Share) Growth - 018(AC), 018(PYE)
KPInum=40
KPIclass='Other Ratios'
KPIdescrip='Page 10 Market (Share) Growth'
acctlist=['acct_018AC','acct_018PYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_018PYE'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_018AC']-dfaccts['ACCT_018PYE']) / 
       dfaccts['ACCT_018PYE'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 41: Loan Growth - 025B(AC), 025B(PYE)
KPInum=41
KPIclass='Other Ratios'
KPIdescrip='Page 10 Loan Growth'
acctlist=['acct_025bAC','acct_025bPYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025BPYE'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_025BAC']-dfaccts['ACCT_025BPYE']) /
       dfaccts['ACCT_025BPYE'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)
#......................................................
# KPI 42: Asset Growth - 010(AC), 010(PYE)
KPInum=42
KPIclass='Other Ratios'
KPIdescrip='Page 10 Asset Growth'
acctlist=['acct_010AC','acct_010PYE']
dfaccts=KPIdfs(AC,acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010PYE'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_010AC']-dfaccts['ACCT_010PYE']) /
       dfaccts['ACCT_010PYE'])*100
dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
dfstats=KPI_stats(dfstats,dfaccts,KPIdescrip,KPInum,KPIclass)
#########################
print('Completed KPI',KPInum)

dfout=JoinKPI(KPInum,dfout,dfaccts,KPIclass,KPInamedict)
# Now write the output csv files.
dfout.to_csv(path_or_buf=outfile, index=False)
# For some reason, blank lines were added to the summary stats
# df. Remove them.
dfstats=dfstats.dropna(how='any')
dfstats.to_csv(path_or_buf=statsfile, index=False)
    