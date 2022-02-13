import os
import sys
import csv
import codecs
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# Internal scripts
from extractor import Extractor
from connection import DBConnection

class DataExtractor:
    def __init__(self, data_dir, features_dir, database_name, table_name, mode, target):
        sys.setrecursionlimit(3000)
        self.data_dir = data_dir
        self.features_dir = features_dir
        self.database_name = database_name
        self.table_name = table_name
        self.mode = mode
        self.target = target
        self.df = self.getData()

    def getData(self):
        df = pd.read_sql('SELECT rec_id, url FROM ' + self.table_name, con= DBConnection(self.database_name).get_connection())
        return df

    def extract(self):
        iter = 1
        for _, data in self.df.iterrows():
            self.save_inputs(data['url'], str(data['rec_id']) + ".html")
            print(str(iter) + " done")
            iter += 1

    def save_inputs(self, url, file):
        html_file = self.data_dir + "/" + file
        result = 1 if (self.mode == "phish") else 0

        # Filter hostname from URL
        hostname = urlparse(url).hostname

        f = codecs.open(html_file, 'r', encoding='utf-8', errors='ignore')
        soup = BeautifulSoup(f)

        #START HTML PARAMETER EXTRACTION
        general_features = Extractor().general_f(soup, hostname)
        a_tag_features = Extractor().a_tag(soup, hostname)
        form_tag_features = Extractor().form_tag(soup, hostname)
        ext_resource_features = Extractor().ext_resource(soup, hostname)
        favicon_feature = Extractor().favicon_feature(soup, url, hostname)
        disabled_status_features = Extractor().disabled_status(soup, hostname)

        n_hyperlinks = a_tag_features['n_hyperlinks']
        null_p_ratio = a_tag_features['nullpointers_ratio']
        external_l_ratio = a_tag_features['external_ratio']
        p_data_forms = form_tag_features['form_input_b']
        html_length = general_features['html_length']
        n_script_tag = general_features['n_script_tag']
        n_style_tag = general_features['n_style_tag']
        n_link_tag = general_features['n_link_tag']
        n_comment_tag = general_features['n_comment_tag']
        diff_body_children = general_features['diff_body_children']
        n_body_tag = general_features['n_body_tag']
        n_head_tag = general_features['n_head_tag']
        ext_res_ratio = ext_resource_features
        favicon_used = favicon_feature
        int_form_act_ratio = form_tag_features['int_form_act_ratio']
        abn_form_act_ratio = form_tag_features['abn_form_act_ratio']
        ext_form_act_ratio = form_tag_features['ext_form_act_ratio']
        title_tag = general_features['title_tag']
        title_url_brand = general_features['title_url_brand']
        n_hidden_disabled_tags = disabled_status_features
        #END HTML PARAMETER EXTRACTION

        with open(self.features_dir + '/' + self.mode + '_' + self.target + '.csv', mode='a') as data_file:
            data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow([url, n_hyperlinks, null_p_ratio, external_l_ratio, p_data_forms, html_length,
                n_script_tag, n_link_tag, n_comment_tag, ext_res_ratio, favicon_used, int_form_act_ratio, abn_form_act_ratio,
                ext_form_act_ratio, title_tag, title_url_brand, result])
