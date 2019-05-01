import json, sys, itertools, os
import numpy as np
from functools import reduce
import utils
import socket


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Variables -------------------------------------------------------------------
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


image_results=[]
color_indices=[]

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

#------------------------------------------------------------------------------
entries=[] # store all entries from '*-entries.txt' file
image_data={}    # store all image data from '*-data.json' file
audio_data={}    # store all audio data from '*-data.json' file
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
	print "matching_query.py: no 'entries' file."
	quit(1)

try:
	with open(sys.argv[2],"r") as f:
		image_data=json.load(f)
except:
	print "matching_query.py: no image 'data' file."
	quit(1)

try:
	with open(sys.argv[3],"r") as f:
		audio_data=json.load(f)
except:
	print "matching_query.py: no audio 'data' file."
	quit(1)


try:
	param_file=sys.argv[4]
	param_filename=os.path.splitext(param_file)[0]
	with open(param_file,"r") as f:
		p=json.load(f)
	target_file=param_filename+"-results.json"
except:
	print "default_parameters"
	p=default_parameters
	target_file="default_parameters-results.json"


color_words={}
try:
	colorwords_file=sys.argv[5]
	with open(colorwords_file,"r") as f:
		color_words=json.load(f)
except:
	print "Could not open ./data/colorwords.json, did you make that step?"
	print "Hint: Run python src/colors.py"
	quit(1)










# make body and face threshold pass through gaussian curve

body_thres=utils.gauss_thres(p['bodies'])
face_thres=utils.gauss_thres(p['faces'])

# print "face_thres",face_thres
# print "body_thres",body_thres

# get gemwin dimensions in smaller variables
gx,gy=p['imgX'],p['imgY']




#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Run queries -----------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def query_database(p)

	for i in entries:
		utils.hi_cut(float(i[2]),p['brightness'],i[0],t_Hiq)

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
	# Target output with Intersections or Unions 

	for i in p:
		try:
			if p[i] > 0: # only concatenate arrays that have something
				exec "arr = "+index_image_arrays[i]
				image_results.append(arr)
		except:
			continue

	inter = list(reduce(np.intersect1d, (image_results)))
	union = list(set().union(*image_results))

	results={
		"inter": {
		"data":inter,
		"length":len(inter)
		},
		"union": {
		"data":union,
		"length":len(union)
		},
		"audiofiles" : []
	}

	image_indices=inter+union


	# query the colorwords database

	for i in image_indices:
		for j in color_words['data']:
			name=j['name']
			if i in j['idlist']:
				if name not in color_indices:
					color_indices.append(name)

	# audio database query

	for i in audio_data['data']:
		file=i['file'] # the name of the audio database (color name)

		if file not in color_indices:
			continue

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
		
		entry={"file":file,"num_instances":num_instances,"indices":audio_indices}
		results['audiofiles'].append(entry)

	with open(target_file,"w") as f:
		f.write(json.dumps(results, indent=2))

	print "read "+target_file












s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', 5010))
s.listen(1)
conn, addr = s.accept()
while 1:
    data = conn.recv(1024)
    if not data:
        break
    print data
    conn.sendall(data)
conn.close()













