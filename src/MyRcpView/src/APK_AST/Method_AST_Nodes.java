package APK_AST;

import java.io.File;  
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.io.BufferedReader;  
import java.io.BufferedWriter;  
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException; 

public class Method_AST_Nodes {
	
	public static ArrayList<String> filepath1_list = new ArrayList<String>();
	public static ArrayList<String> filepath2_list = new ArrayList<String>();
	
	
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub

		String method_path="F:\\2018年第一学年科研\\APK科研\\笔记本资料\\AST_抽象语法树\\103.java";
		ASTParserTool parserTool1 = new ASTParserTool();
		MethodList methodVectorList1 = new MethodList();
		System.out.println(method_path);
		methodVectorList1 = parserTool1.parseMethod(method_path);
//		for(int m=0;m<methodVectorList1.size();m++) {
////			System.out.println(m);
//			methodVectorList1.getMethodVector(m).print();
//			
//		}
		for(int i=0;i<ASTParserTool.method_key_word.size();i++) {
			System.out.println(ASTParserTool.method_key_word.get(i));
		}
	}
	public static void ReadCSV(BufferedReader reader,ArrayList<String> list1, ArrayList<String> file_list,String directory_path) throws IOException {
		reader.readLine();//
        String line = null; 
        while((line=reader.readLine())!=null){ 
            String item[] = line.split(",");//
             
            String filename = item[1];//
            String startline = item[2];
            String endline = item[3];
            
            if(!list1.contains(filename)) {
            	list1.add(filename);
            	String file_path = findFiles(directory_path,filename,file_list);
            	
            }           
        }
	}
	private static String findFiles(String Source_path, String filename , ArrayList<String> absolute_path_list) {
		// TODO Auto-generated method stub
		String result = null;
		String tempName = null;  
		File baseDir = new File(Source_path); 
		if (!baseDir.exists() || !baseDir.isDirectory()){  
            System.out.println("File search failed：" + Source_path + "not a directory！");  
        } 
		else {
			 String[] filelist = baseDir.list();  
	            for (int i = 0; i < filelist.length; i++) {  
	                File readfile = new File(Source_path + "\\" + filelist[i]);  
	                //System.out.println(readfile.getName());  
	                if(!readfile.isDirectory()) {  
	                    tempName =  readfile.getName();   
	                    if (tempName.equals(filename)) {  
	                        
	                    result = readfile.getAbsolutePath();          
	                    absolute_path_list.add(result);
//	                    System.out.println(result);  
	                    }  
	                } 
	                else if(readfile.isDirectory()){  
	                    findFiles(Source_path + "\\" + filelist[i],filename,absolute_path_list);  
	                }  
	            }
		}
		
		return result;
	}
}