import os
import sys
from lib.clax import clax
from settings import *
from lib.method import metodo
from lib.util import *
from lib.LogCat import *
from subprocess import check_call
from subprocess import Popen
from subprocess import PIPE
from shutil import copyfile
import xml.etree.ElementTree as ET


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
						com[index-1]="#LOGGED PARAMETERS"
						msg=klx.getName()+":"+klm.getName()
						tag="InjectionLogger"
						klm.setMsg(msg,index)
						klm.setTag(tag,index)
						ret=insertLogParameter(glob,klm,msg,tag)
						index+=1
						ind=index
						for ins in ret:
							com.insert(ind,ins)
							ind+=1
						com.insert(ind,"#END LOG PARAMETERS")
					if line.split()[1] == "stack" or line.split()[1]=="STACK":
						msg=klx.getName()+"->"+klm.getName()
						tag="InjectionLogger"
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
			if line=="\n" or line.strip()=="":
				continue
			line=line.strip()
			if insidemethod==True and line.split()[0]=="#LOG" or line.split()[0]=="#log":
				klx.setModified(klm)
				klm.addCommand(line)
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
	returned={}
	tree = ET.parse(path+"\\AndroidManifest.xml")
	root = tree.getroot()
	#namespace=root.get('android')
	namespace="{http://schemas.android.com/apk/res/android}"
	returned['package']=root.get('package')
	act=''
	cat=''
	for tag in root.iter('activity'):
		name=tag.get(namespace+'name')
		for tag2 in tag.iter('action'):
			act=tag2.get(namespace+'name')
			if act=="android.intent.action.MAIN":
				break
		for tag2 in tag.iter('category'):
			cat=tag2.get(namespace+'name')
			if cat=="android.intent.category.LAUNCHER":
				break		
		if act=='android.intent.action.MAIN' and cat=='android.intent.category.LAUNCHER':
			returned['main']=name
			break
	return returned
				
def ParseLogcat(log,tag,file):
	logclass=Logcat()
	for line in log.split("\n"):
		if tag in line:
			tags=line.split(":")[0]
			line=line.replace(tags+":","").strip()
			logclass.addLog(line)

def StartLog(conf,package):
	print("\n\nExecuting application and log parameters...")
	#Start logcat
	subp=conf.getSdk()+"\\adb"
	check_call([subp,'logcat','-c'])
	#am start intent -> To start main activity
	#Check if the process is already running
	while True:
		process=Popen([subp,'shell','ps', '|', 'grep', package['package']], stdout=PIPE)
		log=process.stdout.read()
		pid=log.split()[1]
		check_call([subp,'shell','kill', pid])
		if log=="":
			break
		print "Please, stop the running process before starting new one...\nPress <Enter> when ready"
		raw_input()
	check_call([subp,'shell','am', 'start', '-n', package['package']+"/"+package['main']])
	#process=Popen([subp,'shell','ps', '|', 'grep', package['package']], stdout=PIPE)
	#log=process.stdout.read()
	#pid=log.split()[1]
	#Popen([subp,'logcat', tag+':*'])
	tag="InjectionLogger"
	log=""
	process=Popen([subp,'logcat', '-v','time','-s', tag],stdout=PIPE)
	print "\n\nUse the application until you want. Press enter to continue, CTRL+C to interrupt"
	raw_input()
	process.terminate()
	log=process.stdout.read()
	#file=sys.stdout
	#ParseLogcat(log,tag,file)
	print log	

def Install(conf,package,name,path):
	s=raw_input("Remove APK from device?[Y/N]")
	subp=conf.getSdk()+"\\adb"
	if s!="N" or s!='n':
		check_call([subp,'uninstall',package['package']])
	print("\n\nInstalling Apk in the device...")
	check_call([subp,'install',path+"\\dist\\"+name])
	subp=conf.getSdk()+"\\adb"

def Repack(conf,path):
	print("Building APK...")
	subp=conf.getApk()+"\\apktool.bat"
	check_call([subp,'b','.'])
	print("\n\nSigning the APK using jarsigner...")
	subp=conf.getJava()+"\\jarsigner"
	name=path.split("\\")[-1]+".apk"
	alias=raw_input("Alias name for signing? ")
	check_call([subp,'-verbose', '-sigalg', 'SHA1withRSA', '-digestalg', 'SHA1', '-keystore', conf.getCert(), path+"\\dist\\"+name, alias])
	print("APK signed!!!\n\n")
	return name

def ScanLog(path,glob):
	print "Searching for logging's comments. This can take a while..."
	for root, dirs, files in os.walk(path):
		for name in files:
			if name.endswith((".smali")):
				localpath=os.path.join(root,name)
				ReadFile(localpath,glob)
	ParseClax(glob)
	print("\n\nWriting the smali classes...")
	for cla in glob:
		myclx=glob[cla]
		if myclx.isModified():
			out=open(myclx.getFilename(),"w")
			myclx.WriteClax(out)
			out.close()
	injection=path+"\\smali\\com\\injected\\"
	if not os.path.exists(injection):
		os.makedirs(injection)
	src=os.path.dirname(os.path.abspath(__file__))+"\\injected\\Logger.smali"
	copyfile(src, injection+"\\Logger.smali")
	print("SMALI successfull modified!!\n\n")
	
def main():
	print "Welcome to logger for Android. This is a simply PoC (for now).\nThis script works only with one device attached (for now).\nPlease run this script inside the directory created by ApkTool to avoid a lot of problems"
	print "\n\n\n"
	path=".\\"
	#Allow to define path from cmdline
	if len(sys.argv) == 2:
		path=sys.argv[1]
	else:
		#Else get current path
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
	package=ParseManifest(path)
	if package is None:
		print "AndroidManifest doesn't found.\nExiting..."
		return
	else:
		print "\n\nPackage information:"
		print "\tPackage name:\t"+package['package']
		print "\tMain activity:\t"+package['main']
	o=""
	name=""
	while True:
		print "\n\n\tL. Scan SMALI for logging comment"
		print "\tR. Repack application"
		print "\tI. Install application"
		print "\tS. Starting and logging"	
		print "\tQ. Quit"
		print "\t<Enter>. Perform last action"
		s=raw_input("\t:")
		s=s.upper()
		if s=="\n":
			s=o
		if s=="L":
			#LOGGING
			ScanLog(path,glob)
		if s=="L" or s=="R":
			#REPACK
			name=Repack(conf,path)
		if s=="L" or s=="R" or s=="I":
			#INSTALL
			if name=="":
				print "Please, perform a repack before install APK"
			else:
				Install(conf,package,name,path)
		if s=="L" or s=="R" or s=="I" or s=="S":
			#start & log
			StartLog(conf,package)
		if s=="Q":
			#Quit
			print "\n\nThanks for using Android Logging Application. This software is in alfa phase.\n\nReport bug to andrea.ferraris90@gmail.com or open issue on https://github.com/bowline90/And-Logging.\n\n\tThanks for your supporting\n\n"
			return
		o=s
	
if __name__ == "__main__":
		main()