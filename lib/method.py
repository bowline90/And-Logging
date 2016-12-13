class metodo:
	command=[]
	locals={}
	TAG=""
	line=""
	#logconst={
	#	"const/4":"LogShort(Ljava/lang/String;S)V"
	#	"const/16":"LogInteger(Ljava/lang/String;I)V"
	#	"const-string":"LogString(Ljava/lang/String;Ljava/lang/String;)V"
	#	"const-wide/32":"LogLong(Ljava/lang/String;J)V"
	#	"const-wide v"
	#}
	def __init__(self):
		self.command=[]
		self.name=""
		self.locals={}
		self.numlocals=0
		self.locals={}
		self.TAG=0
		self.msg=0
		self.line=""
	def addLocal(self):
		i=self.numlocals
		self.numlocals+=1
		return i
	def setMsg(self,x,index):
		local=self.addLocal()
		y="const-string v"+str(local)+", \""+x+":"
		#self.command.insert(index,y)
		self.msg=local
		self.line=y
	def setTag(self,x,index):
		local=self.addLocal()
		y="const-string v"+str(local)+", \""+x+"\""
		self.TAG=local
		self.command.insert(index,y)
		
	def getMsg(self):
		return self.msg
	def getTag(self):
		return self.TAG
	def getLine(self):
		return self.line
	def addLogCommand(self,inser,index):
		#x="invoke-static {v"+str(self.TAG)+", v"+str(self.msg)+", "+inser
		self.command.insert(index,x)
	
	def addName(self,x):
		self.name=x
	def getName(self):
		return self.name
	def getCommand(self):
		return self.command
	def addCommand(self,line):
		self.command.append(line)
		if ".locals" in line:
			self.numlocals = int(line.split()[1])
		elif "const" in line:
			splitted=line.split()
			self.locals[splitted[1].replace(",","")]=splitted[0]
		elif "move-result" in line:
			splitted=line.split()
			self.locals[splitted[1]]=self.command[-2]
		elif "move" in line:
			splitted=line.split()
			self.locals[splitted[1].split(",")[0]]=line
		elif "new" in line:
			splitted=line.split()
			self.locals[splitted[1].split(",")[0]]=line
	
		
	def ParseType(self,line):
		if line == "const/4":
			return "LogShort(Ljava/lang/String;S)V"
		elif line == "const/16":
			return "LogShort(Ljava/lang/String;S)V"
			
	def PrintData(self):
		print "\t\tName:"+self.name
		print "Locals:"+self.numlocals
		print self.locals
		for line in self.command:
			print line
			
	def __str__(self):
		returned=""
		for line in self.command:
			if ".locals" in line:
				returned+="\t.locals "+str(self.numlocals)
			elif ".method" in line or ".end method" in line:
				returned+=line
			else:
				returned+="\t"+line
			returned+="\n"
		return returned