import json, os, glob, sys
import catjson as cj
import timid2json as t2j
import ntpath

try:
    srcpath=sys.argv[1]
except:
    print "make_audio_db.py: no path for source files was given."
    quit(1)

try:
    tgtpath=sys.argv[2]
except:
    print "make_audio_db.py: no filename for target file was given."
    quit(1)

print "converting all *.timid in:",srcpath,"..."
t2j.batch_convert_extra(srcpath)

files={"data":[]}
for filename in glob.glob(os.path.join(srcpath, "*.json")):
	with open(filename) as f:
		file=os.path.splitext(ntpath.basename(filename))[0]
		print "appending:",file,"..."
		files['data'].append({"file":file,"data":json.load(f)})

with open(tgtpath,"w") as t:
    print "making audio database in:",tgtpath,"..."
    t.write(json.dumps(files,indent=4))
