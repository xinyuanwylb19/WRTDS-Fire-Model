# WRTDS-Fire Model
# Xinyuan Wei
# 1/16/2020

import pandas as pd
import math
import random
from pandas import DataFrame
from sklearn import linear_model

watershed_list=['North_Sylamore']

watershed_name=watershed_list[0]

'''
Discharge:  feet3/s     L/s
DOC:        mg C /L     kg C/day
feet3 - L   28316.8
'''
# Read the data.
DOC_file=watershed_name+'_DOC.csv'
DISC_file=watershed_name+'_DISC.csv'

DOC_data=pd.read_csv(DOC_file, sep=',')
DISC_data=pd.read_csv(DISC_file, sep=',')

#print(DOC_data)
#print(DISC_data)

DOC_records=len(DOC_data)
print('The total number of DOC records is '+str(DOC_records)+'.')

Results_arr=[]

# Match DOC and discharge.
for i in range (DOC_records):
    temp=[]
    
    m_DOC=DOC_data['DOC'].at[i]
    
    date=DOC_data['Date'].at[i]
    DISC=DISC_data.loc[DISC_data['Date']==date]
    m_DISC=DISC['Discharge'].tolist()[0]
    m_Fire_Size=DISC['Fire_Size'].tolist()[0]
    m_TSLF=DISC['TSLF'].tolist()[0]
    m_Fire_Severity=DISC['Fire_Severity'].tolist()[0]
    
    
    #print(m_DISC)
    
    temp.append(date)
    temp.append(m_DISC)
    temp.append(m_DOC)
    temp.append(m_Fire_Size)
    temp.append(m_TSLF)
    temp.append(m_Fire_Severity)
    
    Results_arr.append(temp)

#print(Results_arr)    
temp_data=DataFrame(Results_arr,columns=['Date','Discharge',
                                          'DOC','Fire_Size',
                                          'TSLF','Fire_Severity'])

# Add year, month, data
temp_data['Date']=pd.to_datetime(temp_data['Date'])
temp_data['Year']=temp_data['Date'].dt.year
temp_data['Month']=temp_data['Date'].dt.month
temp_data['Day']=temp_data['Date'].dt.day

model_arr=[]
for i in range (DOC_records):
    temp=[]
    LNDOC=math.log(temp_data['DOC'].at[i])
    LNDIS=math.log(temp_data['Discharge'].at[i])
    SINM=math.sin(temp_data['Month'].at[i])
    COSD=math.cos(temp_data['Day'].at[i])
    EXPTSLF=math.exp(-temp_data['TSLF'].at[i])
    
    temp.append(temp_data['Date'].at[i])
    temp.append(temp_data['Year'].at[i])
    temp.append(temp_data['Month'].at[i])
    temp.append(temp_data['Day'].at[i])
    temp.append(temp_data['Discharge'].at[i])
    temp.append(temp_data['DOC'].at[i])
    temp.append(LNDOC)
    temp.append(LNDIS)
    temp.append(SINM)
    temp.append(COSD)
    temp.append(temp_data['Fire_Size'].at[i])
    temp.append(temp_data['Fire_Severity'].at[i])
    temp.append(EXPTSLF)
    
    model_arr.append(temp)
model_data=DataFrame(model_arr,columns=['Date','Year','Month','Day',
                                        'Discharge','DOC','LNDOC',
                                        'LNDIS','SINM','COSD','Fire_Size',
                                        'Fire_Severity','EXPTSLF'])

DOC_data=model_data.copy()

nan_value=float('NaN')
DOC_data.replace('',nan_value,inplace=True)
DOC_data.dropna(subset=['LNDOC'],inplace=True)

#print(DOC_data)

