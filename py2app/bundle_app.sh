#!/bin/bash -x

echo "############### bundling ###############"

# sign executables
codesign -s QUR2LGYJJW --entitlements Ctrax.entitlements dist/Ctrax.app/Contents/MacOS/Ctrax
codesign -s QUR2LGYJJW --entitlements python.entitlements dist/Ctrax.app/Contents/MacOS/python

# build and sign .pkg
#productbuild --component dist/Ctrax.app /Applications --sign QUR2LGYJJW dist/Ctrax-`cat version.txt`.pkg
productbuild --component dist/Ctrax.app /Applications dist/Ctrax-`cat version.txt`.pkg

# test installer
sudo rm -r dist/Ctrax.app
sudo rm -r /Applications/Ctrax.app
sudo installer -store -pkg dist/Ctrax-`cat version.txt`.pkg -target /
   CTRAX_NO_REDIRECT=1 /Applications/Ctrax.app/Contents/MacOS/Ctrax /Users/jbender/src/janelia/ctrax/trunk/py2app/test-movies/batch-test/movie20100707_141914_trimmed2.fmf
#/Users/jbender/src/janelia/ctrax/trunk/py2app/test-movies/norpix\ compression.avi
