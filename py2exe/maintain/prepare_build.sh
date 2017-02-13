#!/usr/bin/bash

rm -rf ../build
rm -rf ../dist

python copy_files_here.py || exit 1
python removepkgresources.py || exit 1
python replacemotmotimports.py || exit 1
python update_version_number.py || exit 1
 
