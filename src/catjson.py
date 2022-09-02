import json, os, glob

def catjson(target,path,base):
	"""
	@brief      { Concatenates json files into one object with one array }
	
	@param      target  The target json file
	@param      base    The base of the source filename
	@param      path    The path to the source file
	
	@return     { The array with all json files }
	"""
	files=[]
	for filename in glob.glob(os.path.join(path, base)):
		with open(filename) as f:
			files.append(json.load(f))
	with open(target,"w") as t:
		t.write(json.dumps({"data":files},indent=4))
	return files

