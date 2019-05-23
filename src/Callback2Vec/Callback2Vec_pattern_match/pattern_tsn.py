from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from get_model import *
def get_method_vector(method_sentence):
    checkpoint_path='F:\\path'
    dx_var,rx_var,rx_emb,visit_emb=test(checkpoint_path)
    return rx_emb[rx_var.index(method_sentence)]
def plot_stn():
    model_path = 'E:/amd_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    tsne = TSNE(n_components=2,random_state=100)
    all_data,data_corpus=get_data()
    for i,pattern in enumerate(all_data):
        pattern_vectors=[]
        for key in pattern:
            if key!=[]:
                pattern_vector=get_method_vector(key)
                pattern_vectors.append(pattern_vector)
        pattern_tsn=tsne.fit_transform(pattern_vectors)
        plt.subplot(221)
        plt.scatter(pattern_tsn[:, 0], pattern_tsn[:, 1], c='g',label='amd pattern vector')
        plt.show()
# plot_stn()
