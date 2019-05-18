import numpy as np
import csv
import matplotlib.pyplot as plt
import re
'''

dx_var:shape=(batch_size, max_visit_per_person, max_dx_per_visit), name='dx_var')
rx_var:shape=(batch_size, max_visit_per_person, max_dx_per_visit, max_rx_per_dx,name='rx_var)
'''
csv.field_size_limit(500 * 1024 * 1024)
def load_data(path,path1):
    csv_file=csv.reader(open(path,'r',encoding='utf-8'))
    csv_file1 = csv.reader(open(path1, 'r', encoding='utf-8'))
    rx_data=[]
    dx_data=[]
    all_dx_data=[]#
    all_rx_data=[]
    i=0
    for line in csv_file:
        if i>800:break
        if len(line)==1:
            if line[0].find('apk'):
                i += 1

        if len(line)>1:
            if line[0]=='code_seq':
                call=[]
                for key in line[1:]:
                    if key=='\\':
                        dx_data.append(call)
                        call=[]
                    else:
                        call.append(key)
            elif line[0]=='call_seq':
                code=[]
                for key in line[1:]:
                    if key=='\\':
                        rx_data.append(code)
                        code=[]
                    else:
                        code.append(key)
            if rx_data!=[]:
                all_rx_data.append(rx_data)
                rx_data=[]
            if dx_data!=[]:
                all_dx_data.append(dx_data)
                dx_data=[]
    rx_data1 = []
    dx_data1 = []
    all_dx_data1 = []  #
    all_rx_data1 = []
    for line in csv_file1:  
        if len(line) > 1:
            if line[0] == 'code_seq':
                call = []
                for key in line[1:]: 
                    if key == '\\':
                        dx_data1.append(call)
                        call = []
                    else:
                        call.append(key)
            elif line[0] == 'call_seq':
                code = []
                for key in line[1:]:
                    if key == '\\':
                        rx_data1.append(code)
                        code = []
                    else:
                        code.append(key)
            if rx_data1 != []:
                all_rx_data1.append(rx_data1)
                rx_data1 = []
            if dx_data1 != []:
                all_dx_data1.append(dx_data1)
                dx_data1 = []
    all_dx_data+=all_dx_data1
    all_rx_data+=all_rx_data1
    return all_dx_data,all_rx_data
def build_corpus_new(all_dx_data,all_rx_data):
    dx_data_corpus=list()
    rx_data_corpus=list()
    dx_data_corpus.append(['<padding> sentence'])
    rx_data_corpus.append('<padding>')
    for key in all_dx_data:
        for v in key:
            if v not in dx_data_corpus:
                dx_data_corpus.append(v)
    for key in all_rx_data:
        for key1 in key:
            for key2 in key1:
                if key2 not in rx_data_corpus:
                    rx_data_corpus.append(key2)
    # print(len(dx_data_corpus))
    # print(len(rx_data_corpus))
    return dx_data_corpus,rx_data_corpus
def generate_train_dataset(path,path1):
    all_dx_data,all_rx_data=load_data(path,path1)
    all_rx_data_new=[]
    all_size=[]
    
    for all_callback_seq in all_rx_data:
        all=[]
        for i,key in enumerate(all_callback_seq):
            new_code=[k for k in key if k!='Lbracket' and k!='Rbracket']
            all_size.append(len(new_code))
            all.append(new_code)
        all_rx_data_new.append(all)
    all_dataset=[]
    for i ,all_callback_seq in enumerate(all_rx_data_new):
        if i==len(all_rx_data_new)-1:break
        data=[]
        for k,key in enumerate(all_callback_seq):
            if len(key)>400:
                # print(len(key))
                i1=0
                for j in range(len(key)//400+1):
                    if len(key[i1:j*400])>0:
                        # print(all_rx_data[i][i1:j*400])
                        data.append((all_dx_data[i][k],key[i1:j*400]))
                        i1=j*400
                if(len(key[i1:])>0):
                    data.append((all_dx_data[i][k],key[i1:]))
            else:
                data.append((all_dx_data[i][k],key))
        if len(data)>35:
            all_dataset.append(data[:len(data)//2])
            all_dataset.append(data[len(data)//2:])
        else:
            all_dataset.append(data)
  
    return all_dataset
def generate_train_data_new(path,path1):
    data=generate_train_dataset(path,path1)
    all_dx_data,all_rx_data=load_data(path,path1)
    dx_data_corpus,rx_data_corpus=build_corpus_new(all_dx_data,all_rx_data)
    dataset=[]
    for key in data:
        values=[]
        for value in key:
            if len(value[1])<400:
                for _ in range(400-len(value[1])):
                    value[1].append('<padding>')
            values.append((value[0],value[1]))
        dataset.append(values)
    data=[]
    for key in dataset:
        if len(key)>35:
            data.append(key[:35])
        else:
            for i in range(35-len(key)):
                key.append((['<padding> sentence'],['<padding>']*400))
            data.append(key)
    all_dx_data_new=[]
    all_rx_data_new=[]
    all_dx_mask=[]
    all_rx_mask=[]
    for key in data:
        dx_data=[]
        rx_data=[]
        dx_mask=[]
        rx_mask=[]
        for value in key:
            # rx_data.append([value[1]])
            if dx_data_corpus.index(value[0])==0:
                dx_mask.append([0])
            else:
                dx_mask.append([1])
            dx_data.append([dx_data_corpus.index(value[0])])
            al_rx=[]
            rx_lb=[]
            for k in value[1]:
                al_rx.append(rx_data_corpus.index(k))
                if rx_data_corpus.index(k)==0:rx_lb.append([0])
                else: rx_lb.append([1])
            rx_mask.append([rx_lb])
            rx_data.append([al_rx])
        all_rx_data_new.append(rx_data)
        all_dx_data_new.append(dx_data)
        all_dx_mask.append(dx_mask)
        all_rx_mask.append(rx_mask)
   
    all_dx_label=[]
    for key in all_dx_data_new:
        all_dx_label.append([key[-1]]+key[:-1])
    print(np.shape(np.array(all_rx_data_new)))
    print(np.shape(np.array(all_dx_data_new)))
    print(np.shape(np.array(all_dx_label)))
    return list(zip(all_dx_data_new,all_rx_data_new,all_dx_mask,all_rx_mask,all_dx_label)),len(dx_data_corpus),len(rx_data_corpus)
def batch_iter(data, batch_size, num_epochs):
    data_size = len(data)
    print(data_size)

    num_batches_per_epoch = int((data_size - 1) / batch_size) + 1
    for epoch in range(num_epochs):

        shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, data_size)
            # print(str(start_idx)+'::'+str(end_idx))
            yield shuffled_data[start_idx: end_idx]
if __name__ == "__main__":
    path='E:/apk_method_code/callback_method1.csv'
    # generate_train_data_new(path)
