import json, os, sys, subprocess
from subprocess import Popen, PIPE


data={}
with open("./data/color_sounds.json","r") as f:
	data=json.load(f)

try:
    srcpath=sys.argv[1]
except:
    print "concat_sounds.py: no path for source files was given."
    quit(1)

try:
    tgtpath=sys.argv[2]
except:
    print "concat_sounds.py: no path for target files was given."
    quit(1)

samplerate=44100

filedata={"data":[]}

for i in data['data']:
	name=i['name']
		
	if len(i['id'])>1:
		fcount=0
		files=''
		filesarray=[]
		for x in i['id']:
			filename= srcpath + str(x) + ".wav"
			cmd=['ffprobe', filename, '-show_format', '-hide_banner','-print_format', 'json' ]
			p = Popen(cmd, stdout=PIPE, stderr=PIPE)
			stdout, stderr = p.communicate()
			# print "------STDOUT--------------------------"
			# print stdout
			# print "-------STDERR ============= -------------------------"
			# print stderr
			if stdout:
				info=json.loads(stdout)
				if 'format' in info:
					dur=int(float(info['format']['duration'])*samplerate)
					if dur > 1:
						files+=" -i "+filename
						fcount+=1
						filesarray.append({"id":x,"dur":dur})
					else:
						print filename, "has no duration..."
				else:
					print filename, "no format in view..."
			else:
				print filename,"Not audio file."
		filedata['data'].append({ "name":name, "files":filesarray })
		filterflags=" -filter_complex '[0:0][1:0][2:0][3:0]"
		filterflags+="concat=n="+str(fcount)+":v=0:a=1[out]' "
		filterflags+=" -map '[out]' "
		filterflags+=" -ar "+str(samplerate)+" "
		command="ffmpeg "+files+filterflags+tgtpath+name+".wav"
		os.system("ffmpeg "+files+filterflags+tgtpath+name+".wav")

with open("./data/color_sounds_concat.json","w") as f:
	f.write(json.dumps(filedata, indent=4))











