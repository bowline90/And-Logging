class DexFile:
	class Header:
		MagicNumber=""




def decompiler(name):
	f=open(name,"rb")		
	try:
		byte=f.read(4)