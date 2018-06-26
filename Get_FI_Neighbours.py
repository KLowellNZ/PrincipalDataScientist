# -*- coding: utf-8 -*-
"""
Created on Tue May  1 19:51:13 2018

@author: Kim Earl Lowell
"""

#%%
# This program reads information for banks and credit unions, and for each
# financial institution, it adds the two "closest" banks and two closest
# CU based on Deposits and Loans_and Leases in feature space.
######################### getclosetsFIs #####################################
# This function accepts three dfs for a particular sate. The first is all
# the FIs for the state, the second is the df for which neighbours are
# sought, and the third is the df from which neighbours are sought. The
# prefix passed is CU_Neigh or Bank_Neigh for variable naming. The two closest
# neighbours based on and Deposits and Loans_and_Leases are added.
def getclosestFIs(varprefix,dfFI,dfFI1,dfFI2):
# Keep original index for restoring original order later. Then reset the
# index. Because dfFI1 might be the same as dfFI2, create copy and work on
# that.
    dfFI3=dfFI2
    dfFI1=dfFI1.reset_index(drop=True)
    dfFI3=dfFI3.reset_index(drop=True)
#    print('dfCU\n',dfCU,'\ndfbank\n',dfbank)
# Now set up empty dataframes for filling. First row has a distance of zero 
# since the distance of an FI from itselef is zero.
    dfFIdist=pd.DataFrame(columns=['Name','FI_dist'])
#    dfbankdist=pd.DataFrame([dfbank.ix[0,'Name'],0],columns=['Name','CU_dist'])
    for i in range(dfFI1.shape[0]):
# Calculate distance to all neighbours from the ith FI and append to new 
# df dfCUdist.
        dfFIdist=pd.DataFrame(columns=['Name','FI_dist'])
        for j in range(dfFI3.shape[0]):
            dftemp=pd.DataFrame([[dfFI1.ix[0,'Name'],0]],columns=['Name','FI_dist'])
            dftemp.iloc[0,0]=dfFI3.ix[j,'Name']
# Scale values because they are causing memory overflow.
            X1 = dfFI1.ix[i,'Deposits']/100000
            X2 = dfFI3.ix[j,'Deposits']/100000
            Y1 = dfFI1.ix[i,'Loans_Leases']/100000
            Y2 = dfFI3.ix[j,'Loans_Leases']/100000
            dftemp.iloc[0,1]=((X1-X2)**2 + (Y1-Y2)**2)**0.5
#            dftemp.iloc[0,1]=((dfFI1.ix[i,'Deposits']-dfFI3.ix[j,'Deposits'])**2 +
#                 (dfFI1.ix[i,'Loans_Leases']-dfFI3.ix[j,'Loans_Leases'])**2)**0.5
            dfFIdist=dfFIdist.append([dftemp])
# All distances for CU i found, now sort descending. Then keep only rows with
# a distance >0 -- i.e., drop the comparison with the subject FI  itself. 
        dfFIdist=dfFIdist.sort(columns=['FI_dist'])
        dfFIdist=dfFIdist[dfFIdist['FI_dist'] > 0.0]
# Now re-index the df.
        dfFIdist=dfFIdist.reset_index(drop=True)
# Now add two neighbours to this row of the dataframe. Note: Row 1 is the 
# distance of a credit union from itself.  Ignore it.
        var1=varprefix+'1'
        var2=varprefix+'2'
        dfFI1.ix[i,var1]=dfFIdist.ix[0,'Name']
        dfFI1.ix[i,var2]=dfFIdist.ix[1,'Name']
# Keep only the FI_Number and the neighbours.
    dfFI1=dfFI1[['FI_Number',var1,var2]]  
    return dfFI1
############# joinappend ##############################################
# This function takes four dfs having nearest neighbours of banks and
# CUs and joins and appends them to make 1 df.
def joinappend(dfCUCU,dfCUbank,dfbankCU,dfbankbank):
# First join the CU and bank neighbours for the credit unions, then the
# banks.
    dfCUneighs=pd.merge(left=dfCUCU, right=dfCUbank)
    dfbankneighs=pd.merge(left=dfbankCU, right=dfbankbank)
# Now append them.
    dfFIneighs=pd.concat([dfCUneighs,dfbankneighs],axis=0)
    return dfFIneighs
      
##########################################################################
################## MAIN BODY OF PROGRAM ##################################
# This manages files. First read the data file.
import pandas as pd
path='C:/Analytics/DATA911/Arkatechture/FDIC_Data/FDIC_KPIs/'
infile='NCUA_and_Banks_KPIs.csv'
outfile='NCUA_and_Banks_KPIs_w_neighs.csv'
dfFI=pd.read_csv(path+infile)
# Make sure columns for calculation have numbers in them.
for i in range(6,dfFI.shape[1]):
    dfFI.iloc[:,i] = dfFI.iloc[:,i].apply(pd.to_numeric, errors='coerce')
# Now get all the unique states and sort it.
stateunique=dfFI['State'].unique()
stateunique.sort()
# For each state, get two closest FIs for CUs and banks in feature space.
# Start with the first state.
state=stateunique[0]
print('Now working on: ',state)
# Subset this state and split it into banks and CUs.
dfsubset=dfFI.ix[dfFI['State']==state]
dfCU=dfsubset.ix[dfsubset['Bank_CU']=='CU']
dfbank=dfsubset.ix[dfsubset['Bank_CU']=='Bank']
# Now get nearest neighbours for banks and credit unions and pass the 
# prefix for the variable name sought.
dfstate1=getclosestFIs('CU_Neigh',dfsubset,dfCU,dfCU)
dfstate2=getclosestFIs('Bank_Neigh',dfsubset,dfCU,dfbank)
dfstate3=getclosestFIs('CU_Neigh',dfsubset,dfbank,dfCU)
dfstate4=getclosestFIs('Bank_Neigh',dfsubset,dfbank,dfbank)
# Now join and append dataframes
dfneighs=joinappend(dfstate1,dfstate2,dfstate3,dfstate4)
for i in range(1,len(stateunique)):
#    if  eak
    print('Now working on: ',stateunique[i])
    dfsubset=dfFI.ix[dfFI['State']==stateunique[i]]
    dfCU=dfsubset.ix[dfsubset['Bank_CU']=='CU']
    dfbank=dfsubset.ix[dfsubset['Bank_CU']=='Bank']
# Now get nearest neighbours for banks and credit unions and pass the 
# prefix for the variable name sought.
    dfstate1=getclosestFIs('CU_Neigh',dfsubset,dfCU,dfCU)
    dfstate2=getclosestFIs('Bank_Neigh',dfsubset,dfCU,dfbank)
    dfstate3=getclosestFIs('CU_Neigh',dfsubset,dfbank,dfCU)
    dfstate4=getclosestFIs('Bank_Neigh',dfsubset,dfbank,dfbank)
# Now join and append dataframes
    dfsubneighs=joinappend(dfstate1,dfstate2,dfstate3,dfstate4)
    dfneighs=pd.concat([dfneighs,dfsubneighs],axis=0)
# We now have all neighbours.  Join it to the main dataframe and output it.
dfout=pd.merge(left=dfFI, right=dfneighs, how='left',left_on='FI_Number',
               right_on='FI_Number')
# Now output the df to a csv.
dfout.to_csv(path_or_buf=path+outfile, index=False)