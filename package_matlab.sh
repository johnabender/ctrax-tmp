#!/bin/bash

version=`tail -n 1 matlab/version_ctrax.m | cut -d' ' -f3 | cut -c2-7`
git checkout-index -a --prefix=/home/jbender/ctraxmatlab-$version/
cd ~/ctraxmatlab-$version || exit 1

zip -r Ctrax-matlab-$version.zip matlab/
zip -r fixerrors-only-$version.zip fixerrors/
zip -r behavioralmicroarray-only-$version.zip behavioralmicroarray/
zip -r behavioralmicroarray-$version.zip behavioralmicroarray/ matlab/
zip -r fixerrors-$version.zip fixerrors/ matlab/
zip -r Ctrax-allmatlab-$version.zip fixerrors/ matlab/ behavioralmicroarray/
