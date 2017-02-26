#!/usr/bin/bash -ex

cd ..
installer="./Ctrax-"`cat version.txt | tr -d '[:space:]'`"-installer.exe"
rm -f $installer

python setup_py2exe.py build
python setup_py2exe.py install
python setup_py2exe.py py2exe

cp maintain/dlls/* dist/
cp build/lib.win32-2.7/*pyd dist/

cp -R xrc dist/
cp -R icons dist/
cp -R mpl-data dist/

/cygdrive/c/Program\ Files\ \(x86\)/NSIS/makensis.exe setup.nsi
$installer

/cygdrive/c/Program\ Files\ \(x86\)/Ctrax-0.5/Ctrax.exe
