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

	
index_audio_arrays = {
"brightness" : "a_br",
"bodies" :  "a_bo",
"faces" :  "a_fa",
"blobiness" :  "a_bl",
"boundedness" : "a_bn",
"kontrastedness" : "_ako",
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

	results={}

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


	# Adjust some values first:

	# make body and face threshold pass through gaussian curve
	body_thres=utils.gauss_thres(p['bodies'])
	face_thres=utils.gauss_thres(p['faces'])

	# get gemwin dimensions in smaller variables
	gx,gy=p['imgX'],p['imgY']


	c_avg=(p['thres_R']+p['thres_G']+p['thres_B'])/3.0
	b_avg=(p['brightness']+c_avg)/2.


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


	# query the colorwords database (with all results)

	for i in union:
		# print i
		for j in color_words['data']:
			name=j['name']
			if i in j['idlist']:
				# print "is in array",name
				if name not in color_indices:
					# print "_____appended",name
					color_indices.append(name)
				# else:
					# print "is repeated",name
			# else:
				# print "not in array",name


	# print "color indices",color_indices

	audio_entries=[]
	

	for i in audio_data['data']:

		file=i['file'] # the name of the audio database (color name)


		# only use audio databases that have the color name

		# there is something wrong here
		if file not in color_indices:
			# print "ignoring",file
			continue

		# print "using", file
		# make the query
		# num_instances=i['data']['num_instances']
		



		audio_results=[]

		idx=0

		for j in i['data']['instances']:
			a_br=[]
			a_bo=[]
			a_fa=[]
			a_bl=[]
			a_bn=[]
			a_ko=[]

			sidx=str(idx)

			utils.band_pass(j['brightness'],b_avg,sidx,a_br)
			utils.band_pass(j['body_face'],body_thres,sidx,a_bo)
			utils.band_pass(j['body_face_size'],face_thres,sidx,a_fa)
			utils.band_pass(j['blobiness'],p['blobiness'],sidx,a_bl)
			utils.band_pass(j['boundedness'],p['boundedness'],sidx,a_bn)
			utils.band_pass(j['kontrastedness'],p['kontrastedness'],sidx,a_ko)
			
			audio_results.append(list(set().union(a_br,a_bo,a_fa,a_bl,a_bn,a_ko)))

			# ignored stuff:
			# 
			# j['histo']

			idx+=1
		
		# only concatenate arrays that have something

		# for i in index_audio_arrays.keys():
		# 	try:
		# 		if p[i] > 0: 
		# 			exec "arr = "+index_audio_arrays[i]
		# 			audio_results.append(arr)
		# 			print "appending",index_audio_arrays[i]
		# 	except:
		# 		continue		

		a_union=list(set().union(*audio_results))
		# a_inter = list(reduce(np.intersect1d, (audio_results)))
		

		# print json.dumps(entry,separators=(",",":"),indent=None)
		
		# update the results object
		
		audio_entries.append({
			"file": file,
			"union": {"data":a_union,"length":len(a_union)}
			# "inter": {"data":a_inter,"length":len(a_inter)},
			})

	results.update({"inter":{"data":inter,"length":len(inter)}})
	results.update({"union":{"data":union,"length":len(union)}})
	results.update({"audio":{"data":audio_entries,"length":len(audio_entries)}}) 

	# write database to disk

	# with open(target_file,"w") as f:
		# f.write(json.dumps(results, indent=2))

	# print "read "+target_file

	# return the results object
	return results


def append_elements(d, s, t):



	for e in d[s]['data']:
		t.append("float")
		t.append(str(e))
		t.append(";\n")


	t.append("list")
	t.append(s)
	t.append(str(d[s]['length']))
	t.append(";\n")

	return t


	# 'audio':  { 
	#     "data" : [ {
	# 	       "file": file,
	# 	       "inter": {"data":a_inter,"length":len(a_inter)},
	# 	       "union": {"data":a_union,"length":len(a_union)}
	# 	   },{},... ]
	# 	}

def dict_to_pd_list(data):
	l=[]
	l.append("symbol begin;\n")

	# first the floats, then the header...
	
	append_elements(data,"union", l)
	append_elements(data,"inter", l)


	for e in data['audio']['data']:




		# l.append(e['file'])
		# l.append("a_inter")
		# l.append(str(e['inter']['length']))
		# for x in e['inter']['data']:
		# 	l.append(str(x))
		# l.append(";\n")

		for x in e['union']['data']:
			l.append("float")
			l.append(str(x))
			l.append(";\n")
		

		l.append("list")
		l.append(e['file'])
		l.append(str(e['union']['length']))
		l.append(";\n")


	l.append("symbol end;\n")
	# if "audio" in data:
	# 	for i in data['audio']:
	# 		append_elements(i,'file',l)
	# 		append_elements(i,'indices',l)
	
	# print json.dumps(data['audio'],separators=(",",":"),indent=None)

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

