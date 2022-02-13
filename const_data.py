import os, sys, csv, argparse
from data_extractor import DataExtractor

import warnings
warnings.filterwarnings("ignore")

#execute
# const_data.py --mode phish --target train
#when execting train script, use "phish" as mode when phishing webpage features are extracted, otherwise use "legitimate"
#when execting train script, use "train" as target if the data extraction is to construct train dataset, otherwise use "test"

# data args
parser = argparse.ArgumentParser(description="Train Hybrid model")
parser.add_argument('--mode', type=str, default='none', metavar="MODE",
  help="type of the dataset. either phishing or legitimate")
parser.add_argument('--target', type=str, default='none', metavar="TARGET",
  help="specify whether the feature extraction is done for training purpose or testing. default is set to training.")
FLAGS = vars(parser.parse_args())

# check mode and target is set
if FLAGS["mode"] == "none" or FLAGS["target"] == "none":
    if FLAGS["mode"] == "none":
        print("please specify whether the feature extraction is executing with phishing dataset or legitimate dataset")
    if FLAGS["target"] == "none":
        print("please specify whether the feature extraction is for training or testing")
    sys.exit()

############IMPORTANT PARAMETERS###############
data_dir = "/path/to/your/html/folder" # dataset html files location
features_dir = "features" # location of the extracted features file
database_name = "db_test" # this script assumes the relevent urls are in a SQL file. See the example SQL file provided in the repository
table_name = "phish_train" # name of the database table
###############################################
print("html files location:")
print(data_dir)
print("location of the extracted features file:")
print(features_dir)
print("database name:")
print(database_name)
print("name of the database table:")
print(table_name)
###############################################

print("All set. Let's begin the feature extraction...")

if not os.path.exists(features_dir):
    os.mkdir(features_dir)

with open(features_dir + '/' + FLAGS["mode"] + '_' + FLAGS["target"] + '.csv', mode='w') as data_file:
    data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data_writer.writerow(['url', 'n_hyperlinks', 'null_p_ratio', 'external_l_ratio', 'p_data_forms', 'html_length',
        'n_script_tag', 'n_link_tag', 'n_comment_tag', 'ext_res_ratio', 'favicon_used', 'int_form_act_ratio',
         'abn_form_act_ratio', 'ext_form_act_ratio', 'title_tag', 'title_url_brand', 'result_flag'])

const = DataExtractor(data_dir, features_dir, database_name, table_name, FLAGS["mode"], FLAGS["target"])
const.extract()

print("Feature extraction is completed. Have a nice day.")
