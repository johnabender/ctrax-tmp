
# fill Ctrax version numbers into template

import sys
sys.path.insert( 0, '..' )
from version import __version__

longversion = __version__
shortversion = __version__
i = shortversion.rfind( '.' )
if i > 0:
    shortversion = shortversion[:i]


template = open( '../setup.nsi.template', 'r' )
outfile = open( '../setup.nsi', 'w' )

for line in template:
    outline = line.replace( '{ctraxlongversion}', longversion )
    outline = outline.replace( '{ctraxshortversion}', shortversion )
    outfile.write( outline )

outfile.close()
template.close()
