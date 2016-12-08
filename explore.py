import os
import sys
from lib.clax import clax
from settings import *
from lib.method import metodo
from lib.util import *
from subprocess import check_call
from shutil import copyfile


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
	print "Welcome to logger for Android. This is a simply PoC (for now).\nThis script works only with one device attached (for now).\nPlease run this script inside the directory created by ApkTool to avoid a lot of problems"
	print "\n\n\n"
	path=".\\"
	if len(sys.argv) == 2:
		path=sys.argv[1]
	else:
		path=os.getcwd()
	print "Working path:\t"+path
	raw_input("The working path is correct? Press enter to continue, CTRL+C to interrupt")
	print "\n\n"
	conf=Settings()
	conf.defineSetting()
	print conf
	raw_input("The settings are correct? Press enter to continue, CTRL+C to interrupt")
	glob={}
	package=""
	print "Searching for logging comments. This can take a while..."
	for root, dirs, files in os.walk(path):
		for name in files:
			if name.endswith((".smali")):
				localpath=os.path.join(root,name)
				ReadFile(localpath,glob)
	package=ParseManifest(path)
	if package is None:
		print "AndroidManifest doesn't found.\nExiting..."
		return
	ParseClax(glob)
	raw_input("\n\nWrite over file? This process can modify the smali class. Ctrl+C to interrupt")
	for cla in glob:
		myclx=glob[cla]
		if myclx.isModified():
			out=open(myclx.getFilename(),"w")
			#out=sys.stdout
			myclx.WriteClax(out)
	injection=path+"\\smali\\com\\injected\\"
	if not os.path.exists(injection):
		os.makedirs(injection)
	src=os.path.dirname(os.path.abspath(__file__))+"\\injected\\Logger.smali"
	copyfile(src, injection+"\\Logger.smali")
	raw_input("SMALI modified...\n\nBuilding APK? Press enter to continue, CTRL+C to interrupt")
	subp=conf.getApk()+"\\apktool.bat"
	check_call([subp,'b','.'])
	raw_input("\n\nSign the APK? Press enter to continue, CTRL+C to interrupt")
	subp=conf.getJava()+"\\jarsigner"
	name=path.split("\\")[-1]+".apk"
	alias=raw_input("Alias name for signing? ")
	check_call([subp,'-verbose', '-sigalg', 'SHA1withRSA', '-digestalg', 'SHA1', '-keystore', conf.getCert(), path+"\\dist\\"+name, alias])
	print("APK signed\n\n")
	s=raw_input("Remove APK from device?[Y/N]")
	subp=conf.getSdk()+"\\adb"
	if s=="Y" or s=='y':
		check_call([subp,'uninstall',package])
	raw_input("\n\nInstall Apk in the device? Press enter to continue, CTRL+C to interrupt")
	check_call([subp,'install',path+"\\dist\\"+name])
	raw_input("\n\nExecuting application and log parameters? Press enter to continue, CTRL+C to interrupt")
	#Start logcat
	
	
	

if __name__ == "__main__":
		main()