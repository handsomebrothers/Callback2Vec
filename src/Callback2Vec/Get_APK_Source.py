import csv
from androguard.misc import AnalyzeAPK
from androguard.core.analysis.analysis import ExternalMethod
import matplotlib.pyplot as plt
import networkx as nx
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard.decompiler import decompiler
import os
import re
from androguard.core.bytecodes import dvm_types
def write_one_apk_source(apkfile,key):
    a = apk.APK(apkfile, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apkfile)
    CFG = nx.DiGraph()
    with open('E:/111/'+key+'.txt', 'w',encoding='utf-8') as txtData:
        for k in d.get_classes():
            print('class_name:' + k.get_name())
            txtData.writelines(dp.get_source_class(k))
            for m in dx.find_methods(classname=k.get_name()):
                orig_method = m.get_method()
                if isinstance(orig_method, ExternalMethod):
                    is_this_external = True
                else:
                    is_this_external = False
                CFG.add_node(orig_method, external=is_this_external)
                if is_this_external == False:
                    print('orig::' + orig_method.get_name())
                else:
                    print('orig+external::'+orig_method.get_name())
                for other_class, callee, offset in m.get_xref_to():
                    if isinstance(callee, ExternalMethod):
                        is_external = True
                    else:
                        is_external = False
                    if callee not in CFG.node:
                        CFG.add_node(callee, external=is_external)
                        if is_external == False:
                            print('external+callee::' + callee.get_name())
                        else:
                            print('callee:' + callee.get_name())
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
if __name__ == "__main__":

    all_path=Read_All_APK('F:/1/')
    for path in all_path:
        a=re.split('/',path)
        print(a)
        print(a[7]+'_'+a[8])
        write_one_apk_source(path,a[7]+'_'+a[8])
