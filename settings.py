import os.path

class Settings:
	sdkpath=""
	apktoolpath=""
	javapath=""
	certificate=""
	
	def getSdk(self):
		return self.sdkpath
	def getApk(self):
		return self.apktoolpath
	def getJava(self):
		return self.javapath

	def ReadConf(self,f):
		for line in f:
			field=line.split("=")
			if field[0].strip() == "Sdk":
				self.sdkpath=field[1].strip()
			elif field[0].strip() == "Apk":
				self.apktoolpath =field[1].strip()
			elif field[0].strip() == "Java":
				self.javapath=field[1].strip()
			elif self[0].strip=="Certificate":
				self.certificate=field[1].strip()

	def WriteConf(self,f):
		self.sdkpath=raw_input("Please, insert the full path for Android Sdk:")
		self.apktoolpath=raw_input("Please, insert the full path for Apktool:")
		self.javapath=raw_input("Please, insert the full path for Java SDK (for jarsigner):")
		self.certificate=raw_input("Please, insert the full path for your certificate:")
		f.write("Sdk="+self.sdkpath+"\n")
		f.write("Apk="+self.apktoolpath+"\n")
		f.write("Java="+self.javapath+"\n")
		f.write("Certificate="+self.certificate+"\n")
	
	def defineSetting(self, name="init.cfg"):
		if os.path.isfile(name):
			print "TRUE"
			f=open(name,"r")
			self.ReadConf(f)
		else:
			f=open(name,"w")
			self.WriteConf(f)
		f.close()
	