# Function to estimate coefficients.
def coef_E(data_arr):
    coefs=[]

    randomlist=random.sample(range(len(data_arr)-1),20)
    
    temp_copy=data_arr.copy()
    model_temp=temp_copy.drop(temp_copy.index[randomlist])
    #print(len(model_temp))
    
    X=model_temp[['LNDIS','Year','SINM','COSD',
                  'Fire_Size','Fire_Severity','EXPTSLF']]
    Y=model_temp['LNDOC']
    
    regr=linear_model.LinearRegression()
    regr.fit(X,Y)
    
    #print('Coefficients:',regr.coef_)
    
    coefs.append(regr.coef_[0])
    coefs.append(regr.coef_[1])
    coefs.append(regr.coef_[2])
    coefs.append(regr.coef_[3])
    coefs.append(regr.coef_[4])
    coefs.append(regr.coef_[5])
    coefs.append(regr.coef_[6])
    coefs.append(regr.intercept_)
    
    return(coefs)

# Estimate coefficients and intercept.
# Coefficients for Nitrogen.
DOC_coefs_arr=[]

for i in range (100):
    temp_coefsDOC=[]
    temp_coefs=coef_E(DOC_data)
    temp_coefsDOC.append(temp_coefs[0])
    temp_coefsDOC.append(temp_coefs[1])
    temp_coefsDOC.append(temp_coefs[2])
    temp_coefsDOC.append(temp_coefs[3])
    temp_coefsDOC.append(temp_coefs[4])
    temp_coefsDOC.append(temp_coefs[5])
    temp_coefsDOC.append(temp_coefs[6])
    temp_coefsDOC.append(temp_coefs[7])
    
    DOC_coefs_arr.append(temp_coefsDOC)
    
DOC_coefs=DataFrame(DOC_coefs_arr,columns=['CDS','CYR','CMN','CDY',
                                           'CFS','CFV','CTF','INC'])    

CDC=round(DOC_coefs['CDS'].mean(),4)
CYR=round(DOC_coefs['CYR'].mean(),4)
CMN=round(DOC_coefs['CMN'].mean(),4)
CDY=round(DOC_coefs['CDY'].mean(),4)
CFS=round(DOC_coefs['CFS'].mean(),4)
CFV=round(DOC_coefs['CFV'].mean(),4)
CTF=round(DOC_coefs['CTF'].mean(),4)
INC=round(DOC_coefs['INC'].mean(),4)
#print(CDC,CYR,CMN,CDY,CFS,CFV,CTF,INC)

# Calculate the DOC fluxes (mg/L).
DISC_data['Date']=pd.to_datetime(DISC_data['Date'])
DISC_data['Year']=DISC_data['Date'].dt.year
DISC_data['Month']=DISC_data['Date'].dt.month
DISC_data['Day']=DISC_data['Date'].dt.day

DOC_arr=[]    
for i in range (len(DISC_data)):
    temp_DOCr=[]
    t_Dc=math.log(DISC_data['Discharge'].at[i])
    t_Yr=DISC_data['Year'].at[i]
    t_Mn=math.sin(DISC_data['Month'].at[i])
    t_Dy=math.cos(DISC_data['Month'].at[i])
    
    t_FS=DISC_data['Fire_Size'].at[i]
    t_FV=DISC_data['Fire_Severity'].at[i]
    t_TF=math.exp(-DISC_data['TSLF'].at[i])
    
    DOC_con=math.exp(CDC*t_Dc+CYR*t_Yr+CMN*t_Mn+CDY*t_Dy
                     +CFS*t_FS+CFV*t_FV+CTF*t_TF+INC)
    
    temp_DOCr.append(DISC_data['Date'].at[i])
    temp_DOCr.append(DISC_data['Year'].at[i])
    temp_DOCr.append(DISC_data['Month'].at[i])
    temp_DOCr.append(DISC_data['Day'].at[i])
    temp_DOCr.append(DISC_data['Discharge'].at[i])
    temp_DOCr.append(DOC_con)
    
    DOC_arr.append(temp_DOCr)

results=DataFrame(DOC_arr,columns=['Date','Year','Month','Day',
                                  'Discharge','DOC']) 
file_name='Result_'+watershed_name+'.csv'

results.to_csv(file_name)
