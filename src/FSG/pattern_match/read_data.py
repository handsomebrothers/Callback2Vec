import csv
from get_apk_words import *
def get_amd_data():
    path = '/home/yujiawei/huangdengrong/amd_data_pattern/new_amd_pattern1.csv'
    csv_file = csv.reader(open(path, 'r', encoding='utf-8'))
    all_amd_data = []
    new_data = []
    apk_data = []
    path_reader=[]
    for reader in csv_file:
        if len(reader) > 1:

            for key in reader:
                if key == '/':
                    apk_data.append(new_data)
                    new_data = []
                else:
                    new_data.append(key)
        else:
            path_reader.append(reader)
            all_amd_data.append(apk_data)
            apk_data = []
    return all_amd_data,path_reader
def pattern_matching_all():
    all_amd_data,path_reader=get_amd_data()
    model_path = '/home/yujiawei/huangdengrong/amd_data_pattern/pattern/amd_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    all_data,data_corpus,patterns=get_data()
    pattern_num_dic={}
    for i in patterns:
        pattern_num_dic[i]=0
    print(len(all_amd_data))
    for ii,data in enumerate(all_amd_data):
        print(path_reader[ii])
        dic={}
        for i in patterns:
            dic[i]=0
        for i,pattern in enumerate(all_data):
            num_pattern=0
            for pattern_key in pattern:
                b=False
                pattern_vector=get_method_vector(pattern_key,model,16)
                for k in data:
                    vector=get_method_vector(k,model,16)
                    distance=Cosin_Simility(pattern_vector,vector)

                    if distance<2:
                        b=True
                        break
                if b==True:
                    num_pattern += 1

            dic[patterns[i]]=num_pattern/len(pattern)
        # for i,k in enumerate(dic):
        #     dic[k]=dic[k]/len(all_data[i])
        new_cal_dic=sorted(dic.items(),key=operator.itemgetter(1),reverse=True)
        print(new_cal_dic)
        for k in new_cal_dic:
            if k[1]>=1:
                pattern_num_dic[k[0]]+=1
    for key in pattern_num_dic:
        print(key)
        print(pattern_num_dic[key])
if __name__ == "__main__":
    # get_amd_data()
    pattern_matching_all()



