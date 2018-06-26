# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 13:19:35 2018

@author: Kim Earl Lowell
"""

#%%
# This file will extract the variables needed for a NCUA KPI, calculate the 
# KPI for all credit unions, then calculate the mean, standard deviation,
# and coefficient of variation for all CUs.
# Start with a very simple KPI: Capital Adequacy 1: Net Worth/Total assets:
#    ACCT_997/ACCT_010  (Files FS200A and FS220, respectively)
# Read the file that has information aobut which files have which ACCTs:
#################################################
# Function calcKPI accepts a list of ACCT codes and a dictionary indicating
# the FS files within which the ACCTs are found. It then returns a df having
# those accts for each credit union.
def KPIdfs(acctlist,acctdict):
    inpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/201703_Call-Report-Data/'
    prefix='201703_'
    inpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/201706_Call-Report-Data/'
    prefix='201706_'
    for i,acct in enumerate(acctlist):
        accttemp=acct
        filename=acctdict[accttemp][1]
# The following reads ACCTs whether they are Acct, ACCT, acct.
        try:
            dfin=pd.read_csv(inpath+prefix+filename+'.csv', 
                usecols=['CU_NUMBER',accttemp], skipinitialspace=True)
        except:
            try:
                accttemp=accttemp.upper()
                dfin=pd.read_csv(inpath+prefix+filename+'.csv', 
                     usecols=['CU_NUMBER',accttemp], skipinitialspace=True)
            except:
                accttemp=accttemp.replace('ACCT','Acct')
                dfin=pd.read_csv(inpath+prefix+filename+'.csv', 
                     usecols=['CU_NUMBER',accttemp], skipinitialspace=True)
# Make sure column names are standardised as ACCT_xxx.
        acctcolname=accttemp.upper()
        dfin.columns=['CU_NUMBER',acctcolname]
# Make the first variable the base dataframe.
        if i == 0:
            dfout=dfin
            continue
# Otherwise join the new dataframe.
        dfout=pd.merge(left=dfout, right=dfin, how='outer', left_on='CU_NUMBER',
               right_on='CU_NUMBER')
    return dfout
############################################################
# Function KPI_stats will calculate the mean, standasrd deviation, and
# coeff of variation of the KPI we've calculated, and append this
# informaiton to the output dataframe. 
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
    KPIindex=KPInum-1
    dfoutKPI=dfoutKPI.append(tempseries,ignore_index=True)
    dfoutKPI.ix[KPIindex,'KPI']= KPInum
    dfoutKPI.ix[KPIindex,'KPI_Class']= KPIclass
    dfoutKPI.ix[KPIindex,'KPI_Mean']= dfaccts['KPI'].mean()
    dfoutKPI.ix[KPIindex,'KPI_StDev']= dfaccts['KPI'].std()
    dfoutKPI.ix[KPIindex,'KPI_CV']= cvacct
    dfoutKPI.ix[KPIindex,'KPI_Count']=dfaccts['KPI'].count()
    dfoutKPI.ix[KPIindex,'KPI_Descrip']=descrip
    return dfoutKPI

############## MAIN BODY OF PROGRAM #############
import pandas as pd
# Set up input of dictionary file.  Dictionary will contain all ACCT-codes
# used in the KPIs as keys and the FS files in which they will be found as
# the look-up value.
# Set up output csv file for summary KPI info.
dfoutKPI=pd.DataFrame(columns=['KPI','KPI_Class','KPI_Mean','KPI_StDev',
                               'KPI_CV','KPI_Count','KPI_Descrip'],index=None)
KPIindex=0
inpath='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/'
#prefix='201703_'
prefix='201706_'
infile1='TargetKPI_TargetAccts.csv'
dfdict=pd.read_csv(inpath+prefix+infile1, usecols=['Account','AcctName','TableName'],
                   skipinitialspace=True)
# Eliminate duplicate lines. Because some ACCTs are sought in the previous year,
# we have to eliminate duplicates.
dfdict=dfdict.drop_duplicates()
# For ease of searching, make all accounts lowercase.
dfdict['Account']=dfdict['Account'].str.lower()
# Make first two characters of file lowercase.
dfdict['TableName']=dfdict['TableName'].str.replace('FS','fs')
# Create empty dictionary for ACCT/file informaiton.
acctdict={}
# Now loop through the file and set up the dictionary.
for i in range(dfdict.shape[0]):
    key=dfdict.iloc[i,0]
    keylist=[dfdict.iloc[i,1],dfdict.iloc[i,2]]
    acctdict[key]=keylist
# Dictionary now established.  Get KPIs.
#......................................................
# KPI 1: Capital Adequacy: Get data frame with desired ACCTs. 997, 010
KPInum=1
KPIclass='Capital Adequacy'
KPIdescrip='Page 1 Net Worth/Total Assets'
# The following should be lowercase.
acctlist=['acct_997','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
# Note everything is now upper case.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=dfaccts['ACCT_997']/dfaccts['ACCT_010']*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 2: Capital Adequacy: 041B/997
KPInum=2
KPIclass='Capital Adequacy'
KPIdescrip='Page 1 Total Delinquent Loans/Net Worth'
acctlist=['acct_041b','acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=dfaccts['ACCT_041B']/dfaccts['ACCT_997']*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 3: Solvency Evalaution (Estimated) 010,860c,925a,
# 825,668,820a,018
KPInum=3
KPIclass='Capital Adequacy'
KPIdescrip='Page 2 Solvency Evaluation (Estimated)'
acctlist=['acct_010','acct_860c','acct_925a','acct_825','acct_668',
       'acct_820a','acct_018']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_018'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_010']-(dfaccts['ACCT_860C']-dfaccts['ACCT_925A'])-
       dfaccts['ACCT_825']-dfaccts['ACCT_668']-dfaccts['ACCT_820A'])/
                dfaccts['ACCT_018'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 4: Classified Assets (Est.)/Net Worth 719, 668, 997
KPInum=4
KPIclass='Capital Adequacy'
KPIdescrip='Page 2 Classified Assets (Est.)/Net Worth'
acctlist=['acct_719','acct_668','acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_719']+dfaccts['ACCT_668'])/dfaccts['ACCT_997'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 5: Delinquent Loans/Total Loans  041B, 025B
KPInum=5
KPIclass='Asset Quality'
KPIdescrip='Page 2 Delinquent Loans/Total Loans'
acctlist=['acct_041b','acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041B']/dfaccts['ACCT_025B'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 6: Net Charge Offs/Average Loans - Required PYE/AC not used  550, 551, 025B
KPInum=6
KPIclass='Asset Quality'
KPIdescrip='Page 2 Net Charge Offs/Average Loans - Required PYE/AC not used'
acctlist=['acct_550','acct_551','acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550']-dfaccts['ACCT_551'])/dfaccts['ACCT_025B'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 7: Fair(Market) Value HTM Investment/Book Value HTM Investments 801, 796e
KPInum=7
KPIclass='Asset Quality'
KPIdescrip='Page 2 Fair(Market) Value HTM Investment/Book Value HTM Investments'
acctlist=['acct_801','acct_796e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_796E'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_801']/dfaccts['ACCT_796E'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 8: Accumulated Unrealized Gain/Loss... / Cost of Available for Sale... 945, 797e
KPInum=8
KPIclass='Asset Quality'
KPIdescrip='Page 2 Accumulated Unrealized Gain/Loss... / Cost of Available for Sale...'
acctlist=['acct_945','acct_797e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_797E']-dfaccts['ACCT_945'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_945']/(dfaccts['ACCT_797E']-dfaccts['ACCT_945']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 9: Delinquent Loans / Assets  041B, 010
KPInum=9
KPIclass='Asset Quality'
KPIdescrip='Page 3 Delinquent Loans / Assets'
acctlist=['acct_041b','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041B']/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 10: Return on Average Assets - Required PYE/AC not used  661A, 0101
KPInum=10
KPIclass='Earnings'
KPIdescrip='Page 3 Return on Average Assets - Required PYE/AC not used'
acctlist=['acct_661a','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_661A']/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 11: Return on Average Assets Before Stablisation - Required PYE/AC not used
#  660A, 010
KPInum=11
KPIclass='Earnings'
KPIdescrip='Page 3 Return on Average Assets Before Stablisation - Required PYE/AC not used'
acctlist=['acct_660a','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_660A']/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 12: Gross Income / Average Assets - Required PYE/AC not used
#  115, 131, 659, 010
KPInum=12
KPIclass='Earnings'
KPIdescrip='Page 3 Gross Income / Average Assets - Required PYE/AC not used'
acctlist=['acct_115','acct_131','acct_659','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_115']+dfaccts['ACCT_131']+dfaccts['ACCT_659'])/
       dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 13: Yield on Average Loans - Required PYE/AC not used
#  110, 119, 025b
KPInum=13
KPIclass='Earnings'
KPIdescrip='Page 3 Yield on Average Loans - Required PYE/AC not used'
acctlist=['acct_110','acct_119','acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_110']-dfaccts['ACCT_119'])/dfaccts['ACCT_025B'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 14: Yield on Average Investments - Required PYE/AC not used
#  120, 124, 799I, 730B, 730C
KPInum=14
KPIclass='Earnings'
KPIdescrip='Page 3 Yield on Average Investments - Required PYE/AC not used'
acctlist=['acct_120','acct_124','acct_799i','acct_730b','acct_730c']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+
                    dfaccts['ACCT_730C'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_120']+dfaccts['ACCT_124'])/
       (dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 15: Fee and Other Operating Income / Average Assets -
#  - Required PYE/AC not used 131, 659, 010
KPInum=15
KPIclass='Earnings'
KPIdescrip='Page 4 Fee and Other Operating Income / Average Assets  - Required PYE/AC not used'
acctlist=['acct_131','acct_659','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_131']+dfaccts['ACCT_659'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 16: Cost of Funds / Average Assets -
#  - Required PYE/AC not used 340, 380, 381, 010
KPInum=16
KPIclass='Earnings'
KPIdescrip='Page 4 Cost of Funds / Average Assets  - Required PYE/AC not used'
acctlist=['acct_340','acct_380','acct_381','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_340']+dfaccts['ACCT_380']+dfaccts['ACCT_381'])/
       dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 17: Net Margin / Average Assets -
#  - Required PYE/AC not used 115, 131,659, 350, 010
KPInum=17
KPIclass='Earnings'
KPIdescrip='Page 4 Net Margin / Average Assets  - Required PYE/AC not used'
acctlist=['acct_115','acct_131','acct_659','acct_350','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_115']+dfaccts['ACCT_131']+dfaccts['ACCT_659']-
       dfaccts['ACCT_350'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 18: Operating Expenses / Average Assets -
#  - Required PYE/AC not used 671, 010
KPInum=18
KPIclass='Earnings'
KPIdescrip='Page 5 Operating Expenses / Average Assets  - Required PYE/AC not used'
acctlist=['acct_671','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_671']/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 19: Provision for Loan & Lease Losses / Average Assets -
#  - Required PYE/AC not used 300, 010
KPInum=19
KPIclass='Earnings'
KPIdescrip='Page 5 Provision for Loan & Lease Losses / Average Assets  - Required PYE/AC not used'
acctlist=['acct_300','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_300']/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 20: Net Interest Margin / Average Assets -
#  - Required PYE/AC not used 115, 350, 010
KPInum=20
KPIclass='Earnings'
KPIdescrip='Page 5 Net Interest Margin / Average Assets  - Required PYE/AC not used'
acctlist=['acct_115','acct_350','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_115']-dfaccts['ACCT_350'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 21: Operating Expenses / Gross Income 671, 115, 131, 659
KPInum=21
KPIclass='Earnings'
KPIdescrip='Page 5 Operating Expenses / Gross Income'
acctlist=['acct_671','acct_115','acct_131','acct_659']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_115']+dfaccts['ACCT_131']+
                    dfaccts['ACCT_659'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_671']/(dfaccts['ACCT_115']+dfaccts['ACCT_131']+
       dfaccts['ACCT_659']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 22: Fixed Assets Including Foreclosed and... / Total Assets
# 007, 008, 798A, 980, 010
KPInum=22
KPIclass='Earnings'
KPIdescrip='Page 6 Fixed Assets Including Foreclosed and... / Total Assets'
acctlist=['acct_007','acct_008','acct_798a','acct_980','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_007']+dfaccts['ACCT_008']+
       dfaccts['ACCT_798A']+dfaccts['ACCT_980'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 23: Net Operating Expenses / Average Assets - Required PYE/AC not used
# 671, 131, 010
KPInum=23
KPIclass='Earnings'
KPIdescrip='Page 6 Net Operating Expenses / Average Assets - Required PYE/AC not used'
acctlist=['acct_671','acct_131','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_671']-dfaccts['ACCT_131'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 24: Net Long-term Assets / Total Assets
# 671, 131, 010
KPInum=24
KPIclass='Asset/Liability Management'
KPIdescrip='Page 7 Net Long-term Assets / Total Assets'
acctlist=['acct_703','acct_386','acct_712','acct_400t','acct_814e','acct_799c1',
          'acct_799c2','acct_799d','acct_007','acct_008','acct_718a','acct_794',
          'acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_703']+dfaccts['ACCT_386']-dfaccts['ACCT_712']+
       dfaccts['ACCT_400T']-dfaccts['ACCT_814E']+dfaccts['ACCT_799C1']+
       dfaccts['ACCT_799C2']+dfaccts['ACCT_799D']+dfaccts['ACCT_007']+
       dfaccts['ACCT_008']-dfaccts['ACCT_718A']+dfaccts['ACCT_794'])/
       dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 25: Regular Shares / Total Shares & Borrowings
# 657, 018, 860C, 781
KPInum=25
KPIclass='Asset/Liability Management'
KPIdescrip='Page 7 Regular Shares / Total Shares & Borrowings'
acctlist=['acct_657','acct_018','acct_860c','acct_781']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_018']+ dfaccts['ACCT_860C']+
                dfaccts['ACCT_781']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_657']/(dfaccts['ACCT_018']+dfaccts['ACCT_860C']+
       dfaccts['ACCT_781']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 26: Total Loans / Total Shares  025B, 018
KPInum=26
KPIclass='Asset/Liability Management'
KPIdescrip='Page 7 Total Loans / Total Shares'
acctlist=['acct_025b','acct_018']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_018'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_025B']/dfaccts['ACCT_018'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 27: Total Loans / Total Assets  025B, 010
KPInum=27
KPIclass='Asset/Liability Management'
KPIdescrip='Page 7 Total Loans / Total Assets'
acctlist=['acct_025b','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_025B']/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 28: Cash and Short-term Investments / Total Assets
# 730A, 730B, 730C, 799A1, 010
KPInum=28
KPIclass='Asset/Liability Management'
KPIdescrip='Page 8 Cash and Short-term Investments / Total Assets'
acctlist=['acct_730a','acct_730b','acct_730c','acct_799a1','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_730A']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']+
       dfaccts['ACCT_799A1'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 29: Total Shares, Deposits and Borrowings / Earning Assets
# 018, 860C, 781, 025B, 799I, 730B, 730C, 781
KPInum=29
KPIclass='Asset/Liability Management'
KPIdescrip='Page 8 Total Shares, Deposits and Borrowings / Earning Assets'
acctlist=['acct_018','acct_860c','acct_781','acct_025b','acct_799i',
          'acct_730b','acct_730c']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_025B']+ dfaccts['ACCT_799I']+
                dfaccts['ACCT_730B']+dfaccts['ACCT_730C']-dfaccts['ACCT_781']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_018']+dfaccts['ACCT_860C']-dfaccts['ACCT_781'])/
       (dfaccts['ACCT_025B']+ dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+
        dfaccts['ACCT_730C']-dfaccts['ACCT_781']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 30: Regular Shares and Share Drafts / Total Shares
# 902, 657, 018, 860C, 781
KPInum=30
KPIclass='Asset/Liability Management'
KPIdescrip='Page 8 Regular Shares and Share Drafts / Total Shares'
acctlist=['acct_902','acct_657','acct_018','acct_860c','acct_781']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_018']+dfaccts['ACCT_860C']-
                dfaccts['ACCT_781']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_902']+dfaccts['ACCT_657'])/
       (dfaccts['ACCT_018']+ dfaccts['ACCT_860C']-dfaccts['ACCT_781']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 31: Borrowing / Total Shares & Net Worth
# 860C, 781, 018, 997
KPInum=31
KPIclass='Asset/Liability Management'
KPIdescrip='Page 8 Borrowing / Total Shares & Net Worth'
acctlist=['acct_860c','acct_781','acct_018','acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_018']+dfaccts['ACCT_997']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_860C']+dfaccts['ACCT_781'])/
       (dfaccts['ACCT_018']+dfaccts['ACCT_997']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 32: Supervisory Interest Rate Risk Threshold / Net Worth
# 703, 799C2, 799D, 997
KPInum=32
KPIclass='Asset/Liability Management'
KPIdescrip='Page 8 Supervisory Interest Rate Risk Threshold / Net Worth'
acctlist=['acct_703','acct_799c2','acct_799d','acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_703']+dfaccts['ACCT_799C2']+
        dfaccts['ACCT_799D'])/dfaccts['ACCT_997'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 33: Members / Potential Members  083, 084
KPInum=33
KPIclass='Productivity'
KPIdescrip='Page 8 Members / Potential Members'
acctlist=['acct_083','acct_084']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_084'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_083']/dfaccts['ACCT_084'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 34: Borrowers / Members  025A, 083
KPInum=34
KPIclass='Productivity'
KPIdescrip='Page 9 Borrowers / Members'
acctlist=['acct_025a','acct_083']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_083'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_025A']/dfaccts['ACCT_083'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 35: Members /Full-time Employees  083, 564A, 564B
KPInum=35
KPIclass='Productivity'
KPIdescrip='Page 9 Members /Full-time Employees'
acctlist=['acct_083','acct_564a','acct_564b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_564A']+dfaccts['ACCT_564B']/2) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_083']/(dfaccts['ACCT_564A']+dfaccts['ACCT_564B']/2))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 36: Average Shares Per Member  018, 083
KPInum=36
KPIclass='Productivity'
KPIdescrip='Page 9 Average Shares Per Member'
acctlist=['acct_018','acct_083']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_083'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_018']/dfaccts['ACCT_083'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 37: Average Loan Balance  025B, 025A
KPInum=37
KPIclass='Productivity'
KPIdescrip='Page 9 Average Loan Balance'
acctlist=['acct_025b','acct_025a']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025A'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_025B']/dfaccts['ACCT_025A'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 38: Salary & Benefits / Full-time Employees  210, 564A, 564B
KPInum=38
KPIclass='Productivity'
KPIdescrip='Page 9 Salary & Benefits / Full-time Employees'
acctlist=['acct_210','acct_564a','acct_564b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_564A']+dfaccts['ACCT_564B']/2) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_210']/(dfaccts['ACCT_564A']+dfaccts['ACCT_564B']/2))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 39: Net Worth Growth - Required PYE/AC not used
# 997(AC), 997(PYE)
KPInum=39
KPIclass='Other Ratios'
KPIdescrip='Page 9 KEEP THIS ONE: Net Worth Growth - Required PYE/AC not used'
acctlist=['acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=999+((dfaccts['ACCT_997']-dfaccts['ACCT_997'])/dfaccts['ACCT_997'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 40: Market (Share) Growth - Required PYE/AC not used
# 018(AC), 018(PYE)
KPInum=40
KPIclass='Other Ratios'
KPIdescrip='Page 10 KEEP THIS ONE: Market (Share) Growth - Required PYE/AC not used'
acctlist=['acct_018']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_018'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=999+((dfaccts['ACCT_018']-dfaccts['ACCT_018'])/dfaccts['ACCT_018'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 41: Loan Growth - Required PYE/AC not used
# 025B(AC), 025B(PYE)
KPInum=41
KPIclass='Other Ratios'
KPIdescrip='Page 10 KEEP THIS ONE: Loan Growth - Required PYE/AC not used'
acctlist=['acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=999+((dfaccts['ACCT_025B']-dfaccts['ACCT_025B'])/dfaccts['ACCT_025B'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 42: Asset Growth - Required PYE/AC not used
# 010(AC), 010(PYE)
KPInum=42
KPIclass='Other Ratios'
KPIdescrip='Page 10 KEEP THIS ONE: Asset Growth - Required PYE/AC not used'
acctlist=['acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=999+((dfaccts['ACCT_010']-dfaccts['ACCT_010'])/dfaccts['ACCT_010'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 43: Investment Growth - Required PYE/AC not used
KPInum=43
KPIclass='Other Ratios'
KPIdescrip='Page 10 KEEP THIS ONE: Investment Growth - Required PYE/AC not used'
acctlist=['acct_799i','acct_730b','acct_730c','acct_781']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+
                    dfaccts['ACCT_730C']-dfaccts['ACCT_781']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']-
        dfaccts['ACCT_781'])-
        (dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']-
         dfaccts['ACCT_781'])/
        (dfaccts['ACCT_799I']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']-
         dfaccts['ACCT_781']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 44: Membership Growth - Required PYE/AC not used
# 083
KPInum=44
KPIclass='Other Ratios'
KPIdescrip='Page 10 KEEP THIS ONE: Membership Growth - Required PYE/AC not used'
acctlist=['acct_083']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_083'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=999+((dfaccts['ACCT_083']-dfaccts['ACCT_083'])/dfaccts['ACCT_083'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 45: Credit Cards Delinquent >= 2 Months (60 days) / Total Leases Receivable
# 045B 396
KPInum=45
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 11 Credit Cards Delinquent >= 2 Months (60 days) / Total Leases Receivable'
acctlist=['acct_045b','acct_396']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_396'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_045B']/dfaccts['ACCT_396'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 46: Leases Receivable Delinquent >= 2 Months(60 days) / Total Leases Receivable
# 041D 002
KPInum=46
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 11 Leases Receivable Delinquent >= 2 Months(60 days) / Total Leases Receivable'
acctlist=['acct_041d','acct_002']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_002'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041D']/dfaccts['ACCT_002'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 47: Non-federally Guaranteed Student Loans >= 2 Months(60 Days) /
# Total Non-federally Guaranteed Student Loans
# 041T 698A
KPInum=47
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 11 Non-federally Guaranteed Student Loans >= 2 Months(60 Days) / Total Non-federally Guaranteed Student Loans'
acctlist=['acct_041t','acct_698a']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_698A'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041T']/dfaccts['ACCT_698A'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 48: New Vehicle Loans >= 2 Months(60 Days) / Total New Vehicle Loans
# 041C1 385
KPInum=48
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 11 New Vehicle Loans >= 2 Months(60 Days) / Total New Vehicle Loans'
acctlist=['acct_041c1','acct_385']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_385'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041C1']/dfaccts['ACCT_385'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 49: Used Vehicle Loans >= 2 Months(60 Days) / Total Used Vehicle Loans
# 041C2 370  NOTE: THIS IS ERRONEOUSLY DEFINED IN THE NCUA KPI DOCUMENT AS
# USING 042C2 -- WHICH DOES NOT EXIST. 
KPInum=49
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 11 ERRONEOUSLY DEFINED IN NCUA DOC: Used Vehicle Loans >= 2 Months(60 Days) / Total Used Vehicle Loans'
acctlist=['acct_041c2','acct_370']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_370'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041C2']/dfaccts['ACCT_370'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 50: Total Vehicle Loans >= 2 Months(60 Days) / Total Vehicle Loans
# 041C1 042C2 385 370  NOTE: THIS IS ERRONEOUSLY DEFINED IN THE NCUA KPI 
# DOCUMENT AS USING 042C2 -- WHICH DOES NOT EXIST.
KPInum=50
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 12 Total Vehicle Loans >= 2 Months(60 Days) / Total Vehicle Loans'
acctlist=['acct_041c1','acct_041c2','acct_385','acct_370']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_370']+dfaccts['ACCT_385']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_041C2']+dfaccts['ACCT_041C2'])/
       (dfaccts['ACCT_370']+dfaccts['ACCT_370']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 51: TDR Consumer Loans Not Secured by Real Estate >=2 months (60 days)/
# Total TDR Consumer Loans Not Secured by Real Estate   041X 1011D
KPInum=51
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 12 TDR Consumer Loans Not Secured by Real Estate >=2 months (60 days)/Total TDR Consumer Loans Not Secured by Real Estate'
acctlist=['acct_041x','acct_1011d']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_1011D'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041X']/dfaccts['ACCT_1011D'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 52: Indirect Loans Delinquent >=2 months (60 days)/ Indirect Loans
# 041E  618A
KPInum=52
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 12 Indirect Loans Delinquent >=2 months (60 days)/ Indirect Loans'
acctlist=['acct_041e','acct_618a']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_618A'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041E']/dfaccts['ACCT_618A'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 53: Participation Loans Delinquent >=2 months (60 days)/ Participation Loans
# 041F 619B 691E
KPInum=53
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 12 Participation Loans Delinquent >=2 months (60 days)/ Participation Loans'
acctlist=['acct_041f','acct_619b','acct_691e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_619B']+dfaccts['ACCT_691E']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041F']/(dfaccts['ACCT_619B']+dfaccts['ACCT_691E']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 54: Business Loans Delinquent >=1 month (30 days)/ Total Business Loans
# 020G1 020G2 020P1 020P2 041G1 041G2 041P1 041P2 400T 814E
KPInum=54
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 12-13 Business Loans Delinquent >= 1 month (30 days)/ Total Business Loans'
acctlist=['acct_020g1','acct_020g2','acct_020p1','acct_020p2','acct_041g1',
          'acct_041g2','acct_041p1','acct_041p2','acct_400t','acct_814e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_400T']+dfaccts['ACCT_814E']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_020G1']+dfaccts['ACCT_020G2']+dfaccts['ACCT_020P1']+
       dfaccts['ACCT_020P2']+dfaccts['ACCT_041G1']+dfaccts['ACCT_041G2']+
       dfaccts['ACCT_041P1']+dfaccts['ACCT_041P2'])/
       (dfaccts['ACCT_400T']+dfaccts['ACCT_814E']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 55: Business Loans Delinquent >=2 months (60 days)/ Total Business Loans
# 041G1 041G2 041P1 041P2 400T 814E
KPInum=55
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 14 Business Loans Delinquent >= 2 months (60 days)/ Total Business Loans'
acctlist=['acct_041g1','acct_041g2','acct_041p1','acct_041p2','acct_400t',
          'acct_814e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_400T']+dfaccts['ACCT_814E']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_041G1']+dfaccts['ACCT_041G2']+dfaccts['ACCT_041P1']+
       dfaccts['ACCT_041P2'])/(dfaccts['ACCT_400T']+dfaccts['ACCT_814E']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 56: TDR Business Loans Not Secured by Real Estate >=2 months (60 days)/ 
# Total TDR Business Loans Not Secured by Real Estate
# 041Y 1011E
KPInum=56
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 14 TDR Business Loans Not Secured by Real Estate >=2 months (60 days) / Total TDR Business Loans Not Secured by Real Estate'
acctlist=['acct_041y','acct_1011e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_1011E'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041Y']/dfaccts['ACCT_1011E'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 57: Loans Held For Sale Delinquent >=2 months (60 days) /
# Total Loans Held For Sale 071J 003
KPInum=57
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 14 Loans Held For Sale Delinquent >=2 months (60 days) / Total Loans Held For Sale'
acctlist=['acct_071j','acct_003']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_003'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_071J']/dfaccts['ACCT_003'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 58: Allowance for Loan and Lease Losses / Delinquent Loans 0719 041B
KPInum=58
KPIclass='Other Delinquency Ratios'
KPIdescrip='Page 15 Allowance for Loan and Lease Losses / Delinquent Loans'
acctlist=['acct_719','acct_041b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_041B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_719']/dfaccts['ACCT_041B'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 59: First Mortgage Fixed/Hybrid/Balloon Loans Delinquent 
# >=2 months (60 days) / Total First Mortgage Fixed/Hybrid/Balloon Loans
# 713A 704A 704B 704C 704D 704E
KPInum=59
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 15 First Mortgage Fixed/Hybrid/Balloon Loans Delinquent >=2 months (60 days) / Total First Mortgage Fixed/Hybrid/Balloon Loans'
acctlist=['acct_713a','acct_704a','acct_704b','acct_704c','acct_704d',
          'acct_704e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_704A']+dfaccts['ACCT_704B']+
         dfaccts['ACCT_704C']+dfaccts['ACCT_704D']+dfaccts['ACCT_704E']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_713A']/(dfaccts['ACCT_704A']+dfaccts['ACCT_704B']+
         dfaccts['ACCT_704C']+dfaccts['ACCT_704D']+dfaccts['ACCT_704E']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 60: First Mortgage Adjustable Rate Loans Delinquent >= 2 months
# (60 days)/ Total First Mortgage Adjustable Rate Loans  714A 705A 705B 704D
KPInum=60
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 15 First Mortgage Adjustable Rate Loans Delinquent >= 2 months (60 days)/ Total First Mortgage Adjustable Rate Loans'
acctlist=['acct_714a','acct_705a','acct_705b','acct_704d']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_705A']+dfaccts['ACCT_705B']+
         dfaccts['ACCT_704D']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_714A']/(dfaccts['ACCT_705A']+dfaccts['ACCT_705B']+
         dfaccts['ACCT_704D']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)

#......................................................
# KPI 61: Other Real Estate Fixed/Hybrid/Balloon Loans Delinquent 
# >=2 months (60 days) / Total Other Real Estate Fixed/Hybrid/Balloon Loans
# 715A 706 708B
KPInum=61
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 15 Other Real Estate Fixed/Hybrid/Balloon Loans Delinquent >=2 months (60 days) / Total Other Real Estate Fixed/Hybrid/Balloon Loans'
acctlist=['acct_715a','acct_706','acct_708b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_706']+dfaccts['ACCT_708B']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_715A']/(dfaccts['ACCT_706']+dfaccts['ACCT_708B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 62: Other Real Estate Adjustable Rate Loans Delinquent 
# >=2 months (60 days) / Total Other Real Estate Adjustable Rate Loans
# 716A 707 708
KPInum=62
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 16 Other Real Estate Adjustable Rate Loans Delinquent >=2 months (60 days) / Total Other Real Estate Adjustable Rate Loans'
acctlist=['acct_716a','acct_707','acct_708']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_707']+dfaccts['ACCT_708']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_716A']/(dfaccts['ACCT_707']+dfaccts['ACCT_708']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 63: Interest Only and Payment Option First & Other RE Loans Delinquent 
# >=2 months (60 days) / Total Interest Only and Payment Option First & Other RE Loans
# 041I 041M 704C1 704D2
KPInum=63
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 16 Interest Only and Payment Option First & Other RE Loans Delinquent >=2 months (60 days) / Total Interest Only and Payment Option First & Other RE Loans'
acctlist=['acct_041i','acct_041m','acct_704c1','acct_704d2']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_704C1']+dfaccts['ACCT_704D2']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_041I']+dfaccts['ACCT_041M'])/
       (dfaccts['ACCT_704C1']+dfaccts['ACCT_704D2']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 64: TDR Real Estate Loans Delinquent >=2 months (60 days) / Total TDR RE Loans
# 041U 041V 1011A 1011B
KPInum=64
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 16 TDR Real Estate Loans Delinquent >=2 months (60 days) / Total TDR RE Loans'
acctlist=['acct_041u','acct_041v','acct_1011a','acct_1011b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_1011A']+dfaccts['ACCT_1011B']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_041U']+dfaccts['ACCT_041V'])/
       (dfaccts['ACCT_1011A']+dfaccts['ACCT_1011B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 65: TDR Real Estate Loans Also MBL Delinquent >=2 months (60 days) / 
# Total TDR Loans Also MBL  041W 1011C
KPInum=65
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 16 TDR Real Estate Loans Also MBL Delinquent >=2 months (60 days) / Total TDR Loans Also MBL'
acctlist=['acct_041w','acct_1011c']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_1011C'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_041W']/dfaccts['ACCT_1011C'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 66: Total Real Estate Loans Delinquent >=1 month (30 days) / 
# Total Real Estate Loans  713A 714A 715A 716A 751 771 755 775 710
KPInum=66
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 16 Total Real Estate Loans Delinquent >=1 months (30 days) / Total Real Estate Loans'
acctlist=['acct_713a','acct_714a','acct_715a','acct_716a','acct_751'
          ,'acct_771','acct_755','acct_775','acct_710']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_710'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_713A']+dfaccts['ACCT_714A']+dfaccts['ACCT_715A']+
       dfaccts['ACCT_716A']+dfaccts['ACCT_751']+dfaccts['ACCT_771']+
              dfaccts['ACCT_755']+dfaccts['ACCT_775'])/dfaccts['ACCT_710'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 67: Total Real Estate Loans Delinquent >=2 months (60 days) / 
# Total Real Estate Loans  713A 714A 715A 716A 710
KPInum=67
KPIclass='Real Estate Loan Delinquency'
KPIdescrip='Page 17 Total Real Estate Loans Delinquent >=2 months (30 days) / Total Real Estate Loans'
acctlist=['acct_713a','acct_714a','acct_715a','acct_716a','acct_710']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_710'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_713A']+dfaccts['ACCT_714A']+dfaccts['ACCT_715A']+
       dfaccts['ACCT_716A'])/dfaccts['ACCT_710'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 68: Charge Offs Due to Bankruptcy (YTD) / Total Charge Offs  682 550
KPInum=68
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 17 Charge Offs Due to Bankruptcy (YTD) / Total Charge Offs'
acctlist=['acct_682','acct_550']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_550'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=(dfaccts['ACCT_682']/dfaccts['ACCT_550'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 69: Net Charge Offs - Credit Cards / Average Credit Cards -- Required
# PYE/AC not used 680 681 396
KPInum=69
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 17 Net Charge Offs - Credit Cards / Average Credit Cards -- Required PYE/AC not used'
acctlist=['acct_680','acct_681','acct_396']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_396'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_680']+dfaccts['ACCT_681'])/dfaccts['ACCT_396'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 70: Net Charge Offs Non-federally Guaranteed Student Loans / Average 
# Non-federally Guaranteed Student Loans -- Required PYE/AC not used
# 550T 551T 698A
KPInum=70
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 17 Net Charge Offs Non-federally Guaranteed Student Loans / Average Non-federally Guaranteed Student Loans -- Required PYE/AC not used'
acctlist=['acct_550t','acct_551t','acct_698a']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_698A'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550T']-dfaccts['ACCT_551T'])/dfaccts['ACCT_698A'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 71: Net Charge Offs -- Total Vehicle Loans / Avg Total Vehicle Loans
# -- Required PYE/AC not used  550C1 550C2 551C1 551C2 385 370
# NOTE: THIS IS ERRONEOUSLY DEFINED IN THE NCUA KPI DOCUMENT AS
# USING 552C2 -- WHICH DOES NOT EXIST. 
KPInum=71
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 18 ERRONEOUSLY DEFINED IN NCUA DOC: Net Charge Offs -- Total Vehicle Loans / Avg Total Vehicle Loans -- Required PYE/AC not used'
acctlist=['acct_550c1','acct_550c2','acct_551c1','acct_551c2',
          'acct_385','acct_370']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_385']+dfaccts['ACCT_370']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550C1']+dfaccts['ACCT_550C2']-dfaccts['ACCT_551C1']
        -dfaccts['ACCT_551C2'])/(dfaccts['ACCT_385']+dfaccts['ACCT_370']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 72: Net Charge Offs -- Total Real Estate Loans / Avg Total Real Estate Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=72
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 18 Net Charge Offs -- Total Real Estate Loans / Avg Total Real Estate Loans -- Required PYE/AC not used'
acctlist=['acct_549','acct_548','acct_608','acct_607','acct_710']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_710'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_549']+dfaccts['ACCT_548']-dfaccts['ACCT_608']
        -dfaccts['ACCT_607'])/dfaccts['ACCT_710'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 73: Net Charge Offs -- First Mortgage Loans / Avg Total Real Estate Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=73
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 18 Net Charge Offs -- First Mortgage Loans / Avg First Mortgage Loans -- Required PYE/AC not used'
acctlist=['acct_548','acct_607','acct_703']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_703'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_548']-dfaccts['ACCT_607'])/dfaccts['ACCT_703'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 74: Net Charge Offs -- Other Real Estate Loans / Avg Other Real Estate Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=74
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 18 Net Charge Offs -- Other Real Estate Loans / Avg Other Real Estate Loans -- Required PYE/AC not used'
acctlist=['acct_549','acct_608','acct_386']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_386'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_549']-dfaccts['ACCT_608'])/dfaccts['ACCT_386'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 75: Net Charge Offs -- Interest Only and Payment Option First &
# Other RE Loans / Avg Interest Only and Payment Option First & Other RE Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=75
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 18 Net Charge Offs -- Interest Only and Payment Option First & Other RE Loans / Avg Interest Only and Payment Option First & Other RE Loans -- Required PYE/AC not used -- Required PYE/AC not used'
acctlist=['acct_550i','acct_551i','acct_550m','acct_551m',
        'acct_704c1','acct_704d2']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_704C1']+dfaccts['ACCT_704D2']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550I']-dfaccts['ACCT_551I'])+
       (dfaccts['ACCT_550M']-dfaccts['ACCT_551M'])/
       (dfaccts['ACCT_704C1']+dfaccts['ACCT_704D2']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 76: Net Charge Offs -- Leases Receivable / Avg Leases Receivable
# -- Required PYE/AC not used  549 548 608 607
KPInum=76
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 18 Net Charge Offs -- Leases Receivable / Avg Leases Receivable -- Required PYE/AC not used'
acctlist=['acct_550d','acct_551d','acct_002']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_002'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550D']-dfaccts['ACCT_551D']) /
       dfaccts['ACCT_002'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 77: Net Charge Offs -- Indirect Loans / Indirect Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=77
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 19 Net Charge Offs -- Indirect Loans / Avg Indirect Loans -- Required PYE/AC not used'
acctlist=['acct_550e','acct_551e','acct_618a']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_618A'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550E']-dfaccts['ACCT_551E']) /
       dfaccts['ACCT_618A'])*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 78: Net Charge Offs -- Participation Loans / Average Participation Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=78
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 20 Net Charge Offs -- Participation Loans / Average Participation Loans -- Required PYE/AC not used'
acctlist=['acct_550f','acct_551f','acct_619b','acct_691e']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_619B']+dfaccts['ACCT_691E']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550F']-dfaccts['ACCT_551F']) /
       (dfaccts['ACCT_619B']+dfaccts['ACCT_691E']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 79: Net Charge Offs -- Business Loans / Average Business Loans
# -- Required PYE/AC not used  549 548 608 607
KPInum=79
KPIclass='Miscellaneous Loan Loss Ratios'
KPIdescrip='Page 20-21 Net Charge Offs -- Business Loans / Average Business Loans -- Required PYE/AC not used'
acctlist=['acct_550g1','acct_550g2','acct_550p1','acct_550p2',
          'acct_551g1','acct_551g2','acct_551p1','acct_551p2',
          'acct_400t','acct_814e',]
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[(dfaccts['ACCT_400T']-dfaccts['ACCT_814E']) == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_550G1']+dfaccts['ACCT_550G2']+dfaccts['ACCT_550P1']+
       dfaccts['ACCT_550P2']-dfaccts['ACCT_551G1']-dfaccts['ACCT_551G2']-
              dfaccts['ACCT_551P1']-dfaccts['ACCT_551P2']) /
       (dfaccts['ACCT_400T']-dfaccts['ACCT_814E']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 80: Specialized Lending Ratios: Indirect Loans Outstanding/Total Loans 
# 618A, 025B- 3/31/04 Forward 
KPInum=80
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 21 Indirect Loans Outstanding/Total Loans'
acctlist=['acct_618a','acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_618A'])/(dfaccts['ACCT_025B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 81: Specialized Lending Ratios: Participation Loans Outstanding/Total Loans 
# 619B, 691E, 025B- 3/31/09 Forward 
KPInum=81
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 21 Participation Loans Outstanding/Total Loans'
acctlist=['acct_619b','acct_691e','acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_619B']+dfaccts['ACCT_691E'])/(dfaccts['ACCT_025B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 82: Specialized Lending Ratios: Participation Loans Purchased YTD/Total Loans Granted YTD
# 690, 031b- 3/31/03 Forward # ANNUALIZED 
KPInum=82
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 22 Participation Loans Purchased YTD/Total Loans Granted YTD'
acctlist=['acct_690','acct_031b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_031B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_690'])/(dfaccts['ACCT_031B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 83: Specialized Lending Ratios: Participation Loans Sold YTD/Total Assets
# 691, 010- 3/31/03 Forward # ANNUALIZED 
KPInum=83
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 22 Participation Loans Sold YTD/Total Assets'
acctlist=['acct_691','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_691'])/(dfaccts['ACCT_010']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 84: Specialized Lending Ratios: Total Business Loans (NMBLB) Less Unfunded Commitments/Assets
# 400T, 814E, 010- 3/31/11 Forward 
KPInum=84
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 22 Total Business Loans (NMBLB) Less Unfunded Commitments/Assets'
acctlist=['acct_400t','acct_814e','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_400T']-dfaccts['ACCT_814E'])/(dfaccts['ACCT_010']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 85: Specialized Lending Ratios: Loans Purchased From Other Financial Institutions and Other Sources YTD/Loans Granted YTD
# 615, 613, 31B- 3/31/11 Forward 
KPInum=85
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 22 Loans Purchased From Other Financial Institutions and Other Sources YTD/Loans Granted YTD'
acctlist=['acct_615','acct_613', 'acct_031b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_031B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_615']+dfaccts['ACCT_613'])/(dfaccts['ACCT_031B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 86: Specialized Lending Ratios: Non-Federally Guaranteed student loans in Deferral Status/Totl Non-Federally Guaranteed Student Loans
# 698a, 698b- 6/30/13 Forward 
KPInum=86
KPIclass='Specialized Lending Ratios'
KPIdescrip='Page 23 Non-Federally Guaranteed student loans in Deferral Status/Totl Non-Federally Guaranteed Student Loans'
acctlist=['acct_698a','acct_698b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_698A'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_698B'])/(dfaccts['ACCT_698A']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 87: Real Estate Lending Ratios: Total Fixed Rate Real Estate Loans/Total Assets
# 704A, 704B, 704C, 704E, 706, 708B, 010- 3/31/08 Forward 
KPInum=87
KPIclass='Real Estate Lending Ratios'
KPIdescrip='Page 23 Total Fixed Rate Real Estate Loans/Total Assets'
acctlist=['acct_704a','acct_704b','acct_704c', 'acct_704e', 'acct_706', 'acct_708b', 'acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_704A']+dfaccts['ACCT_704B']+dfaccts['ACCT_704C']+dfaccts['ACCT_704E']+dfaccts['ACCT_706']+dfaccts['ACCT_708B'])/(dfaccts['ACCT_010']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 88: Real Estate Lending Ratios: Total Fixed Rate Real Estate Loans/Total Loans
# 704A, 704B, 704C, 704E, 706, 708B, 025B- 3/31/08 Forward 
KPInum=88
KPIclass='Real Estate Lending Ratios'
KPIdescrip='Page 23 Total Fixed Rate Real Estate Loans/Total Loans'
acctlist=['acct_704a','acct_704b','acct_704c', 'acct_704e', 'acct_706', 'acct_708b', 'acct_025b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_025B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_704A']+dfaccts['ACCT_704B']+dfaccts['ACCT_704C']+dfaccts['ACCT_704E']+dfaccts['ACCT_706']+dfaccts['ACCT_708B'])/(dfaccts['ACCT_025B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 89: Real Estate Lending Ratios: Total Fixed Rate Real Estate Loans Granted YTD/Total Loans Granted YTD
# 720A, 720B, 720C, 720E, 722, 724B, 031B- 3/31/08 Forward 
KPInum=89
KPIclass='Real Estate Lending Ratios'
KPIdescrip='Page 24 Total Fixed Rate Real Estate Loans Granted YTD/Total Loans Granted YTD'
acctlist=['acct_031b','acct_720a','acct_720b', 'acct_720c', 'acct_720d', 'acct_720e', 'acct_722', 'acct_724b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_031B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_720A']+dfaccts['ACCT_720B']+dfaccts['ACCT_720C']+dfaccts['ACCT_720D']+dfaccts['ACCT_720E']+dfaccts['ACCT_722']+dfaccts['ACCT_724B'])/(dfaccts['ACCT_031B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 90: Real Estate Lending Ratios: First Mortgage Real Estate Loans Sold YTD/First Mortgage Real Estate Loans Granted YTD
# 736,720A, 720B, 720C, 720E, 721A, 721B- 3/31/04 Forward 
KPInum=90
KPIclass='Real Estate Lending Ratios'
KPIdescrip='Page 24 First Mortgage Real Estate Loans Sold YTD/First Mortgage Real Estate Loans Granted YTD'
acctlist=['acct_736','acct_720a','acct_720b', 'acct_720c', 'acct_720d', 'acct_720e', 'acct_721a', 'acct_721b']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_720A']+dfaccts['ACCT_720B']+dfaccts['ACCT_720C']+dfaccts['ACCT_720D']+dfaccts['ACCT_720E']+dfaccts['ACCT_721A']+dfaccts['ACCT_721B'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_736'])/(dfaccts['ACCT_720A']+dfaccts['ACCT_720B']+dfaccts['ACCT_720C']+dfaccts['ACCT_720D']+dfaccts['ACCT_720E']+dfaccts['ACCT_721A']+dfaccts['ACCT_721B']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 91: Real Estate Lending Ratios: Interest Only and Payment Options First & Other Re/Total Assets
# 704C1, 704D2, 010- 3/31/09 Forward 
KPInum=91
KPIclass='Real Estate Lending Ratios'
KPIdescrip='Page 24 Interest Only and Payment Option First & Other RE/Total Assets'
acctlist=['acct_704c1','acct_704d2','acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_704C1']+dfaccts['ACCT_704D2'])/(dfaccts['ACCT_010']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 92: Real Estate Lending Ratios: Interest Only and Payment Options First & Other Re/Net Worth 
# 704C1, 704D2, 997- 3/31/09 Forward 
KPInum=92
KPIclass='Real Estate Lending Ratios'
KPIdescrip='Page 24 Interest Only and Payment Option First & Other RE/Net Worth'
acctlist=['acct_704c1','acct_704d2','acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_704C1']+dfaccts['ACCT_704D2'])/(dfaccts['ACCT_997']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 93: Miscellaneous Ratios: Mortgage Servicing Rights/Net Worth
# 779, 997 - 3/31/03 Forward 
KPInum=93
KPIclass='Miscellaneous Ratios'
KPIdescrip='Page 24 Mortgage Servicing Rights/Net Worth'
acctlist=['acct_779','acct_997']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_997'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_779'])/(dfaccts['ACCT_997']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 94: Miscellaneous Ratios: Unused Commitments/Cash & Short Term Investments
# 816A, 730A, 730B, 730C, 799A1 - 3/31/10 Forward 
KPInum=94
KPIclass='Miscellaneous Ratios'
KPIdescrip='Page 25 Unused Commitments/Cash & Short Term Investments'
acctlist=['acct_816a','acct_730a', 'acct_730b', 'acct_730c', 'acct_799a1']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_730A']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']+dfaccts['ACCT_799A1'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_816A'])/(dfaccts['ACCT_730A']+dfaccts['ACCT_730B']+dfaccts['ACCT_730C']+dfaccts['ACCT_799A1']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 95: Miscellaneous Ratios: Complex Assets/Total Assets
# 705A, 705B, 707, 708, 704C, 704D, 732, 733, 733A, 010 - 3/31/08 Forward
KPInum=95
KPIclass='Miscellaneous Ratios'
KPIdescrip='Page 25 Complex Assets/Total Assets'
acctlist=['acct_705a','acct_705b', 'acct_707', 'acct_708', 'acct_704c', 'acct_704d', 'acct_742c2', 'acct_981', 'acct_010']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_010'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_705A']+dfaccts['ACCT_705B']+dfaccts['ACCT_707']+
       dfaccts['ACCT_708']+dfaccts['ACCT_704C']+dfaccts['ACCT_704D']+
       dfaccts['ACCT_742C2']+dfaccts['ACCT_981'])/(dfaccts['ACCT_010']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)
#......................................................
# KPI 96: Miscellaneous Ratios: Short Term Liabilities/Total Shares, Deposits,
# Borrowings ACCT_A908A+ACCT_A906A+ACCT_A630A+ACCT_A880A+ACCT_A058A+ACCT_A867A+
#ACCT_A011A+ACCT_A8838A+ACCT_A911/ACCT_A018+ACCT_A860C-ACCT_A781.- 3/31/05 Forward
# NOTE: THIS IS ERRONEOUSLY DEFINED IN THE NCUA KPI DOCUMENT AS USING (FOR
# EXAMPLE A908A, A906A, ETC. -- WHICH DO NOT EXIST.
KPInum=96
KPIclass='Miscellaneous Ratios'
KPIdescrip='Page 25 ERRONEOUSLY DEFINED IN NCUA DOC: Short Term Liabilities/Total Shares, Deposits, Borrowings'
acctlist=['acct_908a','acct_906a', 'acct_630a', 'acct_880a', 'acct_058a', 
          'acct_867a', 'acct_011a', 'acct_883a', 'acct_911', 'acct_018',
          'acct_860c', 'acct_781']
dfaccts=KPIdfs(acctlist,acctdict)
# Protect against division by zero -- drop rows if denominator = 0.
dfaccts = dfaccts.drop(dfaccts[dfaccts['ACCT_018']+dfaccts['ACCT_860C']+
                               dfaccts['ACCT_781'] == 0].index)
# NOTE: Returned dataframe has capital ACCTs as columns.
dfaccts['KPI']=((dfaccts['ACCT_908A']+dfaccts['ACCT_906A']+
       dfaccts['ACCT_630A']+dfaccts['ACCT_880A']+dfaccts['ACCT_058A']+
       dfaccts['ACCT_867A']+dfaccts['ACCT_011A']+dfaccts['ACCT_883A']+
       dfaccts['ACCT_911'])/(dfaccts['ACCT_018']+dfaccts['ACCT_860C']-
        dfaccts['ACCT_781']))*100
dfoutKPI=KPI_stats(dfoutKPI,dfaccts,KPIdescrip,KPInum,KPIclass)


outfile='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/201706_KPI_Stats.csv'
dfoutKPI.to_csv(path_or_buf=outfile, index=False)
# Now write an Excel workbook with colours for sparse data.
outfile='C:/Analytics/DATA911/Arkatechture/NCUA_Data/NCUA_Data_Final/201706_KPI_Stats'
outfile= pd.ExcelWriter(outfile+'.xlsx', engine='xlsxwriter')
# Worksheet will be called KPIs
dfoutKPI.to_excel(outfile,'KPIs',index=False)
# Customise output by highlighting in red variable with more than thresh
# percent of NA and zero combined.
workbook = outfile.book
worksheet = outfile.sheets['KPIs']
format1 = workbook.add_format({'bg_color': 'red'})
format2 = workbook.add_format({'bg_color': 'yellow'})
# Color CV cells if variability is "low" (CVthresh <= somevalue)
color_range = "E2:E{}".format(KPInum+1)
CVthresh=50
worksheet.conditional_format(color_range, {'type': 'cell',
            'criteria': '<','value':CVthresh,'format': format1})
# Color COUNT cells if number/count is "low" (countthresh <= somevalue)
color_range = "F2:F{}".format(KPInum+1)
countthresh=5000
worksheet.conditional_format(color_range, {'type': 'cell',
            'criteria': '<','value':countthresh,'format': format2})
outfile.save()
    