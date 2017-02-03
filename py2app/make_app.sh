#!/bin/bash

echo "############### building ###############"
rm -rf build
sudo rm -rf dist
rm -rf Ctrax/*
cp -R ../Ctrax/* Ctrax/
cp Ctrax-script.py Ctrax/
for subcomp in 'kcluster2d' 'houghcircles' 'hungarian' 'tracking_funcs' 'psutil'
do
   rm -rf $subcomp
   cp -R ../$subcomp .
done

python setup_py2app.py py2app && \
  cp -R ../Ctrax/xrc dist/Ctrax.app/Contents/Resources/lib/python2.7 && \
  cp mac-xrc/* dist/Ctrax.app/Contents/Resources/lib/python2.7/xrc && \
  cp -R ../Ctrax/icons dist/Ctrax.app/Contents/Resources/lib/python2.7
