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

def construct_model():
    mergedOut = Add()([model_A.output,model_B.output])

    # output layer
    mergedOut = Dense(1, activation='sigmoid')(mergedOut)

    model = Model([model_A.input,model_B.input], mergedOut)
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    model.compile(optimizer=adam, loss='binary_crossentropy', metrics=['acc'])
    return model

def predict_classes(model, x):
    proba = model.predict(x)
    if proba.shape[-1] > 1:
        return proba.argmax(axis=-1)
    else:
        return (proba > 0.5).astype('int32')

# data load
legitimate_train = pd.read_csv('features/legitimate_train.csv')
legitimate_test = pd.read_csv('features/legitimate_test.csv')
phish_train = pd.read_csv('features/phish_train_w2v.csv')
phish_test = pd.read_csv('features/phish_test.csv')

train = create_scaler(pd.concat([legitimate_train, phish_train], axis=0)).sample(frac=1).reset_index(drop=True)
test = create_scaler(pd.concat([legitimate_test, phish_test], axis=0)).sample(frac=1).reset_index(drop=True)

X_train, y_train = train.drop(columns=['result_flag']), train.result_flag
X_test, y_test = test.drop(columns=['result_flag']), test.result_flag

# load sub-models
model_A = load_model('models/model_A.h5')
model_A.layers.pop()
model_A = Model(inputs=model_A.inputs, outputs=model_A.layers[-1].output)

model_B = load_model('models/model_B.h5')
model_B.layers.pop()
model_B = Model(inputs=model_B.inputs, outputs=model_B.layers[-1].output)

# early stopping
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=50)
mc = ModelCheckpoint('models/tmp_model.h5', monitor='val_loss', mode='min', verbose=1, save_best_only=True)

# create model
model = construct_model()

# fit model
history = model.fit([create_X_1(X_train),create_X_2(X_train)], y_train, validation_split=0.1, epochs=500, batch_size=64, verbose=1, callbacks=[es, mc])

# load the saved model
model = load_model('models/tmp_model.h5')
model.save('models/model_C.h5')
os.remove('models/tmp_model.h5')

# evalaute model performance
y_pred = predict_classes(model, [create_X_1(X_test),create_X_2(X_test)])
print(confusion_matrix(y_test, y_pred))

print("All done.")
