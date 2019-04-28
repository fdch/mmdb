import json, math, sys, itertools, os
import numpy as np
from functools import reduce
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Varuables -------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
t_Red=[] # store indices for red threshold
t_Gre=[] # store indices for green threshold
t_Blu=[] # store indices for blue threshold
t_Col=[] # store indices for color threshold (avg rgb)
t_Hiq=[] # store indices for histogram quantile threshold
t_Bdy=[] # store indices for body (threshold by size)
t_Fac=[] # store indices for faces (threshold by size)
t_Smo=[] # store indices for smoothness threshold
t_Cut=[] # store indices for cutness threshold
t_Blo=[] # store indices for blobiness threshold
t_Skw=[] # store indices for skewness threshold
t_Bou=[] # store indices for boundedness of circles
t_Kon=[] # store indices for keypoints contrast
#------------------------------------------------------------------------------
entries=[] # store all entries from '*-entries.txt' file
data={}    # store all image data from '*-data.json' file
default_parameters={
    "thres_R" : 0.8,
    "thres_G" : 0.5,
    "thres_B" : 0.4,
    "thres_C" : 0.4,
    "brightness" : 0.7,
    "bodies" : 0.08,
    "faces" : 0.07,
    "smoothness" : 0.8,
    "cutness" : 0.2,
    "blobiness" : 0.97,
    "skewness" : 0.1,
    "boundedness" : 0.7,
    "kontrastedness" : 0.8,
    "imgX" : 320,
    "imgY" : 212,
    "maxKeyPoints" : 250.0,
    "maxSkewAngle" : -90
}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Functions -------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def avg(lst): 
    return sum(lst) / len(lst) 

def gemwin_length(f):
	return f*2*100/float(p['imgX']*p['imgY'])

def hi_cut(val,thres,src,tar):
	if thres == 0:
		return
	if (val >= thres) or thres == 1:
		tar.append(int(src))

def lo_cut(val,thres,src,tar):
	if thres == 0:
		return
	if (val <= thres) or thres == 1:
		tar.append(int(src))

def bool_has(val,src,tar):
	if (val >= 1) or (val >= "1"):
		tar.append(int(src))

def calc_avg(key,dic,subkey):
	if key in dic:
		k=[]
		for i in dic[key]:
			k.append(i[subkey])
		return avg(k)

def calc_sum(key,dic,subkey):
	if key in dic:
		k=[]
		for i in dic[key]:
			k.append(i[subkey])
		return sum(k)

def calc_circarea(key,dic,subkey):
	if key in dic:
		k=[]
		for i in dic[key]:
			r=i[subkey]
			k.append(r*r*math.pi/float(p['imgX']*p['imgY']))
		return avg(k)

def intersect(*d):
    sets = iter(map(set, d))
    result = sets.next()
    for s in sets:
        result = result.intersection(s)
    return result

def convert(list): 
    s = [str(i) for i in list]
    res = " ".join(s) 
    return(res) 

def gauss(x,mean=0.8,stdev=0.01):
	return math.exp(-1.0 * (((x-mean)**2.0) / (2.0 * stdev))) * ( 1.0 / math.sqrt(2.0 * (stdev**2.0) * math.pi) )

def band_pass(val,thres,src,tar,q=8.0,stdev=0.01):
	if thres == 0:
		return
	elif thres == 1:
		tar.append(int(src))
	else:
		g = gauss(val,thres,stdev)
		if g >= q:
			tar.append(int(src))

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Arguments -------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

try:
	with open(sys.argv[1],"r") as f:
		entries=f.readlines()
	entries = [x.strip().split(' ') for x in entries]
except:
	print "query.py: no 'entries' file."
	quit(1)

try:
	with open(sys.argv[2],"r") as f:
		data=json.load(f)
except:
	print "query.py: no 'data' file."
	quit(1)

