import os
import sys
from lib.clax import clax
from lib.method import metodo
from lib.util import *
from subprocess import call

#Parse classes in order to find LOG
def ParseClax(glob):
	for clasn in glob:
		klx=glob[clasn]
		met=klx.getLogMethod()
		for klm in met:
			com=klm.getCommand()
			index=0
			while index < len(com):
				line=com[index]
				index+=1
				if "#LOG" in line or "#log" in line:
					if line.split()[1] == "parameters" or line.split()[1]=="PARAMETERS":
						#print "Log Parameters"
						msg=klx.getName()+"->"+klm.getName()
						tag="InjectionLoggerParam"
						klm.setMsg(msg,index)
						klm.setTag(tag,index)
						ret=insertLogParameter(glob,klm,msg,tag)
						index+=2
						ind=index
						for ins in ret:
							com.insert(ind,ins)
							ind+=1
						com.insert(ind,"#END LOG PARAMETERS")
					if line.split()[1] == "stack" or line.split()[1]=="STACK":
						msg=klx.getName()+"->"+klm.getName()
						tag="InjectionLoggerStack"
						klm.setMsg(msg,index)
						klm.setTag(tag,index)
						index+=2
						s="invoke-static {v"+str(klm.getTag())+", v"+str(klm.getMsg())+"}, Lcom/injected/Logger;->LogTrace(Ljava/lang/String;)V"
						com.insert(index,s)
						com.insert(index+1,"#END LOG STACK")

#Reading and prepare classes from smali
def ReadFile(name,globclax):
	klx=clax()
	klx.InsertFilename(name)
	with open(name,"r") as f:
		insidemethod=False
		for line in f:
			if line=="\n":
				continue
			line=line.strip()
			if insidemethod==True and "#LOG" in line or "#log" in line:
				klx.setModified(klm)
				klm.addCommand(line+" OK")
				continue
			elif insidemethod==True and ".end method" not in line:
				klm.addCommand(line)
				continue
			elif ".end method" in line:
				klm.addCommand(line)
				insidemethod=False
				klx.addCommand(klm)
				continue
			elif ".method" in line:
				klm=metodo()
				klm.addName(line.replace(".method","").strip())
				klm.addCommand(line)
				insidemethod=True
				continue
			elif ".class" in line:
				y=line.replace(".class","").strip()
				y=y.split()[-1]
				klx.InsertName(y)
				klx.addCommand(line)
				continue
			elif ".super" in line:
				klx.InsertSuper(line.replace(".super","").strip())
				klx.addCommand(line)
				continue
			elif ".field" in line:
				klx.InsertField(line.replace(".field","").strip())
				klx.addCommand(line)
				continue
			else:
				klx.addCommand(line)
				continue
	globclax[klx.getName()]=klx


def ParseManifest(path):
	for root, dirs, files in os.walk(path):
		for name in files:
			if name=="AndroidManifest.xml":
				localpath=os.path.join(root,name)
				with open(localpath,"r") as f:
					for line in f:
						if "package" in line:
							line=line.strip().split()
							for find in line:
								if "package" in find:
									s=find.split("=")[1].replace("\"","")
									return s
				
	
def main():
	path=".\\app-debug"
	glob={}
	package=""
	for root, dirs, files in os.walk(path):
		for name in files:
			if name.endswith((".smali")):
				localpath=os.path.join(root,name)
				ReadFile(localpath,glob)
	package=ParseManifest(path)
	print package
	ParseClax(glob)
	print "Write over file? This process can modify the smali class. Ctrl+C to interrupt"
	raw_input()
	for cla in glob:
		myclx=glob[cla]
		if myclx.isModified():
			out=open(myclx.getFilename(),"w")
			#out=sys.stdout
			myclx.WriteClax(out)
	#call(["apktool","b "+path])
	

if __name__ == "__main__":
    main()