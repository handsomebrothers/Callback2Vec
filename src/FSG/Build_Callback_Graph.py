import numpy as np
import csv
from androguard.misc import AnalyzeAPK
from androguard.core.analysis.analysis import ExternalMethod
import matplotlib.pyplot as plt
import networkx as nx
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard.decompiler import decompiler
import random
import copy
import re
import os

from androguard.core.bytecodes import dvm_types
reader=csv.reader(open('F:\\2018年第一学年科研\\APK科研\\数据集\\callback_api.csv'))
all_callback=set()
for i in reader:
    all_callback.add(i[1])
print(len(all_callback))
'''
# STRUCTURE DEFINE
# state -- {"label": label_content, "component": "activity", ...}
# edges -- {start_label_content1: [(start_state1, end_state1),(start_state1, end_state2), ...], start_label_content2: [(start_state2, end_state1), (start_state2, end_state2),...] }
# activities -- {activity_name: {label_name1: state1, label_name2: state2, ...}, activity_name: {},...}
# activity -- {label_name1: state1, label_name2: state2, ...}
'''

ACTIVITY='activity'
SERVICE='service'
RECEIVER='receiver'
OTHER='other'
LIFE_CYCLE='activity_cycle'
NON_LIFE_CYCLE='non_activity_cycle'
ATTRAUX= "attr_aux"
ATTRORIGINAL = "attr_original"
activity_callback=["onCreate","onStart","onResume","onPause","onStop","onDestroy","onRestart"]
service_callback=["onCreate","onStartCommand","onBind","onUnbind","onDestroy"]
receiver_callback=["onReceive"]
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
def get_component_graph(component_class):
    life_states=[]
    non_life_states=[]
    edges={}
    edges_back = {}
    callback_collect=[]
    if component_class.get_superclassname().find("Activity")>-1 and\
        not component_class.get_superclassname().find("$")>-1:
        edges,edges_back=activity_life(edges,edges_back,component_class)
        for j1 in component_class.get_methods():
            if j1.get_name()=="onCreate"  or \
                j1.get_name()=="onStart" or \
                j1.get_name()=="onResume"  or \
                j1.get_name()=="onPause"  or \
                j1.get_name()=="onStop"  or \
                j1.get_name()=="onDestroy" or \
                j1.get_name()=="onRestart"  :
                key = "%s %s %s" % (j1.get_class_name(), j1.get_name(), j1.get_descriptor())
                state_tmp = {"label": key, "component":"Activity"}
                # replace_states(edges,edges_back,state_tmp)
                life_states.append(state_tmp)
                callback_collect.append(j1.get_name())
            elif j1.get_name() in all_callback and j1.get_name() not in activity_callback:
                key = "%s %s %s" % (j1.get_class_name(), j1.get_name(), j1.get_descriptor())
                state_tmp = {"label": key,"component":"Activity"}
                non_life_states.append(state_tmp)

        edges,edges_back=add_non_activity_life_states(edges,edges_back,non_life_states,component_class)

        if non_life_states!=[]:
            del edges[get_new_state("onResume",component_class)][edges[get_new_state("onResume",component_class)].index([get_new_state("onResume",component_class),get_new_state("onPause",component_class)])]
            # del edges[get_new_state("onPause",component_class)][edges[get_new_state("onPause",component_class)].index([get_new_state("onPause",component_class),get_new_state("onResume",component_class)])]
            del edges_back[get_new_state("onPause",component_class)][edges_back[get_new_state("onPause",component_class)].index([get_new_state("onResume",component_class),get_new_state("onPause",component_class)])]

            # del edges_back[get_new_state("onResume",component_class)][edges_back[get_new_state("onResume",component_class)].index([get_new_state("onPause",component_class),get_new_state("onResume",component_class)])]
        for node in life_states:
            edges,edges_back=replace_states(edges,edges_back,node)
        init_node={"label": "%s %s" % (component_class.get_name(), '<init>'),"component":"Activity"}
        edges,edges_back=replace_states(edges,edges_back,init_node)
        Terminal_node={"label": "%s %s" % (component_class.get_name(),'onTerminal'),"component":"Activity"}
        edges,edges_back=replace_states(edges,edges_back,Terminal_node)
    if component_class.get_superclassname().find("Service")>-1 and\
        not component_class.get_superclassname().find("$")>-1:
        #service lifecycle
        edges,edges_back=service_life(edges,edges_back,component_class)
        for j1 in component_class.get_methods():
            if j1.get_name()=="onCreate" or \
                j1.get_name()=="onStartCommand" or \
                j1.get_name()=="onBind" or \
                j1.get_name()=="onUnbind" or \
                j1.get_name()=="onDestroy" :
                key = "%s %s %s" % (j1.get_class_name(), j1.get_name(), j1.get_descriptor())
                state_tmp = {"label": key, "component":"Service"}
                life_states.append(state_tmp)
                callback_collect.append(j1.get_name())
            elif j1.get_name() in all_callback and j1.get_name() not in service_callback:
                key = "%s %s %s" % (j1.get_class_name(), j1.get_name(), j1.get_descriptor())
                state_tmp = {"label": key,"component":"Service"}
                non_life_states.append(state_tmp)
        edges,edges_back=add_non_service_life_states(edges,edges_back,non_life_states,component_class)
        for node in life_states:
            edges,edges_back=replace_states(edges,edges_back,node)
        init_node={"label": "%s %s" % (component_class.get_name(), '<init>'),"component":"Service"}
        # print(init_node)
        edges,edges_back=replace_states(edges,edges_back,init_node)
        Terminal_node={"label": "%s %s" % ( component_class.get_name(),'onTerminal'),"component":"Service"}
        edges,edges_back=replace_states(edges,edges_back,Terminal_node)

    if component_class.get_superclassname().find("BroadcastReceiver") > -1 and \
            not component_class.get_superclassname().find("$") > -1:
        edges,edges_back=receiver_life(edges,edges_back,component_class)
        for j1 in component_class.get_methods():
            if j1.get_name()=="onReceive":
                key = "%s %s %s" % (j1.get_class_name(), j1.get_name(), j1.get_descriptor())
                state_tmp = {"label": key, "component": "Receiver"}
                life_states.append(state_tmp)
                callback_collect.append(j1.get_name())
            elif j1.get_name() in all_callback and j1.get_name() not in receiver_callback:
                key = "%s %s %s" % (j1.get_class_name(), j1.get_name(), j1.get_descriptor())
                state_tmp = {"label": key,"class_name":j1.get_class_name(), "component": "Receiver", "attr": NON_LIFE_CYCLE}
                non_life_states.append(state_tmp)
        # edges,edges_back=add_non_activity_life_states(edges,edges_back,non_life_states,component_class)
        for node in life_states:
            edges,edges_back=replace_states(edges,edges_back,node)
        init_node={"label": "%s %s" % (component_class.get_name(), '<init>'),"component":"Receiver"}
        edges,edges_back=replace_states(edges,edges_back,init_node)
        # Terminal_node={"label": "%s %s" % (component_class.get_name(), 'onTerminal'),"component":"Receiver"}
        Terminal_node={"label": "%s %s" % (component_class.get_name(),'onTerminal'),"component":"Receiver"}
        edges,edges_back=replace_states(edges,edges_back,Terminal_node)
    return edges,edges_back,life_states,non_life_states,callback_collect#return edges and edges_back

