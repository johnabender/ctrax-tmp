#!/usr/bin/bash -ex

rm -rf ../build
rm -rf ../dist

python copy_files_here.py
python removepkgresources.py
python replacemotmotimports.py
python update_version_number.py
 
