# Callback2Vec
A callback based hierarchical embedding approach for Android app.
# Basic Usage
- For Callback2Vec its usage is as follows:
- First you need to run Callback2Vec/src/Callback2Vec/Get_APK_Source.py to get the source code for all apks，
- Run Callback2Vec/src/MyRcpView/src/APK_AST/Method_AST_Nodes.java to convert all APK sources to AST nodes，
  Example:
  for code snippets:
  >public static void main(String[] args) {
        >for (int i = 0; i < args.length; i++) {
            >try {
                >String doc = URLGrabber.getDocumentAsString(args[i]);
                >System.out.println(doc);
            >} catch (MalformedURLException e) {
                >System.err.println(args[i] + " cannot be interpreted as a URL.");
            >} catch (IOException e) {
                >System.err.println("Unexpected IOException: " + e.getMessage());
            >}
        >}
    >}
- you need to import the jar package under the Lib folder and install Eclipse RCP IDE to run Method_AST_Nodes.java
  file.
- Run Callback2Vec/src/Callback2Vec//Build_Callback_Graph.py in the normal way of running.Py files to get callback 
  function call graph of an apk,run randWalk.py obtains callback function sequence by random walk callback function graph.
- To train model
$ python train.py
- To get embedding of APK from an  existing model
$ python eval.py
# Requirements
Install requirements.txt file to make sure correct versions of libaraies are being used
- Python 3.5.x
- networkx==2.2
- numpy==1.15.2
- gensim==3.6.0
- tensorflow>=1.12.1
- matplotlib==3.0.0
- androguard==3.2.1
- Eclipse RCP Oxygen.3a Release (4.7.3a)
