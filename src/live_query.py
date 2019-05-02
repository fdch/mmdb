import json, sys, itertools, os
import numpy as np
from functools import reduce
import utils
import socket
import struct

default_port=5010
default_host="localhost"


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Variables -------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------



entries=[] # store all entries from 'image-entries.txt' file
image_data={}    # store image database from 'image-data.json' file
audio_data={}    # store audio database from 'audio-data.json' file
color_words={}   # store color words database

image_results=[]
color_indices=[]

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



index_image_arrays = {
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
# Arguments -------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

try:
	with open(sys.argv[1],"r") as f:
		entries=f.readlines()
	entries = [x.strip().split(' ') for x in entries]
except:
	print "live_query.py: no 'entries' file (argument 1)"
	quit(1)

try:
	with open(sys.argv[2],"r") as f:
		image_data=json.load(f)
except:
	print "live_query.py: no image 'data' file (argumen 2)"
	quit(1)

try:
	with open(sys.argv[3],"r") as f:
		audio_data=json.load(f)
except:
	print "live_query.py: no audio 'data' file (argument 3)"
	quit(1)


try:
	colorwords_file=sys.argv[4]
	try:
		with open(colorwords_file,"r") as f:
			color_words=json.load(f)
	except:
		print "Could not open ./data/colorwords.json, did you make that step?"
		print "Hint: Run python src/colors.py"
except:
	print "live_query.py: no colorwords 'data' file (argument 4)"
	quit(1)

try:
	port=int(sys.argv[5])
	print "live_query.py: using port:", port
except:
	port=default_port
	print "live_query.py: using default port:", port

try:
	host=sys.argv[6]
	print "live_query.py: using host:", host
except:
	host=default_host
	print "live_query.py: using default host:", host


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Run queries -----------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def query_database(p):

	# Adjust some values first:

	# make body and face threshold pass through gaussian curve
	body_thres=utils.gauss_thres(p['bodies'])
	face_thres=utils.gauss_thres(p['faces'])

	# get gemwin dimensions in smaller variables
	gx,gy=p['imgX'],p['imgY']


	# query the entries file

	for i in entries:
		utils.hi_cut(float(i[2]),p['brightness'],i[0],t_Hiq)

	# query the image database

	for i in image_data['data']:
		imgid=i['id']
		
		maxclust = max(i['mean_col'], key=lambda x: x['pct'])

		utils.band_pass(maxclust['r'],  p['thres_R'],imgid,t_Red)
		utils.band_pass(maxclust['g'],  p['thres_G'],imgid,t_Gre)
		utils.band_pass(maxclust['b'],  p['thres_B'],imgid,t_Blu)
		utils.band_pass(maxclust['pct'],p['thres_C'],imgid,t_Col)

		bavg=utils.calc_avg('bodies',i,'r')
		if bavg:
			bdiam=utils.gemwin_length(bavg,gx,gy)
			utils.band_pass(bdiam,body_thres,imgid,t_Bdy)

		favg=utils.calc_avg('faces',i,'r')
		if favg:
			fdiam=utils.gemwin_length(favg,gx,gy)
			utils.band_pass(fdiam,face_thres,imgid,t_Fac)

		lavg=utils.calc_avg('lines',i,'d')
		if lavg:
			lavglen=utils.gemwin_length(lavg,gx,gy)
			utils.band_pass(lavglen,p['smoothness'],imgid,t_Smo)
			utils.band_pass(lavglen,1.-p['cutness'],imgid,t_Cut)

		bsum=utils.calc_sum('cvblob',i,'area')
		if bsum:
			utils.band_pass(bsum,p['blobiness'],imgid,t_Blo)
		
		bskw=utils.calc_avg('cvblob',i,'angle')
		if bskw:
			utils.band_pass(bskw,p['skewness']*p['maxSkewAngle'],imgid,t_Skw)
			
		csum=utils.calc_circarea('circles',i,'r',gx,gy)
		if csum:
			utils.band_pass(csum,p['boundedness'],imgid,t_Bou)

		if 'keypoints' in i:
			utils.band_pass(len(i['keypoints'])/float(p['maxKeyPoints']),p['kontrastedness'],imgid,t_Kon)
	

	# only concatenate arrays that have something

	for i in p:
		try:
			if p[i] > 0: 
				exec "arr = "+index_image_arrays[i]
				image_results.append(arr)
		except:
			continue

	# Filter image database query with Intersections or Unions 
	
	inter = list(reduce(np.intersect1d, (image_results)))
	union = list(set().union(*image_results))

	# place image database query in JSON object 'results'

	results={
		"inter": {
		"data":inter,
		"length":len(inter)
		},
		"union": {
		"data":union,
		"length":len(union)
		},
		"audio" : []
	}


	# query the colorwords database (with all results)

	for i in image_results:
		for j in color_words['data']:
			name=j['name']
			if i in j['idlist']:
				if name not in color_indices:
					color_indices.append(name)


	# query the audio database

	for i in audio_data['data']:

		file=i['file'] # the name of the audio database (color name)


		# only use audio databases that have the color name

		if file not in color_indices:
			continue

		# make the query
		num_instances=i['data']['num_instances']
		
		audio_indices={"idx":[],"extra":[]}
		
		ai=audio_indices['idx']
		ax=audio_indices['extra']
		
		idx=0

		for j in i['data']['instances']:
			# j['histo']
			t=0
			t+=utils.band_pass(j['brightness'],p['brightness'],idx,ai)
			t+=utils.band_pass(j['body_face'],body_thres,idx,ai)
			t+=utils.band_pass(j['body_face_size'],face_thres,idx,ai)
			t+=utils.band_pass(j['blobiness'],p['blobiness'],idx,ai)
			t+=utils.band_pass(j['boundedness'],p['boundedness'],idx,ai)
			t+=utils.band_pass(j['kontrastedness'],p['kontrastedness'],idx,ai)
			if t>=4:
				ax.append({
					"index":idx,
					"smoothness":p['smoothness'],
					"cutness":p['cutness'],
					"skewness":p['skewness']
					})
			idx+=1
		
		entry={"file":file,"num_instances":num_instances,"indices":list(audio_indices)}

		# update the results object
		
		results['audio'].append(entry)

	# write database to disk

	# with open(target_file,"w") as f:
		# f.write(json.dumps(results, indent=2))

	# print "read "+target_file

	# return the results object
	return results
	# return {"data":results}

def append_elements(d, s, t):
	t.append(s)
	t.append(str(d[s]['length']))
	for e in d[s]['data']:
		t.append(str(e))
	return t


def dict_to_pd_list(data):
	l=[]

	append_elements(data,"union", l)

	l.append(";\n")

	append_elements(data,"inter", l)

	l.append(";\n")

	l.append("audio")
	l.append(str(len(data['audio'])))
	
	for e in data['audio']:
		l.append(str(e))

	l.append(";\n")

	return " ".join(l)


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Read incoming JSON TCP string -----------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def pd_to_str(msg=''):
	return str(msg+";\n") # .replace(",","\,")

def pd_from_str(tcpstring):
	return (tcpstring[:-2].replace("\,",","))

def pd_read_json(data):
	p=json.loads(pd_from_str(data))

	# make the query
	r = query_database(p)
	# r = p # just echo the file

	# return r
	# return r object
	return dict_to_pd_list(r)
	# return pd_to_str(json.dumps(r,separators=(',',':'), indent=None))

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Open Socket -----------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))

s.listen(10)

conn, addr = s.accept()

while 1:
    data = conn.recv(1024)
    if not data:
        break
    conn.sendall(pd_read_json(data))
conn.close()

