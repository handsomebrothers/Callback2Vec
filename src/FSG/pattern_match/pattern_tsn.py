from sklearn.manifold import TSNE
from data_helper import get_data,get_already_word2vec_model
import matplotlib.pyplot as plt
def get_word_vector(word,w2vModel):

    embeddingDim = w2vModel.vector_size

    embeddingUnknown = [0 for i in range(embeddingDim)]
    if word in w2vModel.wv.vocab:
        return w2vModel[word]
    else:
        return embeddingUnknown
def get_method_vector(method_sentence,model,embedding_size):
    num = len(method_sentence)
    if num == 0:
        num = 1
    method_vector = [0 for i in range(embedding_size)]

    for word in method_sentence:
        word_vector = get_word_vector(word, model)
        # print(word_vector)
        method_vector = [word_vector[i] + method_vector[i] for i in range(len(word_vector))]
    method_vector = [i / num for i in method_vector]
    return method_vector
def plot_stn():
    model_path = 'E:/amd_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    tsne = TSNE(n_components=2,random_state=100)
    all_data,data_corpus=get_data()
    for i,pattern in enumerate(all_data):
        pattern_vectors=[]
        for key in pattern:
            if key!=[]:
                pattern_vector=get_method_vector(key,model,16)
                pattern_vectors.append(pattern_vector)
        pattern_tsn=tsne.fit_transform(pattern_vectors)
        plt.subplot(221)
        plt.scatter(pattern_tsn[:, 0], pattern_tsn[:, 1], c='g',label='amd pattern vector')
        plt.show()
# plot_stn()
