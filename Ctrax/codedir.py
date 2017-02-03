
import os

codedir = os.path.dirname(__file__)
while 'library.zip' in codedir: # Windows
    codedir, tail = os.path.split(codedir)
(head,tail) = os.path.split(codedir)
if tail == 'site-packages.zip': # Mac app
    codedir = head
