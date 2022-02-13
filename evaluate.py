import numpy as np
import pandas as pd
import re, os, time
from string import printable
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

import tensorflow as tf
from keras.layers import *
from keras import backend as K
from keras.optimizers import Adam
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import sequence
from keras.models import Sequential, Model, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers.convolutional import Conv1D, MaxPooling1D
from keras.layers.core import Dense, Dropout, Activation, Lambda, Flatten

def create_scaler(df):
    # apply standard scaler
    html_len = df[['html_length']].values.astype(float)
    n_hyperlinks = df[['n_hyperlinks']].values.astype(float)
    n_script_tag = df[['n_script_tag']].values.astype(float)
    n_link_tag = df[['n_link_tag']].values.astype(float)
    n_comment_tag = df[['n_comment_tag']].values.astype(float)

    scaler = StandardScaler()
    html_len_scaled = scaler.fit_transform(html_len)
    n_hyperlinks_scaled = scaler.fit_transform(n_hyperlinks)
    n_script_tag_scaled = scaler.fit_transform(n_script_tag)
    n_link_tag_scaled = scaler.fit_transform(n_link_tag)
    n_comment_tag_scaled = scaler.fit_transform(n_comment_tag)

    # remove column and add to data frame
    df = pd.concat([df.drop(columns=['html_length','n_hyperlinks','n_script_tag','n_link_tag','n_comment_tag']),
                    pd.DataFrame(html_len_scaled, columns=['html_length_std']),
                    pd.DataFrame(n_hyperlinks_scaled, columns=['n_hyperlinks_std']),
                    pd.DataFrame(n_script_tag_scaled, columns=['n_script_tag_std']),
                    pd.DataFrame(n_link_tag_scaled, columns=['n_link_tag_std']),
                    pd.DataFrame(n_comment_tag_scaled, columns=['n_comment_tag_std'])], axis=1, join='inner')

    return df

def create_X_1(temp_X_1):
    url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable] for url in temp_X_1.url]
    max_len=150
    X_new_1 = sequence.pad_sequences(url_int_tokens, maxlen=max_len)
    return X_new_1

def create_X_2(temp_X_2):
    # input (x) variables
    x = temp_X_2.drop(columns=['url']).values.astype(float)

    # reshape input (x)
    X_new_2 = x.reshape(x.shape[0], x.shape[1], 1)
    return X_new_2

def predict_classes(model, x):
    proba = model.predict(x)
    if proba.shape[-1] > 1:
        return proba.argmax(axis=-1)
    else:
        return (proba > 0.5).astype('int32')

# data load
legitimate_test = pd.read_csv('features/legitimate_test.csv')
phish_test = pd.read_csv('features/phish_test.csv')

test = create_scaler(pd.concat([legitimate_test, phish_test], axis=0)).sample(frac=1).reset_index(drop=True)
X_test, y_test = test.drop(columns=['result_flag']), test.result_flag
print(y_test)

# load the saved model
model = load_model('models/model_C.h5')

# evalaute model performance
y_pred = predict_classes(model, [create_X_1(X_test),create_X_2(X_test)])
print(confusion_matrix(y_test, y_pred))

print("All done.")
