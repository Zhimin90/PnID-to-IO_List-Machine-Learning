#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
pd.set_option('display.expand_frame_repr', False)

instrument_sheet = pd.read_excel("PJ00437 BP Baltimore-Instrumentation.xlsx", sheet_name="General Instrument Symbols")
instrumentation = pd.read_excel("PJ00437 BP Baltimore-Instrumentation.xlsx", sheet_name="Instrumentation")



# In[22]:


instrument_sheet


# In[30]:


instrument_sheet.columns


# In[39]:


instrument_sheet = instrument_sheet[['DWG Number', 'Tag', 'Area', 'Type',
       'Description','Class Name',
       'PnPID', 'Area No', 'Unit No', 'Supplied By',
       'Sequence Number', 'Suffix', 'Instrument Spec', 'Signal Type 1', 'Signal Type 2']]


# In[49]:


instrument_sheet[(instrument_sheet['Signal Type 1']!='DIASI') & (instrument_sheet['Signal Type 1']!='DOASI')]


# In[40]:


instrument_sheet.describe(include = 'all')


# In[24]:


hist_DWG_Num = instrument_sheet["DWG Number"].hist(bins=13, figsize=(12,6))


# ### There are on average 25 instrument per P&ID

# In[27]:


hist_DWG_Num = instrument_sheet["Signal Type 1"].hist(bins=6, figsize=(12,6))


# In[28]:


hist_DWG_Num = instrument_sheet["Signal Type 2"].hist(bins=6, figsize=(12,6))


# In[29]:


hist_DWG_Num = instrument_sheet["Signal Type 3"].hist(bins=6, figsize=(12,6))

# In[30]:
instrumentation.columns
instrumentation = instrumentation[['DWG Number', 'Tag', 'Type', 'Description', 'Manufacturer', 'Model Number', 'Class Name',
       'PnPID', 'Area No', 'Unit No', 'Supplied By', 'Status',
       'Sequence Number', 'Suffix', 'Instrument Spec', 'Spec Issued']]
instrumentation.describe(include = 'all')
