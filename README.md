*This version expands the encoded PDF document, removes the author contacts, then compresses the file.

Single file:
python contacts-remover.py input.pdf output.pdf

Entire directory (be certain that directory contents are CRS PDFs):
python contacts-remover.py /input_directory/ /output_directory/


The method:
CRS/LOC/GOV emails and telephone numbers are detected within specific PDF objects. Objects are mapped, then specific contact characters are replaced with blank spaces. This method is more comprehensive than prior versions. Please report any contact removal failures.

This python script is built on (https://github.com/billmarczak)'s mapping version: https://github.com/antoinemcgrath/contact_removal/commit/ea9635c61c793859aee0d888e10e95da2c85af52 and qpdf**)


**Please do not include spaces in the document names or directories
**QPDF is used to expand and condense CRS reports files it is released under the terms of Version 2.0 of the Artistic License. Visit the site http://qpdf.sourceforge.net/ for additional information.
