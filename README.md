# HybridDLM
# Detecting phishing attacks using a combined model of LSTM and CNN.
This repository includes the implementation done when introducing the novel phishing detection approach presented in http://www.science-gate.com/IJAAS/2020/V7I7/1021833ijaas202007007.html
#
# Folder Structure:
features - this contains the features already extracted from a dataset.
models - model_A.h5 and model_B.h5 were already trained with a 40,000 dataset and used to constrct model c. The model_c.h5 is a already trained model.
const_data.py - Use this to extract features from HTML pages. PLease follow the given instrctions in the script.
train.py - Once the feature extraction is done, use this script to train a new model 
evalaute.py - Use this to evalaute a rained model with some test data 
