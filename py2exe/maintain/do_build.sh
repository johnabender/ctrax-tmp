#!/usr/bin/bash

cd ..
installer="./Ctrax-"`cat version.txt | tr -d '[:space:]'`"-installer.exe"
rm -f $installer

python setup_py2exe.py build || exit 1
python setup_py2exe.py install || exit 1
python setup_py2exe.py py2exe || exit 1

cp maintain/dlls/* dist/
cp build/lib.win32-2.7/*pyd dist/

cp -R xrc dist/
cp -R icons dist/
cp -R mpl-data dist/

/cygdrive/c/Program\ Files\ \(x86\)/NSIS/makensis.exe setup.nsi || exit 1
$installer || exit 1

/cygdrive/c/Program\ Files\ \(x86\)/Ctrax-0.5/Ctrax.exe
