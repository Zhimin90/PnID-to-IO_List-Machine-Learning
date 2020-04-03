import pickle
import pandas as pd
import numpy as np

file = open("df_complete.pickle", 'rb')
df = pickle.load(file)

# In[137]:


import itertools
pd.crosstab(df['ASIGateway_label'], df['Signal Type 1'])


# In[138]:


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 110)
pd.set_option('display.width', 110)


# In[139]:


moduleList = [[4, 4], [4, 0], [0, 4], [2, 2], [2, 1]]
#[AC5235,AC5215,AC5233,AC5214,AC2316]

#This function takes a dataframe of a unit with its associated instruments,
#it searches for all listed possible configuration from configuration list
#and returns the the best possible assignment as a dataframe appended with
#Asi address and module chosen


def unitModuleCombinationSearch(df):
    df_len = df.shape[0]
    suffix_no = getSuffixNo(df)
    #Search from the top of the module list
    #Call moduleAssignmentSearch
    #start a breadth first search to find the highest aggregate configuration score
    return recurseHelperFunc(df, moduleList, suffix_no)


def recurseHelperFunc(df, moduleList, suffix_no):
    print("df.index: " + str(df.index))
    scoreList = []

    for module in moduleList:
        combinationList = moduleAssignmentSearch(
            df['Signal Type 1'], module, suffix_no)
        if not len(combinationList) == 0:
            # top of the best scored index position
            score = combinationList[0][0]
            scoreList.append((score, module, combinationList[0][1]))

    bestModuleConfig = sorted(scoreList, key=lambda x: x[0], reverse=True)[0]
    config_index = [df.index[i] for i in bestModuleConfig[2]]
    #print(df.index,config_index)
    #print(sorted(scoreList, key=lambda x: x[0], reverse=True)[0:10])
    #print("best module is: " + str(bestModuleConfig[1]))

    remainingRows = Diff(list(df.index), config_index)
    if len(remainingRows) == 0:
        print("Config Combination Found!")
        module_id = 0
        return([(config_index, module_id, bestModuleConfig[1])])

    prevBestModule = recurseHelperFunc(
        df.loc[remainingRows, :], moduleList, suffix_no)

    #prevBestModule = found_index, module_id, prevModuleConfig
    #print(prevBestModule)
    module_id = prevBestModule[-1][1]
    curBestModule = (config_index, module_id+1, bestModuleConfig[1])
    return prevBestModule + [curBestModule]


def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


def getSuffixNo(df):
    #print("count: " +str(df['Suffix'].value_counts()))
    #print("mode: "+str(df['Suffix'].value_counts().mode().values[0]))
    if len(df['Suffix'].value_counts().mode().values) == 0:
        return 1
    if df['Suffix'].value_counts().mode().values[0]:
        return df['Suffix'].value_counts().mode().values[0]
    else:
        return 1


# In[140]:


#module_config => [numberoftype1IO,numberoftype2IO,...]
#suffix_no is the number of instrument tag witht the same suffix
def moduleAssignmentSearch(df, module_config, suffix_no):
    #print("index: " + str(df.index))
    shift = 0
    df_len = df.shape[0]
    numOfIndex = int(df_len/suffix_no)
    configPositions = range(0, numOfIndex)
    noOfPossiblePosition = int(sum(module_config)/suffix_no)
    listOfList = []

    for comb in itertools.combinations(list(configPositions), noOfPossiblePosition):
        #print(comb)
        indexOfIndex = []
        for index in comb:
            for member in range(0, suffix_no):
                indexOfIndex.append(index*suffix_no+member)
        #print(indexOfIndex)
        listOfCurrSelRows = [df.index[i] for i in indexOfIndex]
        listOfList.append(indexOfIndex)
        #print(listOfCurrSelRows)

    ValidConfigList = []
    for comb in listOfList:
        #print(comb)
        curr_config = np.array(df.iloc[comb].value_counts())
        configurationValidity, configurationScore = checkConfig(
            module_config, curr_config)
        if configurationValidity:
            #print("config found!")
            #print("score: " + str(configurationScore))
            ValidConfigList.append((configurationScore, comb))
        else:
            pass
            #print("config failed!")

    if (sum(module_config) > df.shape[0]):
        curr_config = np.array(df.value_counts())
        configurationValidity, configurationScore = checkConfigRemainder(
            module_config, curr_config)
        if configurationValidity:
            return [(configurationScore, list(range(0, df.shape[0])))]
        else:
            return [(-9999, [])]

    bestConfigList = sorted(ValidConfigList, key=lambda x: x[0], reverse=True)
    return bestConfigList


def checkConfig(setConfig, currentConfig):
    score = 0  # zero is a perfect score
    if (len(setConfig) != len(currentConfig)):
        return False, None
    for i, config in enumerate(setConfig):
        if ((config - currentConfig[i]) > 1) or (currentConfig[i] > config):
            return False, None
        score -= abs(config - currentConfig[i])
    return True, score


def checkConfigRemainder(setConfig, currentConfig):
    #print(setConfig, currentConfig)
    score = 0  # zero is a perfect score

    for i, config in enumerate(currentConfig):
        if (config - setConfig[i]) > 0:
            return False, None
        # a small penalty to find the best module
        score -= abs(config - setConfig[i])/10
    if len(currentConfig) < len(setConfig):
        #print("in Penalty")
        #print("len(currentConfig)"+str(len(currentConfig)))
        #print("setConfig[len(currentConfig):-1]" + str(setConfig[len(currentConfig):]))
        for diff in setConfig[len(currentConfig):]:
            score -= diff/10
    return True, score


# In[141]:


df["moduleConfig"] = None
df["moduleId"] = None
df["ASiAddress"] = None


# In[142]:


def increASI(address):
    letter = address[-1]
    if len(address) == 2:
        num = int(address[0])
    else:
        num = int(address[0:2])

    if (letter == 'A'):
        return (str(num)+'B')
    else:
        return (str(num+1)+letter)


# In[143]:


for df_group in df.groupby(['ASIGateway_label']):
    unit_group = df_group[1][['Unit No', 'Sequence Number', 'ASIGateway_label_order']].groupby(
        ['Unit No', 'Sequence Number']).agg({'ASIGateway_label_order': ['mean']})
    unit_group.columns = ['_'.join(col).strip()
                          for col in unit_group.columns.values]
    IO_List = df_group[1][['DWG Number', 'ASIGateway_label', 'Tag',
                           'Unit No', 'Type', 'Sequence Number', 'Suffix',
                           'ASIGateway_label_order', 'Description',
                           'RLocation', 'Signal Type 1']].sort_values(by=['Unit No',
                                                                          'Sequence Number',
                                                                          'Type', 'Signal Type 1',
                                                                          'ASIGateway_label_order'])
    ASiAddress = '1A'
    ASiEnumeration = 0
    sorted_list = pd.merge(IO_List, unit_group, left_on=['Unit No', 'Sequence Number'], right_index=True).sort_values(
        by=['ASIGateway_label_order_mean', 'Type', 'Signal Type 1'])
    #print(sorted_list)
    for unit_no, sequence_no in sorted_list.groupby(['Unit No', 'Sequence Number']):
        #print((unit_no, sequence_no)[0])
        #print((unit_no, sequence_no)[1])
        unit_df = (unit_no, sequence_no)[1]
        #print(unit_df['Signal Type 1'].value_counts())
        #print(unit_df.sort_values(by=['Suffix','Signal Type 1']))
        unit_sorted = unit_df.sort_values(by=['Suffix', 'Signal Type 1'])
        config = unitModuleCombinationSearch(unit_sorted)
        #print("config: " + str(config))
        for row in config:
            print(row[0])
            df.loc[np.array(row[0]), 'moduleConfig'] = str(row[2])
            df.loc[np.array(row[0]), 'ASiAddress'] = ASiAddress
            ASiAddress = increASI(ASiAddress)
            df.loc[np.array(row[0]), 'moduleId'] = ASiEnumeration
            ASiEnumeration += 1
        #moduleAssignmentSearch(unit_sorted['Signal Type 1'],[4,4],2)
        #print(unit_sorted.iloc[0:8,:]['Signal Type 1'].value_counts())
        #print('-'*100)

    #print(IO_List)


# In[144]:


for df_group in df.groupby(['ASIGateway_label']):
    unit_group = df_group[1][['Unit No', 'Sequence Number', 'ASIGateway_label_order']].groupby(
        ['Unit No', 'Sequence Number']).agg({'ASIGateway_label_order': ['mean']})
    unit_group.columns = ['_'.join(col).strip()
                          for col in unit_group.columns.values]
    IO_List = df_group[1][['DWG Number', 'ASIGateway_label', 'Tag',
                           'Unit No', 'Type', 'Sequence Number', 'Suffix',
                           'ASIGateway_label_order', 'Description', 'moduleConfig', 'moduleId',
                           'Signal Type 1']].sort_values(by=['Unit No',
                                                             'Sequence Number',
                                                             'Type', 'Signal Type 1',
                                                             'ASIGateway_label_order'])
    sorted_list = pd.merge(IO_List, unit_group, left_on=['Unit No', 'Sequence Number'], right_index=True).sort_values(by=['Unit No',
                                                                                                                          'Sequence Number',
                                                                                                                          'Type', 'Signal Type 1', ])
    #print(sorted_list)


# In[145]:


df.columns


# In[146]:


exportDF = df[['DWG Number', 'ASIGateway_label', 'RLocation', 'Tag', 'Area', 'Type', 'Loop Number', 'Location',
               'Description', 'Manufacturer', 'Model Number', 'Comment', 'Class Name', 'PnPID', 'Area No', 'Unit No',
               'Supplied By', 'Status', 'Sequence Number', 'Suffix', 'Instrument Spec', 'Spec Issued', 'PO Issued',
               'Signal Type 1', 'Signal Type 2', 'Signal Type 3', 'ASiAddress',
               'ASIGateway_label_order', 'moduleConfig', 'moduleId']].sort_values(by=['ASIGateway_label', 'moduleId', 'Unit No', 'Sequence Number'])
#exportDF


# In[147]:


exportDF.columns


# In[148]:


exportDF[['DWG Number', 'ASIGateway_label', 'Tag', 'Description',
          'Signal Type 1', 'ASiAddress', 'ASIGateway_label_order',
          'moduleConfig', 'moduleId']].to_csv(r'IO_List.csv', index=False)

