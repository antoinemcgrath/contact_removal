This script removes author contact information from CRS reports.

python contacts-remover.py /input.pdf /output.pdf

*Requires that the input pdf be decoded.

The method:
CRS/LOC/GOV emails and telephone numbers are detected within specific PDF objects. Object are mapped, then specific contact characters are replaced with blank spaces. This method is more comprehensive than prior versions. Please report any contact removal failures.

.py script built upon (https://github.com/billmarczak)'s mapping method. 
