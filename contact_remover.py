#!/usr/bin/python

## The input file is expected to be an unlocked & decoded CRS document that has author contacts
## The ouput file is the same doc without CRS contacts (author telephone and email addresses)

# Single file run:
# python contacts-remover.py /input.pdf /output.pdf

# List of files run (3 inputs):
# while read line; do python /contacts-remover.py /sourcedir/$line /destinationdir/$line ; done < /file_list.txt


import re
import sys
import os
import subprocess

if len(sys.argv) < 2:
    print "ERROR: Please specify which file you would like to remove authors from"
    sys.exit(-1)


#### First decode and expand the original CRS file
## BASH in python for: qpdf --qdf --object-streams=disable /input.pdf /output.pdf
bash_line = 'qpdf --qdf --object-streams=disable'

bash_command = bash_line + " " + sys.argv[1] + " " + sys.argv[2] + "temp1"
print(bash_command)
p = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
out, err = p.communicate()
print (out)
#### End file decode


#### Now that the expanded file is in expanded
##   we locate objects (sections) of interest
##   and map the characters within the object

#Prep
f = open(sys.argv[2] + "temp1", "r")
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

#   Gets everything between "BT" and "ET" markers as text.
#   WARNING WARNING: This may break if the PDF contains text that is "BT" or "ET"
    for m in re.finditer(r'BT(.*?)ET', obj_data, re.DOTALL):
        the_text = m.group(1)
        text_start = m.start(1)
        # Find all the stuff inside the parentheses
        for t in re.finditer(r'\(([^\(\)]+)\)', the_text):
            text_piece = t.group(1)
            for idx in range(len(text_piece)):
                text_map.append(obj_start + text_start + t.start(1) + idx)
            master_text += text_piece



#   em catches the bulk of contact occurences
#   Looks for email + telehpne within close proximity
#   The following regex is inclusive of occurences of:
#   @crs.loc.gov   @crs.loc.   @crs.lo.  @crsloc.gov   mailto:##@crs.loc.gov

    for em in re.finditer(r'((\b)|mailto:)\w+@crs(\.)?lo(\.)?(c\.(gov)?)?', master_text):
        segment = master_text[em.start(0)-35:em.end(0)+35]
        for emt in re.finditer(r'7-\d{4}', segment):
            print "REMOVING TELE", "\"", emt.group(0), "\""
            for idx in range(emt.start(0)+em.start(0)-35, emt.end(0)+em.start(0)-35):
                data_idx = text_map[idx]
                data = data[:data_idx] + " " + data[data_idx+1:]
#    Removing
        print "REMOVING EMAIL", "\"", em.group(0), "\""
        for idx in range(em.start(0), em.end(0)):
            data_idx = text_map[idx]
            data = data[:data_idx] + " " + data[data_idx+1:]

#   cover catches telephone contacts on the coverpage
    for cover in re.finditer(r'(\b)(www.crs.gov)', master_text):
        segment = master_text[cover.start(0)-35:cover.end(0)]
        #    Removing
        for cover_tele in re.finditer(r'7-\d{4}', segment):
            print "REMOVING TELE", "\"", cover.group(0), "\""
            for idx in range(cover_tele.start(0)+cover.start(0)-35, cover_tele.end(0)+cover.start(0)-35):
                data_idx = text_map[idx]
                data = data[:data_idx] + " " + data[data_idx+1:]

#   ack catches telephone contacts within Acknowledgment sections
    for ack in re.finditer(r'(\b)(Acknowledgments)', master_text):
        segment = master_text[ack.start(0):ack.end(0)+500]
        for ack_tele in re.finditer(r'7-\d{4}', segment):
            #    Removing
            print "REMOVING TELE", "\"", ack.group(0), "\""
            for idx in range(ack.start(0)+ack_tele.start(0), ack_tele.end(0)+ack.start(0)):
                data_idx = text_map[idx]
                data = data[:data_idx] + " " + data[data_idx+1:]


f = open(sys.argv[2] + "temp2", 'w')
f.write(data)
f.close()


#### Compress the new author contacts free CRS file into your final pdf
## BASH in python for: qpdf --linearize /input.pdf /output.pdf
bash_line = 'qpdf --linearize'

bash_command = bash_line + " " + sys.argv[2] + "temp2" + " " + sys.argv[2]
print(bash_command)
p = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
out, err = p.communicate()
print (out)
#### End file decode

#### Clean up temp files
os.remove(sys.argv[2] + "temp1")
os.remove(sys.argv[2] + "temp2")
##

####
print ("Have a nice day")
