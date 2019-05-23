import csv
import re
import os
import multiprocessing
from gensim.models import Word2Vec
import csv
def get_already_word2vec_model(file_to_load):
    model = Word2Vec.load(file_to_load)
    return model
def embedding_sentences(sentences, embedding_size = 64, window = 3, min_count = 0, file_to_load = None, file_to_save = None):

    if file_to_load is not None:
        w2vModel = Word2Vec.load(file_to_load)
    else:
        w2vModel = Word2Vec(sentences, size = embedding_size, window = window, min_count = min_count, workers = multiprocessing.cpu_count(),seed=200)
        if file_to_save is not None:
            w2vModel.save(file_to_save)
    return w2vModel

def get_data():
    path='E:\\'
    all_data=[]
    data_corpus=[]
    for filename in os.listdir(path):
        reader=csv.reader(open(path+filename,encoding='utf-8'))
        path_data=[]
        d_corpus=[]
        for i in reader:
            data=[]
            for k in i:
                if k:
                    if '[' in k or ']' in k:
                        d=re.split('\[|\]',k)
                        for l in d:
                            if l:
                                data.append(l)
                    else:
                        data.append(k)
            d_corpus+=data
            path_data.append(data)
        all_data.append(path_data)
        data_corpus.append(d_corpus)
    print(len(all_data))
    print(len(data_corpus))
    return all_data,data_corpus
def get_corpus_():
    all_data = []
    data_readers = csv.reader(open('F:/new_amd_callback_data.csv'))
    for reader in data_readers:
        if len(reader) > 1:
            # print(reader)
            all_data.append(reader)
    amd_data_readers = csv.reader(open('F:/new_amd_callback_data1.csv'))
    for amd_reader in amd_data_readers:
        if len(amd_reader) > 1:
            # print(amd_reader)
            all_data.append(amd_reader)
    amd_data_readers_=csv.reader(open('F:/new_callback_data.csv'))
    for amd_reader_ in amd_data_readers_:
        if len(amd_reader_)>1:
            all_data.append(amd_reader_)
            # print(amd_reader_)
    print('over')

    return all_data
def bulid_word2vec_model(dataset):
    model = embedding_sentences(dataset, embedding_size=16,
                                min_count=0,
                                file_to_save='E:/amd_trained_word2vec.model')
    return model
if __name__ == "__main__":
    all_data,data_corpus=get_data()
    all_dataset=get_corpus_()
    all_dataset+=data_corpus
    bulid_word2vec_model(all_dataset)