#get name and class  of callback
def get_callback_name_class(state):
    str_state=state2str(state)
    callback_name=str_state.split(' ')[1]
    callback_class=str_state.split(' ')[0]

    callback= "%s %s"%(callback_name,callback_class)

    return callback
#replace state of callback with original callback
def replace_states(edges,edges_back,state):

    callback=get_callback_name_class(state)
    for k in edges.keys():
        states=edges[k]
        for i,state1 in enumerate(states):
            if callback in state1:
                edges[k][i][state1.index(callback)]=state
    for k in edges_back.keys():
        states=edges_back[k]
        for i,state1 in enumerate(states):
            if callback in state1:
                edges_back[k][i][state1.index(callback)]=state
    return edges,edges_back
#参数要求：start_states 是node ,end_states是任意类型
def non_life_edge_gene(edges,edges_back,start_states,end_states):
    # add into edges
    if get_callback_name_class(start_states) in edges.keys():
        if [start_states,end_states] not in edges[get_callback_name_class(start_states) ]:
            edges[get_callback_name_class(start_states) ].append([start_states,end_states])
    else:
        edges[get_callback_name_class(start_states)] = []
        edges[get_callback_name_class(start_states)].append([start_states,end_states])
    if type(end_states).__name__=='str':
        if end_states in edges_back.keys():
            if [start_states,end_states] not in edges_back[end_states]:
                edges_back[end_states].append([start_states,end_states])
        else:
            edges_back[end_states] = []
            edges_back[end_states].append([end_states,end_states])
    else:
        if get_callback_name_class(end_states) in edges.keys():
            if [start_states,end_states] not in edges[get_callback_name_class(end_states) ]:
                edges[get_callback_name_class(end_states) ].append([start_states,end_states])
        else:
            edges[get_callback_name_class(end_states)] = []
            edges[get_callback_name_class(end_states)].append([start_states,end_states])
    # add into  edges_back


    return edges,edges_back
