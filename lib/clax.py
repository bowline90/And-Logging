class clax:
	methodlist=[]
	logmeth=[]
	modified=False
	command=[]
	field=[]
	name=""
	super=""
	filename=""
	def __init__(self):
		self.methodlist=[]
		self.logmeth=[]
		self.field=[]
		self.name=""
		self.super=""
		self.filename=""
		self.modified=False
		self.command=[]
	def setModified(self,meth):
		self.modified=True
		if meth is not None:
			self.logmeth.append(meth)
	def isModified(self):
		return self.modified
	def InsertName(self,nmx):
		self.name=nmx
	def getName(self):
		return self.name
	def InsertFilename(self,nxa):
		self.filename=nxa
	def getFilename(self):
		return self.filename
	def InsertMethod(self, meth):
		self.methodlist.append(meth)
	def getLogMethod(self):
		return self.logmeth
	def InsertSuper(self, sup):
		self.super=sup
	def InsertField(self,line):
		self.field.append(line)
	def getField(self):
		return self.field
	def addCommand(self,line):
		self.command.append(line)
	def PrintClax(self):
		print "Filename:"+self.filename
		print "\tClass name:"+self.name
		print "\tSuperclass name:"+self.super
		print "\tField:"
		for i in self.field:
			print i
		print "\tMethod:"
		for i in self.methodlist:
			print "Self method"
			raw_input()
			i.PrintData()
	def __str__(self):
		return "CLASSE!"
	def WriteClax(self,out):
		for i in self.command:
			out.write(str(i))
			out.write("\n")
		