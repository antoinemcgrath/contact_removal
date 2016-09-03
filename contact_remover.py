#!/usr/bin/python
# Verion start by https://github.com/billmarczak
import re
import sys

if len(sys.argv) < 2:
    print "ERROR: Please specify which file you would like to remove authors from"
    sys.exit(-1)

f = open(sys.argv[1], "r")
data = f.read()
f.close()

# initialize variables
objnum = -1
objlist = []

# put each object number in objlist
find_obj = re.compile("^([0-9]+) [0-9]+ obj$")
for line in data.split("\n"):
    lin = line.rstrip() # Strips line of beginning and ending ()characters
    mat = find_obj.match(lin) # Values each line as find_obj match or none
    if mat:
        objnum = mat.group(0) # Assigns a value to each match
    elif lin == "endobj": # Find object endings
        objlist.append(objnum)


for item in objlist:
    obj_start = data.find(item)
    data_obj_net = data[obj_start:]

    found_endobj = data_obj_net.find("endobj")
    obj_end = (obj_start+found_endobj)
    obj_data = data[obj_start: obj_start+found_endobj]

    # For THIS OBJECT, master text will contain all of the text concatenated together
    master_text = ""
    # Given an index in master_text, the text_map array tells us what index that is in data
    text_map = []

    # Gets everything between "BT" and "ET" markers as text.
    # WARNING WARNING: This may break if the PDF contains text that is "BT" or "ET"
    for m in re.finditer(r'BT(.*?)ET', obj_data, re.DOTALL):
        the_text = m.group(1)
        text_start = m.start(1)
        # Find all the stuff inside the parentheses
        for t in re.finditer(r'\(([^\(\)]+)\)', the_text):
            text_piece = t.group(1)
            for idx in range(len(text_piece)):
                text_map.append(obj_start + text_start + t.start(1) + idx)
            master_text += text_piece
                
    for em in re.finditer(r'[^ ]+@crs\.loc\.gov.*?\d-\d{4}', master_text):
        print "REMOVING EMAIL", "\"", em.group(0), "\""
        for idx in range(em.start(0), em.end(0)):
            data_idx = text_map[idx]
            data = data[:data_idx] + " " + data[data_idx+1:]
                
f = open('OUTPUT.pdf', 'w')
f.write(data)
f.close()
