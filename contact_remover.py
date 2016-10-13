# -*- encoding: utf-8 -*-

#!/usr/bin/python3

#### Single file run:
# python contacts-remover.py input_file.pdf output_file.pdf

#### Run on an entire directory:
# python contacts-remover.py input_directory/ output_directory/

#### This script will remove author contacts (telephone numbers, emails (and author names when provided in .txt)) from CRS PDFs
# (Will not execute on hidden files nor subdirectories)
# (Will halt script if a document is not a PDF or if PDF is corrupt)
# (Destination directory will be created if it does not exist)
# (Directories and document titles must not include spaces)

##**QPDF is used to expand and condense CRS reports files it is released under
# **the terms of Version 2.0 of the Artistic License. Visit the site http://qpdf.sourceforge.net/
# **for additional information.

import re
import sys
import os
import subprocess
import tempfile

#Load author names (utf-8 characters only) 
with open("author_names.txt", "r", encoding="utf-8") as f:
    names = [line.rstrip('\n') for line in f]

#author_file = open("author_names.txt", "r", encoding="utf-8")

#global names
#names = author_file.read().split('\\n')
#name = names.encode('utf-8')#.decode().split('\\n')
#name = names.decode()
#nam = name.split('\\n')
#author_file = author_file.encode('ascii', '.').decode('ascii')
#names = author_file.read().split(',').encode('utf-8').strip()

#print ((names.encode('utf-8')))

#with open("author_names.txt", "r") as f:
#author_file = author_file.decode("ascii")
#    train_set, valid_set, test_set = f.load(f, encoding='latin1')

#    names = f
    #names = f.read().split(',')
#    print (names)



#read lines into an array

#### Begin removing author contacts
def remove_contacts_in_pdf(infile, outfile):
    #### Record what we removed.
    what_was_removed = []

    #### First decode and expand the original CRS file
    data = subprocess.check_output(['qpdf', '--qdf', '--object-streams=disable',
        infile, "-"])

    #### Now that the expanded file is in expanded
    ##   we locate objects (sections) of interest
    ##   and map the characters within the object
    objnum = -1
    objlist = []

    # Find object starts in document and list
    find_obj = re.compile(b"^([0-9]+) [0-9]+ obj$")
    for line in data.split(b"\n"):
        lin = line.rstrip() # Strips line of beginning and ending ()characters
        mat = find_obj.match(lin) # Values each line as find_obj match or none
        if mat:
            objnum = mat.group(0) # Assigns a value to each match
        elif lin == b"endobj": # Find object endings
            objlist.append(objnum)

    # Define span of each object within document data
    for item in objlist:
        obj_start = data.find(item)
        data_obj_net = data[obj_start:]
        found_endobj = data_obj_net.find(b"endobj")
        obj_end = (obj_start+found_endobj)
        obj_data = data[obj_start: obj_start+found_endobj]

        # For THIS OBJECT, master text will contain all of the text concatenated together
        master_text = b""
        # Given an index in master_text, the text_map array tells us what index that is in data
        text_map = []

    #   Gets everything between "BT" and "ET" markers as text.
    #   WARNING WARNING: This may break if the PDF contains text that is "BT" or "ET"
        for m in re.finditer(rb'BT(.*?)ET', obj_data, re.DOTALL):
            the_text = m.group(1)
            text_start = m.start(1)
            # Find all the stuff inside the parentheses
            for t in re.finditer(rb'\(([^\(\)]+)\)', the_text):
                text_piece = t.group(1)
                for idx in range(len(text_piece)):
                    text_map.append(obj_start + text_start + t.start(1) + idx)
                master_text += text_piece


    #   em Will catch the bulk of contact occurences
    #   em Looks for email and the telephone within close proximity
    #   The following regex finds occurences of:
    #   @crs.loc.gov   @crs.loc.   @crs.lo.  @crsloc.gov   mailto:##@crs.loc.gov
        for em in re.finditer(rb'((\b)|mailto:)\w+@crs(\.)?lo(\.)?(c\.(gov)?)?', master_text):
            segment = master_text[em.start(0)-35:em.end(0)+35]
            for emt in re.finditer(rb'7-\d{4}', segment):
                what_was_removed.append(emt.group(0))
                for idx in range(emt.start(0)+em.start(0)-35, emt.end(0)+em.start(0)-35):
                    data_idx = text_map[idx]
                    data = data[:data_idx] + b" " + data[data_idx+1:]
    #    Removing em contact occurences
            what_was_removed.append(em.group(0))
            for idx in range(em.start(0), em.end(0)):
                data_idx = text_map[idx]
                data = data[:data_idx] + b" " + data[data_idx+1:]



    #   Remove author names (as provided from file author_names.txt)

        for named in names:
            print (named)
            print (named)
            print (type(named))
            #it = iter(named)
            nameds = named.encode("utf-8")
            #some_string.encode(encoding)

            for authors_name in re.finditer(nameds, master_text):
                segment = master_text[authors_name.start(0)-35:authors_name.end(0)+35]
                print (segment)
                print (segment)

                for authors_namet in re.finditer(nameds, segment):
                    what_was_removed.append(authors_namet.group(0))
                    for idx in range(authors_namet.start(0)+authors_name.start(0)-35, authors_namet.end(0)+authors_name.start(0)-35):
                        data_idx = text_map[idx]
                        data = data[:data_idx] + b" " + data[data_idx+1:]
        #    Removing em contact occurences
                what_was_removed.append(authors_name.group(0))
                for idx in range(authors_name.start(0), authors_name.end(0)):
                    data_idx = text_map[idx]
                    data = data[:data_idx] + b" " + data[data_idx+1:]








    #   cover Catches telephone contacts on the coverpage
        for cover in re.finditer(rb'(\b)(www.crs.gov)', master_text):
            segment = master_text[cover.start(0)-35:cover.end(0)]
            #    Removing cover contact occurences
            for cover_tele in re.finditer(rb'7-\d{4}', segment):
                what_was_removed.append(cover.group(0))
                for idx in range(cover_tele.start(0)+cover.start(0)-35, cover_tele.end(0)+cover.start(0)-35):
                    data_idx = text_map[idx]
                    data = data[:data_idx] + b" " + data[data_idx+1:]

    #   ack catches telephone contacts within Acknowledgment sections
        for ack in re.finditer(rb'(\b)(Acknowledgments)', master_text):
            segment = master_text[ack.start(0):ack.end(0)+500]
            for ack_tele in re.finditer(rb'7-\d{4}', segment):
                #    Removing ack contact occruences
                what_was_removed.append(ack.group(0))
                for idx in range(ack.start(0)+ack_tele.start(0), ack_tele.end(0)+ack.start(0)):
                    data_idx = text_map[idx]
                    data = data[:data_idx] + b" " + data[data_idx+1:]





    #### Compress the new author-contact-free CRS file and write to the output file.
    with tempfile.NamedTemporaryFile() as f:
        f.write(data)
        f.flush()
        subprocess.check_call(['qpdf', '--linearize', f.name, outfile])

    return what_was_removed

