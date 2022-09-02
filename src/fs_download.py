import time # this is needed otherwise freesound throttles downloads at +60/min
import sys, json
import requesting as rq

client={}
tokens={}

with open("client.json","r") as f:
    client=json.load(f)

with open("tokens.json","r") as f:
    tokens=json.load(f)


data={}

try:
    with open(sys.argv[1],"r") as f:
        data=json.load(f)
except:
    print "fs_download.py: no 'data' file."
    quit(1)

try:
    audiopath=sys.argv[2]
except:
    print "fs_download.py: no path for downloading files was given."
    quit(1)

# count=0
for i in data['data']:
    # count+=1
    queries=[]
    i.update({"id":[]})
    queries.append(i['name'])
    for w in i['words']:
        queries.append(w['word'])
    for q in queries:
        print "querying...", q
        resp = rq.query_id(q,client['client_secret'])
        if "results" in resp:
            for x in resp['results']:
                i['id'].append(x['id'])
                rq.download_id(str(x['id']),audiopath,tokens['access_token'])
                time.sleep(1)
    # if count==3:
    #     break

with open("./data/color_sounds.json","w") as f:
    f.write(json.dumps(data,indent=4))

