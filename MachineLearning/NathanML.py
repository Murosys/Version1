#!/usr/bin/env python
# coding: utf-8

# ### Tracks is the big database of songs that we recommend from. StreamingHistory is Nathan's streaming history. We'll use Streaming History to predict Nathan's music tastes.

# In[12]:


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
#from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score
from sklearn.linear_model import LogisticRegression


# In[13]:


def clean_and_merge_data(song_data, user_data):
    # Read in tracks.csv
    music = song_data

    # Data Cleaning Steps
    music = music.drop_duplicates(subset = ['name', 'artists'])
    user_grouped = user_data.groupby(by = 'trackName').max().reset_index()
    music['primary_artist'] = music['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
    merged = pd.merge(user_grouped, music, left_on = ['trackName', 'artistName'], right_on = ['name', 'primary_artist'])
    merged.loc[merged['msPlayed'] <= 30000, 'Likes_Song'] = 0
    merged.loc[merged['msPlayed'] > 30000, 'Likes_Song'] = 1
    
    return merged

def split_data(song_data, user_data):
    
    merged_data = clean_and_merge_data(song_data, user_data)
    
    # This grabs the following features: ['danceability', 'energy', 'key', 'loudness', 'mode', 
    # 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']
    filters = list(merged_data.columns[12:24])
    train = merged_data[filters + ["Likes_Song"]]
    user_x = train[filters]
    user_y = train["Likes_Song"]
    
    return user_x, user_y, filters

def RandomForestModel(song_data, user_data):
    
    # Split data into train x and train y
    user_x, user_y, filters = split_data(song_data, user_data)
    
    # Make test data stuff
    test = song_data[filters]
    name = song_data['name']
    artist = song_data['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
    
    model = RandomForestClassifier(n_estimators = 70, criterion = "entropy", max_depth = 7, random_state = 123)
    model.fit(user_x, user_y)
    predictions = model.predict(test)

    test['recommendations'] = predictions
    test['name'] = name
    test['artist'] = artist
    
    recommendations = test[test['recommendations'] == 1].sample(50)[['name','artist']]
    
    return recommendations


# In[14]:


tracks = pd.read_csv("tracks.csv")
nathan = pd.read_csv("StreamingHistory.csv")
RandomForestModel(tracks, nathan)


# In[65]:


#
# Gave up on 29/11/22 at 12pm. idk how to fix the nans bro.
# I thought the nans were caused by the values in "y" being floats
# instead of integers, but when I changed the nums to integers then
# the type changed to a numpy array instead of a Panda series.
#
def grid_search(song_data, user_data):
    x, y, filters = split_data(song_data, user_data)
    print("This is y: ", type(y))
    print("This is y_values: ", y.values)
    #y = y.values.astype(int)
    print('This is int_y_values: ', type(y))
    x_train, y_train, x_test, y_test = train_test_split(x, y, test_size = 0.5, random_state = 123)
#     x_test = x_test(lambda x: int(x))
#     y_test = y_test(lambda y: int(y))
    print("x_train: ", x_train)
    print("y_train: ", y_train)
    print("x_test: ", x_test)
    print("y_test: ", y_test)
    n_estimators = [int(x) for x in np.linspace(start = 10, stop = 80, num = 10)]
    max_features = ["auto", "sqrt"]
    max_depth = [2, 6]
    min_samples_split = [2, 5]
    min_samples_leaf = [1, 2]
    bootstrap = [True, False]
    
    param_grid = {"n_estimators": n_estimators, "max_features": max_features,
                  "max_depth": max_depth, "min_samples_split": min_samples_split,
                  "min_samples_leaf": min_samples_leaf, "bootstrap": bootstrap}
    
    rf_model = RandomForestClassifier()
    rf_grid = GridSearchCV(estimator = rf_model, param_grid = param_grid, cv = 3, verbose = 2, n_jobs = 4)
    
    rf_grid.fit(x_train, y_train)
    
    return rf_grid.best_params_


# In[66]:


# I know I'm passing in the right csvs
grid_search(tracks, nathan)


# In[ ]:


# def recommendations(features):
# #     cursor = connection.cursor()
# #     cursor.execute("select * from songs")
# #     music = pd.DataFrame(cursor.fetchall())
# #     music.columns = [i[0] for i in cursor.description]


# #     cursor = connection.cursor()
# #     cursor.execute("select endTime, artistName, trackName, msPlayed from listening_history where user_id = %s", (session['id'],))
# #     user = pd.DataFrame(cursor.fetchall())
# #     user.columns = [i[0] for i in cursor.description]

#     # Read in tracks.csv
#     music = pd.read_csv("tracks.csv")
#     user = pd.read_csv("StreamingHistory.csv")

#     # Data Cleaning Steps
#     music = music.drop_duplicates(subset = ['name', 'artists'])
#     user_grouped = user.groupby(by = 'trackName').max().reset_index()
#     music['primary_artist'] = music['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
#     merged = pd.merge(user_grouped, music, left_on = ['trackName', 'artistName'], right_on = ['name', 'primary_artist'])
#     merged.loc[merged['msPlayed'] <= 30000, 'Likes_Song'] = 0
#     merged.loc[merged['msPlayed'] > 30000, 'Likes_Song'] = 1

#     # Selecting subset of features
#     #filters = list(merged.columns[12:22])
#     filters = features
#     train = merged[filters + ["Likes_Song"]]
#     name = music['name']
#     artist = music['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
#     test = music[filters]
#     user_x = train[filters]
#     user_y = train["Likes_Song"]

#     model = RandomForestClassifier()
#     model.fit(user_x, user_y)
#     predictions = model.predict(test)
#     test['recommendations'] = predictions
#     test['name'] = name
#     test['artist'] = artist

#     recommendations = test[test['recommendations'] == 1].sample(50)[['name','artist']]


# In[ ]:





# In[11]:


tracks = pd.read_csv("tracks.csv")
tracks.head()


# In[12]:


streamingHistory = pd.read_csv("StreamingHistory.csv")
streamingHistory.head()

