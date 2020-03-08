#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import pickle


# In[2]:



file = open("temp_model.pickle",'rb')
df = pickle.load(file)
file.close()
lats = []
lons = []

for row in df['RLocation']:
    if type(row) != str:
        lat,lon = (None,None)
    else:
        lat,lon = tuple(str(row).split(','))
        lat = int(lat)
        lon = int(lon)
    lats.append(lat)
    lons.append(lon)
df["Lat"] = lats
df["Long"] = lons 

df_located = df[['RLocation','Lat','Long']][df['RLocation'].notna()]
X = np.array(df_located)
X = X[:,1:3]


# In[3]:


from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler


# In[4]:


X = StandardScaler().fit_transform(X)
db = DBSCAN(eps=0.03, min_samples=2).fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

df_located["unit_label"] = db.labels_
df["unit_label"] = None
df.iloc[df_located.index, -1] = db.labels_

groupby_unit_label_Lat = df[df['Lat'].notnull()].groupby('unit_label').mean()[['Lat','Long']]
groupby_unit_label_Lat = groupby_unit_label_Lat.rename(columns={'Lat':'Lat_mean','Long':'Long_mean'})
df = df.merge(groupby_unit_label_Lat, how = 'left', right_index = True, left_on = 'unit_label')
df[['Area No','Unit No','Sequence Number']] = df[['Area No','Unit No','Sequence Number']].applymap(str)
df_encoded = pd.get_dummies(df[['DWG Number', 'Area No','Unit No']], prefix=['DWG Number', 'Area No','Unit No'])
normalized_df = df_encoded
train_index = normalized_df[df["RLocation"].notna()].dropna().index

X = np.array(normalized_df[df["RLocation"].notna()].dropna())
y = np.array(pd.get_dummies(df.iloc[train_index,:]["unit_label"]))

from sklearn.neighbors import KNeighborsClassifier
model_knn= KNeighborsClassifier(n_neighbors=3, metric='jaccard')
model_knn.fit(X,y)


# In[5]:


test_index = normalized_df[df["RLocation"].isna()].dropna().index
X_test = np.array(normalized_df.iloc[test_index,:])
y_pred = model_knn.predict(X_test)

y_pred_arr = []
No_Out_list = []
for j, row in enumerate(y_pred):
    for i,v in enumerate(row):
        if v: y_pred_arr = np.append(y_pred_arr,i)
    if sum(row) == 0: 
        print("nothing at j: " + str(j))
        No_Out_list = np.append(No_Out_list,j)
        y_pred_arr = np.append(y_pred_arr, None)

df['pre_unit_label'] = None
df['pre_unit_label'] = pd.Series(y_pred_arr,index=test_index)
groupby_unit_label_Lat = groupby_unit_label_Lat.rename(columns={'Lat_mean':'pre_Lat_mean','Long_mean':'pre_Long_mean'})
df = df.merge(groupby_unit_label_Lat, how = 'left', right_index = True, left_on = 'pre_unit_label')
check_result_df = df[['DWG Number', 'Tag', 'Signal Type 1', 'Lat',
       'Long', 'unit_label', 'Lat_mean', 'Long_mean', 'pre_unit_label', 'pre_Lat_mean', 'pre_Long_mean']]
combined_location_df = check_result_df[['Lat_mean', 'Long_mean',
       'pre_Lat_mean', 'pre_Long_mean']].apply(
    lambda x: ','.join(x.dropna().astype(str)),
    axis=1)
combined_location_df = combined_location_df.str.split(',',expand=True)
check_result_df[['cL_Lat', 'cL_Long']] = combined_location_df
plot_df = check_result_df[['Tag','cL_Lat','cL_Long']]
plot_df = plot_df[['cL_Lat', 'cL_Long']].apply(pd.to_numeric)
plot_bygroup_df = plot_df.groupby(['cL_Lat', 'cL_Long']).size().reset_index(name='count')
nonNAN_index = plot_df[['cL_Lat', 'cL_Long']].dropna().index
X = np.array(plot_df.iloc[nonNAN_index,:][['cL_Lat', 'cL_Long']] )


# In[6]:


from dbscan import MyDBSCAN
from sklearn.preprocessing import StandardScaler


# In[7]:


X_normalized = StandardScaler().fit_transform(X)
my_labels = np.array(MyDBSCAN(X_normalized, eps=.4, MinPts=20, MaxPts = 100))
core_samples_mask = np.zeros_like(my_labels, dtype=bool)
core_samples_mask[np.array(range(0,len(my_labels)))] = True
labels = my_labels
clusterDict = {}
for label in labels:
    if label in clusterDict.keys():
        clusterDict[label] += 1
    else:
        clusterDict[label] = 1
dbscan_labeled = check_result_df.iloc[nonNAN_index,:]
dbscan_labeled["Gateway_Label"] = my_labels


# In[8]:


export_df = df[['DWG Number','Tag','Description','Signal Type 1']]
export_df['ASIGateway_label'] = dbscan_labeled['Gateway_Label']


# In[9]:


file = open("temp_model.pickle",'rb')
df = pickle.load(file)
df['ASIGateway_label'] = dbscan_labeled['Gateway_Label']

with open('learnedmodel.pickle', 'wb') as f:
    pickle.dump(df, f)

