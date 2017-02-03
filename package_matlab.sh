#!/bin/bash

version=`tail -n 1 matlab/version_ctrax.m | cut -d' ' -f3 | cut -c2-7`
svn export . ~/ctraxmatlab-$version
cd ~/ctraxmatlab-$version

zip -r Ctrax-matlab-$version.zip matlab/
zip -r fixerrors-only-$version.zip fixerrors/
zip -r behavioralmicroarray-only-$version.zip behavioralmicroarray/
zip -r behavioralmicroarray-$version.zip behavioralmicroarray/ matlab/
zip -r fixerrors-$version.zip fixerrors/ matlab/
zip -r Ctrax-allmatlab-$version.zip fixerrors/ matlab/ behavioralmicroarray/