def add_non_activity_life_states(edges,edges_back,non_life_states,component_class):

    for i in range(len(non_life_states)-1):
        for j in range(i+1, len(non_life_states)):
            non_life_edge_gene(edges,edges_back,non_life_states[i],non_life_states[j])
            non_life_edge_gene(edges,edges_back,non_life_states[j],non_life_states[i])

    if len(non_life_states)>0:
        life_edge_gene(edges,edges_back,get_new_state("onResume",component_class),non_life_states[0])
        non_life_edge_gene(edges,edges_back,non_life_states[-1],get_new_state("onPause",component_class))
    return edges,edges_back
def add_non_service_life_states(edges,edges_back,non_life_states,component_class):

    for i in range(len(non_life_states)-1):
        for j in range(i+1, len(non_life_states)):
            non_life_edge_gene(edges,edges_back,non_life_states[i],non_life_states[j])
            non_life_edge_gene(edges,edges_back,non_life_states[j],non_life_states[i])

    if len(non_life_states)>0:
        life_edge_gene(edges,edges_back,get_new_state("onBind",component_class),non_life_states[0])
        non_life_edge_gene(edges,edges_back,non_life_states[-1],get_new_state("onUnbind",component_class))
    return edges,edges_back

def get_length_edges(edges):
    len1=0
    for key in edges.keys():
        len1+=len(edges[key])
    return len1

key_service=['bindService','startService']
key_activity=['startActivity','startActivityForResult']
key_receiver=['registerReceiver']
key=['bindService','startService','startActivity','startActivityForResult','registerReceiver','Intent','setClass']

def combine_component(cp1,cp2,component_edges_dic):
    # print(component_edges_dic[cp1][list(component_edges_dic[cp1].keys())[0]][0][0])
    # component_edges_dic[cp1][list(component_edges_dic[cp1].keys())[0]].\
    #     append([component_edges_dic[cp1][list(component_edges_dic[cp1].keys())[0]][0][0],
    #             component_edges_dic[cp2][list(component_edges_dic[cp2].keys())[0]][0][0]])
    for key in component_edges_dic[cp2].keys():
        # print(component_edges_dic[cp2][key])
        if key in component_edges_dic[cp1].keys():
            component_edges_dic[cp1][key]+=component_edges_dic[cp2][key]
        else:
            component_edges_dic[cp1][key]=component_edges_dic[cp2][key]
    component_edges_dic[cp2]={}
    return component_edges_dic

def get_source_apk(apk_path):
    a = apk.APK(apk_path, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apk_path)
    with open('F:\\1.txt', 'w') as txtData:
        for k in d.get_classes():
            print('class_name:' + k.get_name())
            txtData.writelines('class_name:' + k.get_name())
            txtData.writelines(dp.get_source_class(k))
    with open('F:\\2.txt', 'w') as write_txt:
        for cls in d1[0].classes.class_def:
            for j in cls.get_methods():
                if j.get_code()!= None:
                    for i in j.get_code().code.get_instructions():
                        write_txt.writelines(i.get_name())
                        write_txt.writelines('\n')
                        write_txt.writelines(i.get_output())
                        write_txt.writelines('\n')

def get_edge_node(edge):
    pass
