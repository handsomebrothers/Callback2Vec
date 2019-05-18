# -*- coding: utf-8 -*-
import multiprocessing
from gensim.models import Word2Vec
import csv
def embedding_sentences(sentences, embedding_size = 64, window = 3, min_count = 0, file_to_load = None, file_to_save = None):
    '''
    embeding_size Word Embedding Dimension
    window : Context window
    min_count : Word frequency less than min_count will be deleted
    '''
    if file_to_load is not None:
        w2vModel = Word2Vec.load(file_to_load)  #  load model
    else:
        w2vModel = Word2Vec(sentences, size = embedding_size, window = window, min_count = min_count, workers = multiprocessing.cpu_count(),seed=200)
        if file_to_save is not None:
            w2vModel.save(file_to_save)     # Save Model
    return w2vModel
# This function is used to represent a sentence as a vector (corresponding to representing a method as a vector)
def get_method_vector(sentence,w2vModel):
    sentence_vector=[]
    for word in sentence:
        sentence_vector.append(w2vModel[word])#Word vectors for adding each word
    return sentence_vector
# This function is used to represent a word as a vector (corresponding to a word in method)
def get_word_vector(word,w2vModel):
    return w2vModel[word]
# This function is used to get the vector of a text (corresponding to the word vector of class or apk)
def get_apk_class_vector(document,w2vModel):
    all_vectors = []
    embeddingDim = w2vModel.vector_size
    # 嵌入维数
    embeddingUnknown = [0 for i in range(embeddingDim)]
    for sentence in document:
        this_vector = []
        for word in sentence:
            if word in w2vModel.wv.vocab:
                this_vector.append(w2vModel[word])
            else:
                this_vector.append(embeddingUnknown)
        all_vectors.append(this_vector)
    return all_vectors
#   This function is used to obtain the similarity between two sentences,
#   with the help of python's own function to calculate the similarity.
def get_two_sentence_simility(sentence1,sentence2,w2vModel):
    sim = w2vModel.n_similarity(sentence1, sentence2)
    return sim
#  Used to build corpus
def bulid_word2vec_model():#Used to build word 2vec model
    model = embedding_sentences(get_corpus_(), embedding_size=32,
                                min_count=0,
                                file_to_save='D:\\APK_科研\\word2vec\\apk_trained_word2vec.model')
    return model
# Used to get the model that has been created
def get_already_word2vec_model(file_to_load):
    model = Word2Vec.load(file_to_load)
    return model
# Used for acquiring corpus
def get_corpus():
    all_data=[]
    data_readers=csv.reader(open('D:/new_amd_callback_data1.csv'))
    for reader in data_readers:
        if len(reader)>1:
            # print(reader)
            all_data.append(reader)
    amd_data_readers=csv.reader(open('D:/new_callback_data1.csv'))
    for amd_reader in amd_data_readers:
        if len(amd_reader)>1:
            # print(amd_reader)
            all_data.append(amd_reader)
    print('over')
    return all_data
def get_corpus_():
    all_data = []
    data_readers = csv.reader(open('D:/new_amd_callback_data.csv'))
    for reader in data_readers:
        if len(reader) > 1:
            # print(reader)
            all_data.append(reader)
    amd_data_readers = csv.reader(open('D:/new_amd_callback_data1.csv'))
    for amd_reader in amd_data_readers:
        if len(amd_reader) > 1:
            # print(amd_reader)
            all_data.append(amd_reader)
    amd_data_readers_=csv.reader(open('D:/new_callback_data.csv'))
    for amd_reader_ in amd_data_readers_:
        if len(amd_reader_)>1:
            all_data.append(amd_reader_)
    print('over')
    return all_data
if __name__ == "__main__":
    bulid_word2vec_model()
