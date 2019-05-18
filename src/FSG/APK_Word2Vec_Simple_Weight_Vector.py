from APK_Method_Analysis import *
from WordEmbedding import *
import math
def Get_Method_Words(method_,class_,class_code_dic):
    method_words=[]
    method_words+=class_code_dic[class_.get_name()][method_.get_name() + method_.get_descriptor()]
    return method_words
def Get_Class_Words(class_,CFG,dx,class_code_dic):
    all_orig_methods = []
    class_all_words = []
    for m in dx.find_methods(classname=class_.get_name()):
        orig_method = m.get_method()
        if isinstance(orig_method, ExternalMethod):
            is_this_external = True
        else:
            is_this_external = False
        CFG.add_node(orig_method, external=is_this_external)
        if not isinstance(orig_method, ExternalMethod):
            all_orig_methods.append(orig_method)
    for m in dx.find_methods(classname=class_.get_name()):
        orig_method = m.get_method()
        if not isinstance(orig_method, ExternalMethod):
            if (orig_method.get_name() in all_callback) or (
                    orig_method.get_name() in APK_Method_Key_Words.key_registers):
                # print(class_code_dic[k.get_name()][orig_method.get_name()+orig_method.get_descriptor()])
                class_all_words.append(class_code_dic[class_.get_name()][orig_method.get_name() + orig_method.get_descriptor()])
    return class_all_words
def Get_APK_Words(apkfile):
    a = apk.APK(apkfile, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apkfile)
    CFG = nx.DiGraph()
    apk_all_words=[]
    class_code_dic, is_amd_class_code_dic = Build_APK_Corpus(apkfile)
    for k in d.get_classes():
        class_all_words = Get_Class_Words(k, CFG, dx, class_code_dic)
        if len(class_all_words) != 0:
            apk_all_words.append(class_all_words)
    return apk_all_words

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
def get_class_vector(class_method,model,embedding_size):

    class_vector = [0 for i in range(embedding_size)]
    num = len(class_method)
    if num == 0:
        num = 1
    for method_sentence in class_method:
        method_vector = get_method_vector(method_sentence, model, embedding_size)
        class_vector = [class_vector[i] + method_vector[i] for i in range(len(method_vector))]
    class_vector = [i / num for i in class_vector]
    return class_vector
def get_apk_vector(apk_classes,model,embedding_size):
    num = len(apk_classes)
    if num == 0:
        num = 1
    apk_vector = [0 for i in range(embedding_size)]
    for apk_class in apk_classes:
        class_vector = get_class_vector(apk_class, model, embedding_size)
        apk_vector = [apk_vector[i] + class_vector[i] for i in range(len(class_vector))]
    apk_vector = [i / num for i in apk_vector]
    return apk_vector
def Analysis_All_Apk(apkfile,writer):
    a = apk.APK(apkfile, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apkfile)
    CFG = nx.DiGraph()
    apk_all_words = []
    class_code_dic, is_amd_class_code_dic = Build_APK_Corpus(apkfile)
    for k in d.get_classes():
        # print(k.get_superclassname())
        writer.writerow([k.get_superclassname()+'::'+k.get_name()])
        for m in dx.find_methods(classname=k.get_name()):
            orig_method = m.get_method()
            if not isinstance(orig_method, ExternalMethod):
                if (orig_method.get_name() in all_callback) or (
                        orig_method.get_name() in APK_Method_Key_Words.key_registers):
                    # writer.writerow(orig_method.get_source())

                    # print(orig_method.get_name() + '::' + orig_method.get_descriptor())
                    writer.writerow([orig_method.get_name() + '::' + orig_method.get_descriptor()+'::'])
                    writer.writerow([orig_method.get_name()+orig_method.get_descriptor()]+class_code_dic[k.get_name()][orig_method.get_name() + orig_method.get_descriptor()])
                    # print(class_code_dic[k.get_name()][orig_method.get_name() + orig_method.get_descriptor()])
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

def Deal_all_amd_data():
    model_path = 'D:\\APK_科研\\word2vec\\apk_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    # print(model)
    with open('D:\\APK_科研\\word2vec\\apk_vector.csv', 'w', newline='')as csvfile:
        writer = csv.writer(csvfile)
        path = 'D:\\APK_科研\\数据集\\DroidKungFu\\amd\\'
        writer.writerow([path])
        all_amd_path = Read_amd_data(path)
        for path in range(len(all_amd_path)):
            print(all_amd_path[path])
            writer.writerow([all_amd_path[path]])
            try:
                apk_word = Get_APK_Words(all_amd_path[path])
                # print(apk_word)
                apk_vector = get_apk_vector(apk_word, model, 64)
                print(apk_vector)
                writer.writerow(apk_vector)
            except Exception:
                print('出错')
                path += 1