def get_states(apk_path,writer):
    writer.writerow([apk_path])
    a = apk.APK(apk_path, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apk_path)
    broadcastreceiver=[]#
    for i in d.get_classes():
        if i.get_superclassname().find("BroadcastReceiver")>-1:
            broadcastreceiver.append(i.get_name())
    # mainclass_name =  a.get_main_activity()#
    # xml=a.get_android_manifest_axml().get_xml()#
    component_edges_dic={}#
    for i in d.get_classes():
        if i.get_superclassname().find("Activity")>-1 and\
        not i.get_superclassname().find("$")>-1 or\
                i.get_superclassname().find("Service")>-1or\
                i.get_superclassname().find("BroadcastReceiver")>-1:
            edges,edges_back=get_final_graph(i,i.get_superclassname())#
            # edge_num=get_length_edges(edges)
            component_edges_dic[i.get_name()]=edges#
    callback_dictory={}#
    for cls in d1[0].classes.class_def:#
            if cls.get_superclassname().find("Activity")>-1 and\
        not cls.get_superclassname().find("$")>-1 or\
                cls.get_superclassname().find("Service")>-1or\
                cls.get_superclassname().find("BroadcastReceiver")>-1:#
                other_callback=[]#
                for j in cls.get_methods():#
                    j1=''
                    b=False
                    if j.get_code()!= None:
                        for i in j.get_code().code.get_instructions():
                            if str(i.get_name()).find("const-class")> -1: #for case 1)2)4)
                                # print(cls.get_name())
                                if cls.get_name()!=i.get_output().split(', ')[-1] and  i.get_output().split(', ')[-1]not in other_callback:
                                    other_callback.append(i.get_output().split(', ')[-1])
                            elif str(i.get_output()).find('registerReceiver')>-1:

                                b=True
                    if b:
                        for key in broadcastreceiver:
                            if key in j1 and key not in other_callback:
                                other_callback.append(key)
                callback_dictory[cls.get_name()]=other_callback
    # for k in d.get_classes():
    #     if k.get_superclassname().find("Activity")>-1 and\
    #     not k.get_superclassname().find("$")>-1 or\
    #             k.get_superclassname().find("Service")>-1or\
    #             k.get_superclassname().find("BroadcastReceiver")>-1:
    #         other_callback=[]#用于统计一个组件是否调用了其他组件
    #         for m in dx.find_methods(classname=k.get_name()):
    #             orig_method=m.get_method()
    #             j1=''
    #             b=False
    #             if not isinstance(orig_method, ExternalMethod):
    #                 if orig_method.get_code()!= None:
    #                     for i in orig_method.get_code().code.get_instructions():
    #                         j1+=i.get_output()
    #                         if str(i.get_output()).find('registerReceiver')>-1:
    #                             #如果找到receiver则进行,将所有的广播器内容进行对比，找到所注册的广播
    #                             b=True
    #                         elif str(i.get_name()).find("const-class")> -1: #for case 1)2)4)
    #                             # print(cls.get_name())
    #                             if k.get_name()!=i.get_output().split(', ')[-1]:
    #                                 other_callback.append(i.get_output().split(', ')[-1])
    #             if b:
    #                 for key in broadcastreceiver:
    #                     if key in j1:
    #                         print('------------')
    #                         print(key)
    #                         other_callback.append(key)
    #             for other_class,callee,offset in m.get_xref_to():#得到原函数调用的其他组件中的方法或者是其他class中的方法
    #                 if not isinstance(callee, ExternalMethod):
    #                     if callee.get_code()!= None:
    #                         for i1 in callee.get_code().code.get_instructions():
    #                             if str(i1.get_output()).find("const-class")>-1:
    #                                 print(i1.get_output())
    #                                 print(callee.get_class_name())
    #                             if str(i1.get_output()).find('registerReceiver')>-1:
    #                                 print(i1.get_output())
    valid_callback={}#
    for i in d.get_classes():
        if i.get_superclassname().find("Activity")>-1 and\
        not i.get_superclassname().find("$")>-1 or\
                i.get_superclassname().find("Service")>-1or\
                i.get_superclassname().find("BroadcastReceiver")>-1:
            valid_callback[i.get_name()]=1

    for i in d.get_classes():
        if i.get_superclassname().find("Activity")>-1 and\
        not i.get_superclassname().find("$")>-1 or\
                i.get_superclassname().find("Service")>-1or\
                i.get_superclassname().find("BroadcastReceiver")>-1:
            if get_length_edges(component_edges_dic[i.get_name()])<10:

                if callback_dictory[i.get_name()]!=[]:
                    for cl in callback_dictory[i.get_name()]:
                        if cl in valid_callback.keys():
                            if valid_callback[cl]==1:
                                #combine callback
                                component_edges_dic=combine_component(i.get_name(),cl,component_edges_dic)
                                valid_callback[cl]=0
            # else:

            #     if callback_dictory[i.get_name()]!=[]:
            #         # print('+++++++++++++')
            #         for cl in callback_dictory[i.get_name()]:
            #             if cl in component_edges_dic.keys():
            #                 if get_length_edges(component_edges_dic[cl])<10:
            #                     if cl in valid_callback.keys():
            #                         if valid_callback[cl]==1:
            #                         #进行合并
            #                             component_edges_dic=combine_component(i.get_name(),cl,component_edges_dic)
            #                             valid_callback[cl]=0

    callback_collection=[]
    for i in d.get_classes():
        if i.get_superclassname().find("Activity")>-1 and\
        not i.get_superclassname().find("$")>-1 or\
                i.get_superclassname().find("Service")>-1or\
                i.get_superclassname().find("BroadcastReceiver")>-1:

            if get_length_edges(component_edges_dic[i.get_name()])<20 and get_length_edges(component_edges_dic[i.get_name()])>1:
                callback_collection.append(i.get_name())#Get all the objects that need to be merged


    #Merge smaller data
    if len(callback_collection)>0:
        for cal in callback_collection[1:]:
            component_edges_dic=combine_component(callback_collection[0],cal,component_edges_dic)
    class_code_dic=callback_method_ast.Update_one_apk_dictory(d,dx)#

    #
    for i in d.get_classes():
        if i.get_superclassname().find("Activity")>-1 and\
        not i.get_superclassname().find("$")>-1 or\
                i.get_superclassname().find("Service")>-1or\
                i.get_superclassname().find("BroadcastReceiver")>-1:
            if component_edges_dic[i.get_name()]!={} and get_length_edges(component_edges_dic[i.get_name()])>1:
                Graph1={}
                class_name=''
                for key in component_edges_dic[i.get_name()].keys():
                    for value in component_edges_dic[i.get_name()][key]:
                        if value[0]['label'] in Graph1.keys():
                            Graph1[value[0]['label']][value[1]['label']]=0
                        else:
                            Graph1[value[0]['label']]={}
                            Graph1[value[0]['label']][value[1]['label']]=0
                        class_name=value[0]['label'].split(' ')[0]
                term_key= "%s %s"%(class_name,'onTerminal')
                if term_key in Graph1.keys():
                    Graph1[term_key]={"%s %s"%(class_name,'<init>'):0}
                else:
                    Graph1[term_key]={}
                    Graph1[term_key]={"%s %s"%(class_name,'<init>'):0}
                Graph1=new_gene_graph(Graph1)
                # print(Graph1)
                print('图的长度：'+str(len(Graph1)))
                print(Graph1[list(Graph1.keys())[0]])
                callback_sequence=list(iter_dfs(Graph1,list(Graph1.keys())[0]))
                # print(callback_sequence)
                call_seq=['call_seq']
                code_seq=['code_seq']
                for s in callback_sequence:
                    if s.split(' ')[1]!='onTerminal' and s.split(' ')[1]!='<init>':
                        if s.split(' ')[0] in class_code_dic.keys() and s.split(' ')[1] in class_code_dic[s.split(' ')[0]].keys():
                                # callback_sequence.append()
                            call_seq+=class_code_dic[s.split(' ')[0]][s.split(' ')[1]]
                            call_seq+='\\'
                            code_seq+=Get_Word(s.split(' ')[1]+'=='+s.split(' ')[-1])
                            code_seq+='\\'
                writer.writerow(call_seq)
                writer.writerow(code_seq)
