import requests as r
import json

datamuse = "https://api.datamuse.com/words"

def find_nouns(query,rmax=5,rtype="rel_jja"):
	try:
	    resp = r.get(datamuse, params={rtype:query,'max':rmax})
	    return resp.json()
	except:
	    print "Couldn't make request"
	    quit(1)

freesnd = "https://www.freesound.org/apiv2"

def query_id(query,token):
	p={
		"page_size":5,
		"sort":"duration_asc",
		"query":query,
		"token":token
	}
	try:
		resp = r.get(freesnd+"/search/text/",params=p)
		return resp.json()
	except:
	    print "Couldn't make request"
	    quit(1)

# LATER FIX EXTENSION TO ORIGINAL EXTENSION!

def download_id(sound,path,token):
	# try:
	api_call_headers = {'Authorization': 'Bearer ' + token}
	resp = r.get(freesnd+"/sounds/"+sound+"/download/",headers=api_call_headers,allow_redirects=True)
	# print resp.headers.get('content-type')
	# print resp.text
	filename=path+"/"+sound+".wav"
	print "Downloading... ", filename
	open(filename, 'wb').write(resp.content)
	# except:
	    # print "Couldn't download"
	    # quit(1)