def Deal_All_APK():
    APK_path=Read_All_APK()
    # my_corpus = WordEmbedding.get_corpus()  #
    model_path='F:\\apk_trained_word2vec.model'
    model=get_already_word2vec_model(model_path)
    with open('F:/Word2vec_ao_yuliaoku/apk_vector.csv', 'w', newline='')as csvfile:
        writer=csv.writer(csvfile)
        for path in APK_path:
            print(path)
            # Build_Class_Word2Vec(path)
            apk_word = Get_APK_Words(path)
            apk_vector = get_apk_vector(apk_word, model, 64)
            print(apk_vector)
            writer.writerow([path])
            writer.writerow(apk_vector)
        # writer.writerow()
        path = 'F:\\amd_data'
        writer.writerow([path])
        all_amd_path = Read_amd_data(path)
        for path in range(len(all_amd_path)):
            print(all_amd_path[path])
            try:
                apk_word = Get_APK_Words(all_amd_path[path])
                apk_vector = get_apk_vector(apk_word, model, 64)
                print(apk_vector)
                writer.writerow([all_amd_path[path]])
                writer.writerow(apk_vector)
            except Exception:

                path += 1
def Read_All_APK():
    APK_path=[]
    path='F:\\seprated_apks\\'
    for _, _dirs, _ in os.walk(path):

        for dir in _dirs:
            for root,dirs,files in os.walk(path+'\\'+dir):
                for file in files:
                    if os.path.splitext(file)[1] == '.apk':
                        APK_path.append(path+'\\'+dir+'\\'+file)
    return APK_path
def Analysis():
    path = 'D:\\DroidKungFu\\amd\\'
    all_amd_path = Read_amd_data(path)

    with open('D:\\word2vec\\apk_vector2.csv', 'w', newline='')as csvfile:
        writer = csv.writer(csvfile)

        for path in range(len(all_amd_path)):
            print(all_amd_path[path])
            try:
                writer.writerow([all_amd_path[path]])
                Analysis_All_Apk(all_amd_path[path],writer)
            except Exception:

                path += 1
def Test_Analysis_All_APK(apkfile):
    a = apk.APK(apkfile, False, 'r', None, 2)
    d = dvm.DalvikVMFormat(a.get_dex())
    vmx = analysis.Analysis(d)
    dp = decompiler.DecompilerDAD(d, vmx)
    a1, d1, dx = AnalyzeAPK(apkfile)
    CFG = nx.DiGraph()
    apk_all_words = []
    class_code_dic, is_amd_class_code_dic = Build_APK_Corpus(apkfile)
    for k in d.get_classes():
        # print(dp.get_source_class(k))
        print('super_class+class::'+k.get_superclassname() + '::' + k.get_name())
        for m in dx.find_methods(classname=k.get_name()):
            orig_method = m.get_method()
            if not isinstance(orig_method, ExternalMethod):
                if (orig_method.get_name() in all_callback) or (
                        orig_method.get_name() in APK_Method_Key_Words.key_registers):
                    print('method::'+orig_method.get_name() + '::' + orig_method.get_descriptor() + '::')
                    print([orig_method.get_name() + orig_method.get_descriptor()] + class_code_dic[k.get_name()][
                            orig_method.get_name() + orig_method.get_descriptor()])

                    # print(orig_method.get_source())


def test():
    path = 'D:\\amd\\04bb304f81e8312873838215b8a69c6a.apk'
    Test_Analysis_All_APK(path)
def Cosin_Simility(vector1,vector2):
    vector=[0 for i in range(len(vector1))]
    print(vector2)
    print(vector1)
    for i in range(len(vector1)):
        vector[i]=float(vector1[i])-float(vector2[i])
    sum=0.0
    for i in range(len(vector)):
        sum+=pow(vector[i],2)
    sum=math.sqrt(sum)
    print(sum)
if __name__ == "__main__":
    # print(model)
    # Deal_all_amd_data()
    # Analysis()
    # # test()
    model_path = 'F:\\Word2vec_ao_yuliaoku\\apk_trained_word2vec.model'
    model = get_already_word2vec_model(model_path)
    # m1=['onFailure','Lbracket',	'Lcom','lidroid','xutils','exception','HttpException','Ljava','lang','String','Rbracket','void']
    # m2=['onSuccess','Lbracket','Lcom','lidroid','xutils','http','ResponseInfo','Rbracket','void']
    m1=['onActivityStarted',	'Lbracket'	,'Landroid',	'app',	'Activity',	'Rbracket',	'void']
    m2=['onActivityCreated',	'Lbracket',	'Landroid',	'os',	'Bundle',	'Rbracket',	'void']
    m3=['startService', 'Lbracket',	'Landroid',	'content',	'Context',	'Rbracket', 'int']
    m4=['stopService',	'Lbracket',	'Rbracket',	'void']
    v1=get_method_vector(m2,model,32)
    v2=get_method_vector(m4,model,32)
    Cosin_Simility(v1,v2)
