
# fill Ctrax version numbers into template

import sys
sys.path.insert( 0, '..' )
from version import __version__

longversion = __version__
shortversion = __version__
i = shortversion.rfind( '.' )
if i > 0:
    shortversion = shortversion[:i]

with open( '../setup.nsi.template', 'r' ) as template:
    with open( '../setup.nsi', 'w' ) as outfile:
        for line in template:
            outline = line.replace( '{ctraxlongversion}', longversion )
            outline = outline.replace( '{ctraxshortversion}', shortversion )
            outfile.write( outline )

with open('../version.txt', 'w') as verfile:
    verfile.write('{!s}\n'.format(longversion))