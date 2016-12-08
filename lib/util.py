from lib.method import metodo

def decodeType(line):
	index=0
	returned=[]
	while index < len(line):
		type=line[index]
		if type=='L':
			#this is a class
			index+=1
			while line[index] !=";":
				type+=line[index]
				index+=1
			type+=line[index]
			index+=1
			#print type
			returned.append(type)
		elif type=='[':
			if line[index+1]=='L':
				#array di classi
				index+=1
				while line[index] !=";":
					type+=line[index]
					index+=1
				type+=line[index]
				index+=1
				returned.append(type)
			else:
				index+=1
				type+=line[index]
				index+=1
				returned.append(type)
		else:
			returned.append(type)
			index+=1
		if type=='':
			print "empty"
			continue
	return returned
	
def CreateLogMethod(glob,clax,msg,tag):
	klm=metodo()
	prol=".method public LogInjection(Ljava/lang/String;Ljava/lang/String;)V"
	klm.addCommand(prol)
	klm.addName(prol.replace(".method","").strip())
	prol=".param p1 #TAG"
	klm.addCommand(prol)
	prol=".param p2 #msg"
	klm.addCommand(prol)
	prol=".locals 1\n"
	klm.addCommand(prol)
	klm.setMsg(msg,4)
	klm.setTag(tag,5)
	v=klm.getTag()
	v+=1
	v="v"+str(v)
	for field in clax.getField():
		type=field.split()[-1].split(":")[-1]
		name=field.split()[-1].split(":")[0]
		if type[0]!='L':
			type=type[:-1]
		if type[0]=='L':
			prol=LogMethod(glob,klm,type,"Class",msg,tag,v)
		elif type[0]=='[':
			if type[1]=='L':
				proll=LogMethod(glob,klm,type,"Carray",msg,tag,v)
			else:
				proll=LogMethod(glob,klm,type,"Parray",msg,tag,v)
		else:
			proll=LogMethod(glob,klm,type,"Primitive",msg,tag,v)
		if "static" in field:
			prol="sget "+v+", "+clax.getName()+"->"+name+":"+type
		else:
			prol="iget "+v+", p0, "+clax.getName()+"->"+name+":"+type
		klm.addCommand(prol)
		klm.addCommand(proll)
	prol=".end method"
	klm.addCommand(prol)
	clax.addCommand(klm)
		
def LogMethod(glob,clax,type,mtype,msg,tag,i):
	if mtype=="Class":
		if type=="Ljava/lang/String;":
			s="invoke-static {v"+str(clax.getTag())+", v"+str(clax.getMsg())+", "+i+"}, Lcom/injected/Logger;->Log(Ljava/lang/String;Ljava/lang/String;"+type+")V"
		else:
			if type in glob:
				s="invoke-virutal {"+str(i)+", v"+str(clax.getTag())+", v"+str(clax.getMsg())+"}, "+type+"->LogInjection(Ljava/lang/String;Ljava/lang/String;)V"
				clx1=glob[type]
				clx1.setModified(None)
				msg=msg+":"+type
				meth=CreateLogMethod(glob,clx1,msg,tag)
			else:
				s="#This class is an API?"
		return s
	if mtype=="Primitive":
		s="invoke-static {v"+str(clax.getTag())+", v"+str(clax.getMsg())+", "+i
		if type=='J' or type=='D':
			param=i[0]
			s1=i[1:]
			s1=int(s1)
			s1+=1
			s1=", "+param+str(s1)
		else:
			s1=""
		s+=s1+"}, Lcom/injected/Logger;->Log(Ljava/lang/String;Ljava/lang/String;"+type+")V"
		return s
	if mtype=="Carray":
		if type=="[Ljava/lang/String;":
			s="invoke-static {v"+str(clax.getTag())+", v"+str(clax.getMsg())+", "+i+"}, Lcom/injected/Logger;->Log(Ljava/lang/String;Ljava/lang/String;"+type+")V"
		else:
			s="THIS IS ANOTHER ARRAY OF CLASS"
		return s
	if mtype=="Parray":
		s="invoke-static {v"+str(clax.getTag())+", v"+str(clax.getMsg())+", "+i+"}, Lcom/injected/Logger;->Log(Ljava/lang/String;Ljava/lang/String;"+type+")V"
		return s
	
	
def insertLogParameter(glob, clax,msg,tag):
		returned=[]
		line=clax.getName()
		par=line.strip()
		par=par.split("(")[1].split(")")[0]
		type=decodeType(par)
		#print type
		if "static" in line:
			index=0
		else:
			index=1
		for log in type:
			i="p"+str(index)
			if log[0]=='L':
				#LOG CLASS	
				returned.append(LogMethod(glob,clax,log,"Class",msg,tag,i))
			elif log[0]=='[':
				if log[1] is not None and log[1]=='L':
					#Array class
					returned.append(LogMethod(glob,clax,log,"Carray",msg,tag,i))
				else:
					#array integer
					returned.append(LogMethod(glob,clax,log,"Parray",msg,tag,i))
			else:
				#primitive
				returned.append(LogMethod(glob,clax,log,"Primitive",msg,tag,i))
				if log[0]=='J' or log[0]=='D':
					index+=1
			index+=1
		return returned