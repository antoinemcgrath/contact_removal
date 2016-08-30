#!/usr/bin/python
import re
from termcolor import colored
import os


#### Define file(s) to edit & get lines
f = open("one_crs_pdf", "r") #f for file

content = f.read()
data = content
lines = content.split("\n")
f.close()

#### Zero variables
cur_obj = ""
objnum = ""
objlist=[]



#### Get objnum for an object containing an @crs.loc email
#### Create a thumbprint or pinkyprint item for each telephone occurrences in obj
#-2 lists [thumb] [pinky]
#### For each item in thumb list run thumb regex and remove, do the same for pinky
#-In descending order remove each indexed or save after each modification.
#### Save data, reset values, rerun from get objnum
#### When objects are left to modify save doc


#### Extract visible texts, test for email and return corresponding obj.
def process_obj(str, objnum):
    texts = re.findall('BT(.*?)ET', str)

    #### Extract visible texts:
    dtext_str = "".join(texts)
    text_strs = re.findall('\(([^\(\)]+)\)', dtext_str)
    text_str = "".join(text_strs)
    if text_str != "":

        #### Test for email:
        #### Track results these nets could miss some loc emails (if texts line breaks with abnormal frequency)
        if "s.loc.g" in text_str or "@crs.l" in text_str or "oc.gov" in text_str:
            print (colored(("FOUND email(s) in objnum: " + objnum), 'blue'))
            #### Return corresponding obj:
            #return objnum
            objlist.append(objnum)
######## End def process_obj


#### Get object data and search for prints
def find_fingerprints(obj_start):
    #print (objlist[-1])
    #### Locates object start:
    #obj_start = data.find(objlist[-1])
    #print (colored(("FOUND obj_start indexed at: " + str(obj_start)), 'yellow'))
    if obj_start == -1:
        return data
    #### Set net as +50,000 characters long:
    data_obj_net = data[obj_start:]
    #### Within net locate the first object end
    found_endobj = data_obj_net.find("endobj")
    obj_end = (obj_start+found_endobj)
    #print (colored(("FOUND obj_end: " + str(obj_end)), 'yellow'))

    #### Isolates object, searches object for telephone # & gets contact thumbprint.
    obj_data = data[obj_start: obj_start+found_endobj]
    #### FOR MONITORING
    ####print data[obj_start: obj_start+found_endobj]
    thumbprints=[]
    pinkyprints=[]



    ##############################################################
    #### Searches object for telephone # & gets contact thumbprint
    ## thumb/pinky print is often ###.####, but assumed to be regex " \d+.\d+ "
    ## "(?P<var>" assigns regex match, "(?:" match but do not capture
    ## Tm/print in line ahead of contact (regular=thumbprint)
    ## 7-#### ~(##)TJ then line break (or none) followed by print/Tm (less common=pinkyprint)
    thumbprints = re.findall(r'(?:\s)(?P<thumbprint>\d+.\d+)(?:\s*Tm\n\[.*? 7-\d\d\d\d?\s?\)\]TJ)', obj_data)
    pinkyprints = re.findall(r'(?:\[.*? 7-\d\d\d\d?\s?\)\]TJ\n+.*?\s)(?P<thumbprint>\d+.\d+)(?:\s*Tm)', obj_data)
    ##############################################################
    #print (colored("Found thumbprints: " + str(thumbprints), "yellow"))
    #print (colored("Found pinkyprints: " + str(pinkyprints), "yellow"))
    return thumbprints, pinkyprints
#### End searching object for prints

#### Searches object for regex of contact segment via prints
def list_segments():
    global data
    for item in objlist:
        obj_start = data.find(item)
        print "obj_start:  " + str(obj_start)
        data_obj_net = data[obj_start:]
        thumbprints, pinkyprints = find_fingerprints(obj_start)
        print "List thumbprints: " + str(thumbprints)
        print "List pinkyprints: " + str(pinkyprints)

        for thumbprint in thumbprints:

            print (colored("START THUMB LOOP For thumbprint: "+ str(thumbprint), "green"))
