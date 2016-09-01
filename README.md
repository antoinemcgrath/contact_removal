This script removes author contact information from CRS reports.

Acting on a CRS file labeled as "one" this script will output test-test-test (an uncompressed pdf document).

The method:
Email CRS/LOC/GOV email addresses are detected in sections of the documents (objects).
Although this information appears on a single line within the PDF it is encoded into many segments. 
A consistent way of tracking all segments is to find the “print” (a formatting number sequence paired with “Tm”.  
In this case “600.0009 Tm” 
If the print occurs before the contact segment it is named as a "thumbprint"
If it occurs after the segment it is named a "pinkyprint". 
The thumb/printprint regex is then applied to both print lists giving us lists of strings. 
Finally the strings are then removed globally from the entire doc which is var "data" and saved as test-test-test

The decoded crs document for test contact removal is titled "one"
A suggested decoding bash method is qpdf
