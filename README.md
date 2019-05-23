# Callback2Vec
A callback based hierarchical embedding approach for Android app.
# Basic Usage
The Callback2Vec can be used as following steps:
- Run Callback2Vec/src/Callback2Vec/Get_APK_Source.py to get the source code for apks
- Run Callback2Vec/src/MyRcpView/src/APK_AST/Method_AST_Nodes.java to convert the source code to AST nodes 
  Example:
  
  For code snippets:
  
  > public static void main(String[] args) {
  >    for (int i = 0; i < args.length; i++) {
  
  >      try {
  >              String doc = URLGrabber.getDocumentAsString(args[i]);
  >              System.out.println(doc);
  >          } catch (MalformedURLException e) {
  >              System.err.println(args[i] + " cannot be interpreted as a URL.");
  >          } catch (IOException e) {
  >              System.err.println("Unexpected IOException: " + e.getMessage());
  >          }
  >       }
  > }
  
  The AST nodes are obtained as follows:
  
  Type     | Value
  -------- | -----
  ReservedWord  | for
  ReservedWord  | try
  ReservedWord  | catch
  PrimitiveTypeToken  | int
  QualifiedName  | args.length
  SimpleTypeToken  | String
  FunctionName  | getDocumentAsString
  Variable  | URLGrabber
  FunctionName  | println
  QualifiedName  | System.out
  SimpleTypeToken  | MalformedURLException
  FunctionName  | println
  QualifiedName  | System.err
  StringLiteral  | " cannot be interpreted as a URL."
  SimpleTypeToken  | IOException
  FunctionName  | println
  QualifiedName  | System.err
  StringLiteral  | "Unexpected IOException: "
  FunctionName  | getMessage
- Note: import the jar package under the Lib folder and install Eclipse RCP IDE to run the Method_AST_Nodes.java file
- Run Callback2Vec/src/Callback2Vec//Build_Callback_Graph.py in the normal way of running.Py files to get Callback Graph of an apk, run randWalk.py to obtain the callback sequences by random walk on the Callback Graph
- Run python train.py to train the proposed model
- Run python eval.py to get embedding of APK from an existing model
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
