import math

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Functions -------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def avg(lst): 
    return sum(lst) / len(lst) 

def gemwin_length(f,x,y):
	return f*2*100/float(x*y)

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

def calc_circarea(key,dic,subkey,x,y):
	if key in dic:
		k=[]
		for i in dic[key]:
			r=i[subkey]
			k.append(r*r*math.pi/float(x*y))
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

def gauss(x,mean=0.7,stdev=0.01):
	return math.exp(-1.0 * (((x-mean)**2.0) / (2.0 * stdev))) * ( 1.0 / math.sqrt(2.0 * (stdev**2.0) * math.pi) )

def band_pass(val,thres,src,tar,q=8.0,stdev=0.015):
	src=int(src)
	if thres == 0:
		return 0
	elif thres == 1:
		tar.append(int(src))
		return 1
	else:
		g = gauss(val,thres,stdev)
		if g >= q:
			if src not in tar:
				tar.append(src)
			return 1
		else:
			return 0

def gauss_thres(thres):
	if thres == 1:
		return 1
	elif thres == 0:
		return 0
	else:
		return gauss(thres-0.5,0.5,0.01)/40.