#            thumbstart=obj_data.rfind(thumbprint)
#            print (colored(str(thumbprint) + " :: length : " + str(len(thumbprint)) + " : starts obj @ : " + str(thumbstart), "yellow"))
            
            while True:
                found_endobj = data_obj_net.find("endobj")
                obj_end = (obj_start+found_endobj)
                obj_data = data[obj_start: obj_start+found_endobj]

                thumb_str_first = [(m.start(0), m.end(0), m.group(4)) for m in re.finditer(r''+thumbprint+' ((TM|Tm|tM|tm)(\n)(.*?)(TJ|Tj|tJ|tj))', obj_data)]
                thumb_str = []
                for ts in thumb_str_first:
                    if ts[2] != "":
                        thumb_str.append(ts)

                if len(thumb_str) == 0:
                    break

                for s in thumb_str:
                    print obj_data[s[0]:s[1]]
                    print data[s[0]+obj_start:s[1]+obj_start]
                    print s[2]

                thumb = thumb_str[0]
                thumbstart = thumb[0]
                thumbend = thumb[1]

                global_start = obj_start + thumbstart + len(thumbprint) + len(" tm\n")
                global_end = obj_start + thumbend - len("tj")

                print colored(("Thumb print: " + repr(data[obj_start + thumbstart : obj_start + thumbend])), "red")
                print colored(("Remove the following segment: " + (data[global_start : global_end])), "green")


                #print data [obj_start+thumbstart-100:obj_start+thumbstart+00]
                datastart = data[:global_start]
                dataend = data[global_end:]
                data = datastart + dataend
                print colored(("RESULT"), "red")
                print data [obj_start+thumbstart-30:obj_start+thumbstart+30]
                #print
                #### Add thumb removal from data

                #del thumb_str[-1]
                #thumb_str.remove(thumb_str[-1])
                #print colored(len(format(m.group(0))), "blue")
                #print colored((format(m.group(0))), "blue")
                #thumb_str.remove(thumb_str[-1])




        for pinkyprint in pinkyprints:

            print (colored("START pinky LOOP For pinkyprint: "+ str(pinkyprint), "green"))
#            pinkystart=obj_data.rfind(pinkyprint)
#            print (colored(str(pinkyprint) + " :: length : " + str(len(pinkyprint)) + " : starts obj @ : " + str(pinkystart), "yellow"))
            
            while True:
                found_endobj = data_obj_net.find("endobj")
                obj_end = (obj_start+found_endobj)
                obj_data = data[obj_start: obj_start+found_endobj]

                pinky_str_first = [(m.start(0), m.end(0), m.group(3)) for m in re.finditer(r'.*(TJ|Tj|tJ|tj)(\n|\n{2}).*'+pinkyprint+' (TM|Tm|tM|tm)', obj_data)]
                pinky_str = []
                for ts in pinky_str_first:
                    if ts[2] != "":
                        pinky_str.append(ts)

                if len(pinky_str) == 0:
                    break

                for s in pinky_str:
                    print obj_data[s[0]:s[1]]
                    print data[s[0]+obj_start:s[1]+obj_start]
                    print s[2]

                pinky = pinky_str[0]
                pinkystart = pinky[0]
                pinkyend = pinky[1]

                global_start = obj_start + pinkystart + len(pinkyprint) + len(" tm\n[(")
                global_end = obj_start + pinkyend - len(")]tj")

                print colored(("Thumb print: " + repr(data[obj_start + pinkystart : obj_start + pinkyend])), "red")
                print colored(("Remove the following segment: " + (data[global_start : global_end])), "green")


                #print data [obj_start+pinkystart-100:obj_start+pinkystart+00]
                datastart = data[:global_start]
                dataend = data[global_end:]
                data = datastart + dataend
                print colored(("RESULT"), "red")
                print data [obj_start+pinkystart-30:obj_start+pinkystart+30]
                #print
                #### Add pinky removal from data

                #del pinky_str[-1]
                #pinky_str.remove(pinky_str[-1])
                #print colored(len(format(m.group(0))), "blue")
                #print colored((format(m.group(0))), "blue")
                #pinky_str.remove(pinky_str[-1])

        #print "objlist"
        #print objlist
        #objlist.remove(objnum)
        #print "objlist"
        #print objlist

#### Fetches objects when called
find_obj = re.compile("^([0-9]+) [0-9]+ obj$")
#### Search doc lines for objects
for line in lines:
    lin = line.rstrip() # Strips line of beginning and ending ()characters
    mat = find_obj.match(lin) # Values each line as find_obj match or none
    if mat:
        objnum = mat.group(0) # Assigns a value to each match
        cur_obj = ""
    elif lin == "endobj": # Find object endings

        #### Execute process loop on objects to discover ones that contain LOC email addresses.
        num = process_obj(cur_obj, objnum)
        #if num:
#            remove_object(cur_obj, content)
    else:
        # Not a "begin object" or "end object" line
        cur_obj += lin

#while objlist:  #this also works: while objlist[0] in objlist:
print (colored("CREATED objlist: " +str(objlist)+ " Gathering fingerprints from: " + str(objlist[-1]), "blue"))
    #find_fingerprints()
    #print (colored("Found thumbprints: " + str(thumbprints), "yellow"))
    #print (colored("Found pinkyprints: " + str(pinkyprints), "yellow"))
    #list1, list2 = find_fingerprints() # Receiving returned lists from find loop
    #thumbprints = list1 # Assigning returned lists
    #pinkyprints = list2 # Assigning returned lists
list_segments()
    #del objlist[-1:]

f = open("test-test-test", "w")
f.write(data)
f.close()