if __name__ == "__main__":
    #### Set input error limits and notifications
    if len(sys.argv) < 3:
        print("\n"+ "INPUT ERROR: Please specify an input/output pair of files or directories" + "\n")
        print("Single file example: ")
        print("python contacts-remover.py input_file.pdf output_file.pdf")
        print("Directory example: ")
        print("python contacts-remover.py /input_directory/ /output_directory/" + "\n")
        sys.exit(-1)
    if len(sys.argv) > 3:
        print("\n"+ "INPUT ERROR: Please specify only one input/output pair of files or directories" + "\n")
        sys.exit(-1)
    #### End of input errors


    #### Determine if input is a pair of files or directories
    # Reckognize directory input
    if os.path.isdir(sys.argv[1]):
        # If 2nd directory input does not exist then create it
        if not os.path.isdir(sys.argv[2]):
            os.makedirs(sys.argv[2])
        # If directories are not an absolute path create it
        print(sys.argv[1] + sys.argv[2])
        sys.argv[1] = os.path.abspath(sys.argv[1])
        sys.argv[2] = os.path.abspath(sys.argv[2])
        if sys.argv[1][:-2:-1] != "/":
            sys.argv[1] = sys.argv[1] + "/"
        if sys.argv[2][:-2:-1] != "/":
            sys.argv[2] = sys.argv[2] + "/"
        print(sys.argv[1] + sys.argv[2])
        print("Author contact information will be removed from files in directory: " + (sys.argv[1]) + "  Contact free files will be created in directory: " + (sys.argv[2]))
        # (Excludes subdirectories and hidden files)
        files = [ f for f in os.listdir(sys.argv[1]) if os.path.isfile(sys.argv[1]+f) if not f.startswith('.') ]
        # Loop file(s)
        for a_file in files:
            infile = sys.argv[1] + a_file
            outfile = sys.argv[2] + a_file
            print(remove_contacts_in_pdf(infile, outfile))

    # Reckognize file input
    if os.path.isfile(sys.argv[1]):
        infile = sys.argv[1]
        outfile = sys.argv[2]
        print(remove_contacts_in_pdf(infile, outfile))
    #### End input detection