def new_gene_graph(graph):
    all_init=[]
    # print(graph)
    for key in graph:
        if key.split(' ')[1]=='<init>':
            all_init.append(key)
            for k in all_init:
                graph[key][k]=0
                graph[k][key]=0
    return graph

def state2str(state):
    return state["label"]
# bind callback and component_class
def get_new_state(callback,component_class):
    return "%s %s"%(callback,component_class.get_name())

def activity_life(edges,edges_back,component_class):#original activity callback
    life_edge_gene(edges,edges_back,get_new_state("<init>",component_class), get_new_state("onCreate",component_class))
    life_edge_gene(edges,edges_back,get_new_state("onCreate",component_class),get_new_state("onStart",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onStart",component_class),get_new_state("onResume",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onResume",component_class),get_new_state("onPause",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onPause",component_class) ,get_new_state("onResume",component_class))#return activity
    life_edge_gene(edges,edges_back,get_new_state("onPause",component_class),get_new_state("onStop",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onStop",component_class),get_new_state("onDestroy",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onStop",component_class), get_new_state("onCreate",component_class))
    life_edge_gene(edges,edges_back,get_new_state("onStop",component_class),get_new_state("onRestart",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onRestart",component_class),get_new_state("onStart",component_class))
    life_edge_gene(edges,edges_back,get_new_state("onPause",component_class),get_new_state("onCreate",component_class))
    life_edge_gene(edges,edges_back,get_new_state("onDestroy",component_class),get_new_state("onTerminal",component_class))

    return edges,edges_back

#service lifecycle
def service_life(edges,edges_back,component_class):#original service callback
    life_edge_gene(edges,edges_back,get_new_state("<init>",component_class), get_new_state("onCreate",component_class))
    life_edge_gene( edges,edges_back,get_new_state("onCreate",component_class),get_new_state("onStartCommand",component_class))
    life_edge_gene( edges,edges_back,get_new_state("onStartCommand",component_class),get_new_state("onDestroy",component_class))
    life_edge_gene(edges,edges_back,get_new_state("onDestroy",component_class),get_new_state("onTerminal",component_class))
    # life_edge_gene(edges,edges_back,get_new_state("<init>",component_class), get_new_state("onCreate",component_class))
    life_edge_gene(edges,edges_back, get_new_state("onCreate",component_class),get_new_state( "onBind",component_class))
    life_edge_gene( edges,edges_back,get_new_state( "onBind",component_class),get_new_state( "onUnbind",component_class))
    life_edge_gene(edges,edges_back, get_new_state( "onUnbind",component_class),get_new_state("onDestroy",component_class))
    # life_edge_gene(edges,edges_back,get_new_state("onDestroy",component_class),get_new_state("onTerminal",component_class))
    return edges,edges_back
def receiver_life(edges,edges_back,component_class ):#original receiver callback
    life_edge_gene( edges,edges_back,get_new_state("<init>",component_class),get_new_state("onReceive",component_class) )
    life_edge_gene(edges,edges_back,get_new_state("onReceive",component_class),get_new_state("onTerminal",component_class))

    return edges,edges_back

def life_edge_gene(edges, edges_back,start, end):
    # add into edges
    if start in edges.keys():
        if [start,end] not in edges[start]:
            edges[start].append([start,end])
    else:
        edges[start] = []
        edges[start].append([start,end])

    # add into  edges_back
    if type(end).__name__=='dict':
        end=get_callback_name_class(end)
        if end in edges_back.keys():
            if [start,end] not in edges_back[end]:
                edges_back[end].append([start,end])
        else:
            edges_back[end] = []
            edges_back[end].append([start,end])
    else:
        if end in edges.keys():
            if [start,end] not in edges_back[end]:
                edges_back[end].append([start,end])
        else:
            edges_back[end] = []
            edges_back[end].append([start,end])
    return edges,edges_back

#replace node with father_node and child_node
def connect_father_child(edges,edges_back,father_node,child_node,node):
    for key in father_node:#
        if type(key).__name__=='str':
            if [key,node] in edges[key]:
                del edges[key][edges[key].index([key,node])]
            if [key,node] in edges_back[node]:
                del  edges_back[node][edges_back[node].index([key,node])]
            for child in child_node:
                if key !=child:
                    life_edge_gene(edges,edges_back,key,child)
        else:

            if [key,node] in edges[get_callback_name_class(key)]:
                del edges[get_callback_name_class(key)][edges[get_callback_name_class(key)].index([key,node])]
            if [key,node] in edges_back[node]:
                del edges_back[node][edges_back[node].index([key,node])]
            for child in child_node:
                if key !=child:
                    non_life_edge_gene(edges,edges_back,key,child)
    return edges,edges_back
def get_final_graph(component_class,super_class):
    edges,edges_back,life_states,non_life_states,callback_collect=get_component_graph(component_class)#得到构建的回调函数调用图

    if super_class.find("Activity")>-1 and not super_class.find("$")>-1:

        no_activity_callback=[]
        for i in activity_callback:
            if i not in callback_collect:
                no_activity_callback.append( "%s %s" %(i,component_class.get_name()))
        # print(no_activity_callback)
        for value in no_activity_callback:
            father_node=get_prenodes(edges_back,value)#
            child_node=get_postnodes(edges,value)#
            edges,edges_back=connect_father_child(edges,edges_back,father_node,child_node,value)
        for i in no_activity_callback:
            del edges[i]
        copy_edges=copy.deepcopy(edges)
        for key in copy_edges.keys():
            for value in copy_edges[key]:
                if get_callback_name_class(value[0])!=key:
                    del edges[key][edges[key].index(value)]

    elif super_class.find("Service")>-1:
        no_service_callback=[]
        for i in service_callback:
            if i not in callback_collect:
                no_service_callback.append( "%s %s" %(i,component_class.get_name()))
        for value in no_service_callback:
            father_node=get_prenodes(edges_back,value)
            child_node=get_postnodes(edges,value)
            edges,edges_back=connect_father_child(edges,edges_back,father_node,child_node,value)
        for i in no_service_callback:
            if i in edges.keys():
                del edges[i]
        # print(edges)
        copy_edges=copy.deepcopy(edges)
        for key in copy_edges.keys():
            for value in copy_edges[key]:
                if get_callback_name_class(value[0])!=key:
                    del edges[key][edges[key].index(value)]
        # for key in edges.keys():
        #     print('....................')
        #     print(key)
        #     for i in edges[key]:
        #         print(i)

    elif super_class.find("BroadcastReceiver")>-1:
        no_receiver_callback=[]
        for i in receiver_callback:
            if i not in callback_collect:
                no_receiver_callback.append( "%s %s" %(i,component_class.get_name()))

        for value in no_receiver_callback:
            father_node=get_prenodes(edges_back,value)
            child_node=get_postnodes(edges,value)
            edges,edges_back=connect_father_child(edges,edges_back,father_node,child_node,value)
        for i in no_receiver_callback:
            del edges[i]
        # print(edges)
        copy_edges=copy.deepcopy(edges)
        for key in copy_edges.keys():
            for value in copy_edges[key]:
                if get_callback_name_class(value[0])!=key:
                    del edges[key][edges[key].index(value)]
        # for key in edges.keys():
        #     print('....................')
        #     print(key)
        #     for i in edges[key]:
        #         print(i)
    return edges,edges_back
#get prenodes of node in graph
def get_prenodes(edges_back,end_node):
    prenodes = []
    if end_node in edges_back.keys():
        for edge in edges_back[end_node]:
            prenodes.append(edge[0])
    return prenodes
#get postnodes of node in graph
def get_postnodes(edges,start_node):
    postnodes = []
    if start_node in edges.keys():
        for edge in edges[start_node]:
            postnodes.append(edge[1])
    return postnodes

def iter_dfs(G,s):
    S,Q=set(),[]
    Q.append(s)
    while Q:
        u = Q.pop()
        if u in S:continue
        S.add(u)
        if u not in G.keys():
            G[u]={}
        Q.extend(G[u])
        yield u
def Read_amd_data(path):
    allFiles = []
    if os.path.isdir(path):
        fileList = os.listdir(path)
        for f in fileList:
            f = path + '\\' + f
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

    for _, _dirs, _ in os.walk(path):

        for dir in _dirs:
            for root,dirs,files in os.walk(path+'\\'+dir):
                for file in files:
                    if os.path.splitext(file)[1] == '.apk':
                        APK_path.append(path+'\\'+dir+'\\'+file)
    return APK_path
def Deal_all_not_amd_data():
    path='F:\\seprated_apks'
    apk_path=Read_All_APK(path)
    csvfile = open('E:/apk_method_code/callback_method_not_amd.csv', 'wt' ,encoding="UTF8",newline='')
    writer=csv.writer(csvfile, delimiter=",")
    for path in range(len(apk_path)):
        print(apk_path[path])
        try:
            get_states(apk_path[path],writer)
        except Exception:

            path += 1
    path1='E:\\APK_数据下载'
    apk_path=Read_All_APK(path1)
    for path in range(len(apk_path)):
        print(apk_path[path])
        try:
            get_states(apk_path[path],writer)
        except Exception:

            path += 1
def Deal_all_amd_data():
    path = 'F:\\amd_data'
    all_amd_path = Read_amd_data(path)
    csvfile = open('E:/apk_method_code/callback_method1.csv', 'wt' ,encoding="UTF8",newline='')
    writer=csv.writer(csvfile, delimiter=",")
    for path in range(len(all_amd_path)):
        print(all_amd_path[path])
        try:
            get_states(all_amd_path[path],writer)
        except Exception:

            path += 1
if __name__ == "__main__":
    apk_path='F:\\amd_data\\Airpush\\variety1\\0b4bd8dc61ab8df5a42b3c1d83d2821a.apk'
    Deal_all_amd_data()