try:
	param_file=sys.argv[3]
	param_filename=os.path.splitext(param_file)[0]
	with open(param_file,"r") as f:
		p=json.load(f)
	target_file=param_filename+"-results.json"
except:
	print "default_parameters"
	p=default_parameters
	target_file="results-default_parameters.json"

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Run queries -----------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

for i in entries:
	hi_cut(float(i[2]),p['brightness'],i[0],t_Hiq)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

for i in data['data']:
	imgid=i['id']

	# EDIT THIS SO THAT IT WORKS WITH KMEANS color
	
	maxclust = max(i['mean_col'], key=lambda x: x['pct'])

	band_pass(maxclust['r'],p['thres_R'],imgid,t_Red)
	band_pass(maxclust['g'],p['thres_G'],imgid,t_Gre)
	band_pass(maxclust['b'],p['thres_B'],imgid,t_Blu)
	band_pass(maxclust['pct'],p['thres_C'],imgid,t_Col)
	
	bavg=calc_avg('bodies',i,'r')
	if bavg:
		bdiam=gemwin_length(bavg)
		band_pass(bdiam,p['bodies'],imgid,t_Bdy)
		# hi_cut(bdiam,p['bodies'],imgid,t_Bdy)

	favg=calc_avg('faces',i,'r')
	if favg:
		fdiam=gemwin_length(favg)
		band_pass(fdiam,p['faces'],imgid,t_Fac)
		# hi_cut(fdiam,p['faces'],imgid,t_Fac)

	lavg=calc_avg('lines',i,'d')
	if lavg:
		lavglen=gemwin_length(lavg)
		band_pass(lavglen,p['smoothness'],imgid,t_Smo)
		band_pass(lavglen,p['cutness'],imgid,t_Cut)
		# hi_cut(lavglen,p['smoothness'],imgid,t_Smo)
		# lo_cut(lavglen,p['cutness'],imgid,t_Cut)

	bsum=calc_sum('cvblob',i,'area')
	if bsum:
		band_pass(bsum,p['blobiness'],imgid,t_Blo)
		# hi_cut(bsum,p['blobiness'],imgid,t_Blo)
	
	bskw=calc_avg('cvblob',i,'angle')
	if bskw:
		band_pass(bskw,p['skewness']*p['maxSkewAngle'],imgid,t_Skw)
		# hi_cut(bskw,p['skewness']*p['maxSkewAngle'],imgid,t_Skw)
		
	csum=calc_circarea('circles',i,'r')
	if csum:
		band_pass(csum,p['boundedness'],imgid,t_Bou)
		# hi_cut(csum,p['boundedness'],imgid,t_Bou)

	if 'keypoints' in i:
		band_pass(len(i['keypoints'])/float(p['maxKeyPoints']),p['kontrastedness'],imgid,t_Kon)
		# hi_cut(len(i['keypoints'])/float(p['maxKeyPoints']),p['kontrastedness'],imgid,t_Kon)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Target output with Intersections or Unions ----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

d=[]

indexarrays = {
"thres_R" : "t_Red",
"thres_G" : "t_Gre",
"thres_B" : "t_Blu",
"thres_C" : "t_Col",
"brightness" : "t_Hiq",
"bodies" :  "t_Bdy",
"faces" :  "t_Fac",
"smoothness" : "t_Smo",
"cutness" : "t_Cut",
"blobiness" :  "t_Blo",
"skewness" : "t_Skw",
"boundedness" : "t_Bou",
"kontrastedness" : "t_Kon",
}

for i in p:
	try:
		if p[i] > 0: # only concatenate arrays that have something
			exec "arr = "+indexarrays[i]
			d.append(arr)
	except:
		continue

inter = list(reduce(np.intersect1d, (d)))
union = list(set().union(*d))

results={
	"inter": {
	"data":inter,
	"length":len(inter)
	},
	"union": {
	"data":union,
	"length":len(union)
	}
}

with open(target_file,"w") as f:
	f.write(json.dumps(results, indent=2))

print "read "+target_file

