import sys
import json
import webcolors
from collections import OrderedDict
import requesting
import catjson as cj

# First concatenate json files into single files

cj.catjson("./data/images-data.json","./txt/","images-*.json")
cj.catjson("./data/videos-data.json","./txt/","videos-*.json")




# https://stackoverflow.com/questions/9694165/convert-rgb-color-to-english-color-name-like-green-with-python

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name



data={}

try:
    with open(sys.argv[1],"r") as f:
        data=json.load(f)
except:
    print "colors.py: no 'data' file."
    quit(1)


color_dict=[]
color_list=[]
unique_colors=[]

for i in data['data']:
    imgid=i['id']

    color_names=[]
    for c in i['mean_col']:

        rgbcol=[int(c['r']*255),int(c['g']*255),int(c['b']*255)]

        actual_name, closest_name = get_colour_name(rgbcol)

        if not actual_name:
            color_names.append(closest_name)
            if closest_name not in unique_colors:
                unique_colors.append(closest_name)
        else:
            color_names.append(actual_name)
            if closest_name not in unique_colors:
                unique_colors.append(actual_name)

    c=list(OrderedDict.fromkeys(color_names))
    color_list.append({'id':imgid,'colors':c})


# with open("color_list.json","w") as f:
#     f.write(json.dumps({"color_list":color_list},indent=4))

for c in unique_colors:
    color_dict.append({
        "name":c,
        "words": requesting.find_nouns(c),
        "idlist": []
        })

# with open("color_words.json","w") as f:
#     f.write(json.dumps({"color_words":color_dict},indent=4))

for i in color_list:
    for j in color_dict:
        if j['name'] in i['colors']:
            if i['id'] not in j['idlist']:
                j['idlist'].append(i['id'])

with open("./data/colorwords.json","w") as f:
    f.write(json.dumps({"data":color_dict},indent=4))

# print json.dumps(color_list)



