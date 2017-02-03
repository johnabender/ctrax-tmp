#!/bin/bash

mkdir -p ~/ctraxsource

version=`cat version.txt`
svn export . ~/ctraxsource/Ctrax-$version
cd ~/ctraxsource/Ctrax-$version || exit 1

rm -r behavioralmicroarray
rm -rf build
rm -rf dist
rm -r fixerrors
rm -r matlab

rm -r stats_*.py
rm -r *.sh

cd ..
tar czf Ctrax-$version.tar.gz Ctrax-$version
