#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[7]:


data = pd.read_csv("Play_Activity_maya.csv")


# In[8]:


data.head()


# In[14]:


data.groupby(by = "Artist Name")['Artist Name'].count().sort_values(ascending = False).head(10)


# In[15]:


data.groupby(by = "Song Name")['Song Name'].count().sort_values(ascending = False).head(10)


# In[16]:


len(data.groupby(by = "Artist Name")['Artist Name'].unique())


# In[17]:


len(data.groupby(by = "Song Name")['Song Name'].unique())


# In[20]:


filtered = data[["Song Name","Milliseconds Since Play"]]


# In[24]:


most_played = pd.DataFrame(filtered.groupby(by = "Song Name").max()).reset_index()


# In[25]:


most_played[most_played['Milliseconds Since Play'] < 30000].head(30)


# In[ ]:




