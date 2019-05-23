import csv
from androguard.misc import AnalyzeAPK
from androguard.core.analysis.analysis import ExternalMethod
import matplotlib.pyplot as plt
import networkx as nx
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard.decompiler import decompiler
from androguard.core.bytecodes import dvm_types#这个里面包含了所有的类型定义和返回类型定义
import re
from pattern_tsn import get_method_vector
from data_helper import get_already_word2vec_model
import os
import math
import operator
#用于获取所有的回调函数
reader=csv.reader(open('/home/yujiawei/huangdengrong/amd_data_pattern/pattern/amd_key_words_new.txt'))
all_key_words=[]
for k in reader:
    if k !=[]:
        all_key_words.append(k[0])
reader=csv.reader(open('/home/yujiawei/huangdengrong/callback_api.csv'))
all_callback=set()
for i in reader:
    all_callback.add(i[1])
#用于获取所有与回调模式相关的关键字
def get_data():
    path='/home/yujiawei/huangdengrong/amd_data_pattern/pattern/patterns/'
    all_data=[]#用于返回每一种pattern所具有的形式
    data_corpus=[]#用于返回与恶意相关的所有的恶意代码
    patterns=[]
    for filename in os.listdir(path):
        reader=csv.reader(open(path+filename,encoding='utf-8'))
        patterns.append(filename)
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
    return all_data,data_corpus,patterns

def Get_Word(method):
    method_final=[]
    method = method.replace(')',';Rbracket;')
    method = method.replace('(', ';Lbracket;')
    method = method.replace('[', 'array;')
    method=re.split('[//;== /''\.]',method)
    for k in method:
        if k !='':
            if k in['V','Z','B','S', 'C','I','J','F','D']:
                method_final.append(dvm_types.TYPE_DESCRIPTOR[k])
            else:
                method_final.append(k)
    return method_final
def Get_one_apk_dictory(apkfile):
    a = apk.APK(apkfile, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apkfile)
    CFG = nx.DiGraph()
    all_apk_data=[]
    fangwen_dic=[]
    for k in d.get_classes():
        for m in dx.find_methods(classname=k.get_name()):

            orig_method = m.get_method()
            if isinstance(orig_method, ExternalMethod):
                is_this_external = True
            else:
                is_this_external = False
            CFG.add_node(orig_method, external=is_this_external)
            callees = []
            for other_class, callee, offset in m.get_xref_to():
                if isinstance(callee, ExternalMethod):
                    is_external = True
                else:
                    is_external = False

                CFG.add_node(callee, external=is_external)
                callees.append(callee)
            if not isinstance(orig_method, ExternalMethod):
                if (orig_method.get_name() + '==' + orig_method.get_descriptor()) not in fangwen_dic:
                    all_apk_data.append(Get_Word(orig_method.get_name() + '==' + orig_method.get_descriptor()))
                    fangwen_dic.append(orig_method.get_name() + '==' + orig_method.get_descriptor())
                    orig_method_code = orig_method.get_source().split('\n')
                    orig_method_code = [i.strip() for i in orig_method_code]
                    for key in all_key_words:
                        for code in orig_method_code:
                            if key in code:
                                if [key] not in all_apk_data:
                                    all_apk_data.append([key])
                for callee in callees:
                    if not isinstance(callee, ExternalMethod):
                        if callee.get_name() != orig_method.get_name():
                            if Get_Word(callee.get_name() + '==' + callee.get_descriptor()) not in fangwen_dic:
                                all_apk_data.append(Get_Word(callee.get_name() + '==' + callee.get_descriptor()))
                                fangwen_dic.append(Get_Word(callee.get_name() + '==' + callee.get_descriptor()))
                                callee_code = callee.get_source().split('\n')
                                callee_code = [i.strip() for i in callee_code]
                                for key in all_key_words:
                                    for code in callee_code:
                                        if key in code:
                                            if [key] not in all_apk_data:
                                                all_apk_data.append([key])
                    else:
                        if Get_Word(callee.get_name() + '==' + callee.get_descriptor()) not in fangwen_dic:
                            all_apk_data.append(Get_Word(callee.get_name() + '==' + callee.get_descriptor()))
    return all_apk_data

def cosin_distance(vector1, vector2):
    dot_product = 0.0
    normA = 0.0
    normB = 0.0
    for a, b in zip(vector1, vector2):
        dot_product += a * b
        normA += a ** 2
        normB += b ** 2
    if normA == 0.0 or normB == 0.0:
        return 0
    else:
        return dot_product / ((normA * normB) ** 0.5)
def Cosin_Simility(vector1,vector2):
    vector=[0 for i in range(len(vector1))]
    # print(vector2)
    # print(vector1)
    for i in range(len(vector1)):
        vector[i]=float(vector1[i])-float(vector2[i])
    sum=0.0
    for i in range(len(vector)):
        sum+=pow(vector[i],2)
    sum=math.sqrt(sum)
    return sum
def Read_amd_data(path):
    allFiles = []
    if os.path.isdir(path):
        fileList = os.listdir(path)
        for f in fileList:
            f = path + '/' + f
            if os.path.isdir(f):
                subFiles = Read_amd_data(f)
                allFiles = subFiles + allFiles
            else:
                allFiles.append(f)
        return allFiles
    else:
        return 'Error,not a dir'
def Read_All_APK(path):
    APK_path=[]
    for _,_dirs,_ in os.walk(path):
        for dir in _dirs:
            for root,dirs,files in os.walk(path+'/'+dir):
                for file in files:
                    if os.path.splitext(file)[1]=='.apk':
                        APK_path.append(path+'/'+dir+'/'+file)
    return APK_path
def pattern_matching_all():
    paths=Read_All_APK('/home/hdr/my_apk_project/dataset_pattern_liangxing/')
    print(len(paths))
    model_path = '/home/hdr/my_apk_project/amd_analysis/amd_analysis/amd_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    all_data,data_corpus,patterns=get_data()
    pattern_num_dic={}
    all_apk_data=[]
    for i in patterns:
        pattern_num_dic[i]=0
    for path in paths:
        print(path)
        dic={}
        for i in patterns:
            dic[i]=0
        try:
            all_apk_data=Get_one_apk_dictory(path)
        except Exception:
            print('chucuo')

        for i,pattern in enumerate(all_data):
            num_pattern=0
            for pattern_key in pattern:
                pattern_vector=get_method_vector(pattern_key,model,16)
                for k in all_apk_data:
                    vector=get_method_vector(k,model,16)
                    distance=Cosin_Simility(pattern_vector,vector)
                    if distance<0.01:
                        num_pattern+=1
                        break
            dic[patterns[i]]=num_pattern
        for i,k in enumerate(dic):
            dic[k]=dic[k]/len(all_data[i])
        new_cal_dic=sorted(dic.items(),key=operator.itemgetter(1),reverse=True)
        print(new_cal_dic)
        for k in new_cal_dic:
            if k[1]>=0.5:
                pattern_num_dic[k[0]]+=1
    for key in pattern_num_dic:
        print(key)
        print(pattern_num_dic[key])
def pattern_matching():
    path='F:/amd_data/AndroRAT/variety1/1b5e6e70643aa22624ed691bce45874f.apk'
    path1='E:\\amd\Bankun\\variety1\\1dc1ad6404a8cf134e9daa9ac7195258.apk'
    all_apk_data=Get_one_apk_dictory(path1)
    model_path = 'E:/amd_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    all_data,data_corpus,patterns=get_data()

    dic={}
    for i in patterns:
        dic[i]=0
    for i,pattern in enumerate(all_data):
        num_pattern=0
        for pattern_key in pattern:
            pattern_vector=get_method_vector(pattern_key,model,16)
            for k in all_apk_data:
                vector=get_method_vector(k,model,16)
                distance=Cosin_Simility(pattern_vector,vector)
                if distance<0.01:
                    num_pattern+=1
                    break
        dic[patterns[i]]=num_pattern
    for i,k in enumerate(dic):
        print(k)
        dic[k]=dic[k]/len(all_data[i])
        print(dic[k])
    new_cal_dic=sorted(dic.items(),key=operator.itemgetter(1),reverse=True)
if __name__ == "__main__":
    pattern_matching_all()
    # pattern_matching()



