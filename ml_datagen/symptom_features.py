import os, sys, re
#depended upon scrapy and genie and data_store
sys.path.insert(0, '/Users/myasir/Personal')
from DataStore.dir import Dir

from os import listdir
from os.path import isfile, join
PATH = Dir('../..')

from collections import OrderedDict

import copy
import spacy
import json
import csv

nlp = spacy.load('en_core_web_sm')

word_count = {}
token_dict = OrderedDict()
disease_symptoms_tokenized = list()
disease_symptoms_sentenced = list()

def save_feature_as_tokens(data_set):
    '''
    data_set = (title, (lot of tokens))
    excel file format :
    col 1 = disease 
    col 2...inf = each token
    col1 value = disease name
    other col value is binary 0|1
    each row is for each set of tokens
    '''
    csv_file = open("feature_as_tokens.csv", "w+")
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    token_obj = copy.copy(token_dict)
    symptom_list = token_obj.keys()
    header = ['disease']
    header.extend(symptom_list)
    import pdb; pdb.set_trace()
    csv_writer.writerow(header)
    for title, tokens in data_set:
        token_obj = copy.copy(token_dict)
        #import pdb; pdb.set_trace()
        row = [title]
        for token in tokens:
            token_obj[token] = 1
        
        row.extend(token_obj.values())
        csv_writer.writerow(row)

def save_feature_as_sents(data_list):
    '''
    data_set = (title, sentence)
    excel file format :
    col 1 = disease 
    col 2 = symptoms
    col1 value = disease name 
    col2 value = one sentence of one disease
    each row is for each set of tokens
    '''
    csv_file = open("feature_as_sents.csv", "w+")
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['disease', 'symptom'])
    for data in data_list:
        #import pdb; pdb.set_trace()
        csv_writer.writerow(data)
    
def tokenize_sent(title, sent):
    token_set = set()
    doc = nlp(sent)
    for word in doc:
        if (not word.is_punct and not word.is_stop
        and not word.is_space and word.is_alpha):
            token_set.add(word.lemma_)
            if word.lemma_ in word_count:
                word_count[word.lemma_] += 1
            else:
                token_dict[word.lemma_] = 0
                word_count[word.lemma_] = 1
            
    disease_symptoms_tokenized.append((title, token_set))

def get_all_token():
    word_count = {k:v for k, v in sorted(word_count.items(), key=lambda itm: itm[1], reverse=True)}
    with open("syptom_keys.txt", "w+") as fp:
        json.dump(word_count, fp, indent=4)

def extract_all_features():
    syptom_sent_set = set()
    flag = 0
    title_flag = 0
    limit = 0
    title = ''

    my_path = PATH.disease_data_dir
    files = [f for f in listdir(my_path) if isfile(join(my_path, f))]
    for fil in files:
        title = ''
        title_flag = 0
        if limit == 2000:
            break
        limit += 1
        fp = open(os.path.join(my_path, fil), "r")
        line_no = 0
        for each_line in fp.readlines():
            each_line = each_line.strip()
            if not title_flag and not title and not line_no:
                title = each_line
                title_flag = 1
                #to fix data issue TODO: to fix data title issue
                if title.startswith(('y', 'eart')) and not title.startswith('yeast'):
                    title = "h{}".format(title)
                
            if not flag and each_line == 'symptoms':
                flag = 1
            elif not flag:
                continue
            if flag and each_line.startswith('->'):
                sent = each_line.strip('->')
                syptom_sent_set.add(sent)
                disease_symptoms_sentenced.append((title, sent))
                tokenize_sent(title, sent)
            if flag and each_line.startswith('---'):
                flag = 0
                break
            line_no += 1


    save_feature_as_sents(disease_symptoms_sentenced)
    save_feature_as_tokens(disease_symptoms_tokenized)




extract_all_features()