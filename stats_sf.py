#!/usr/bin/python

# JAB 10/19/13

import json
import sys
import time
import urllib

host = 'https://sourceforge.net'
base_path = '/projects/ctrax/files/'
ctrax_dirs = (('Ctrax%20in%20Windows',
               ('Ctrax-%s-installer.exe',)),
              ('Ctrax%20in%20Mac%20OS',
               ('Ctrax-%s.pkg',)),
              ('Ctrax%20in%20Linux',
               ('python-ctrax_%s-1_amd64.deb', 'python-ctrax_%s-1_i386.deb')),
              ('Ctrax%20source',
               ('Ctrax-%s.tar.gz',)))
matlab_dirs = (('Matlab%20complete',
                ('Ctrax-allmatlab-%s.zip',)),
               ('Matlab%20BehavioralMicroarray',
                ('Ctrax-matlab-%s.zip',
                 'behavioralmicroarray-only-%s.zip',
                 'behavioralmicroarray-%s.zip')),
               ('Matlab%20FixErrors',
                ('Ctrax-matlab-%s.zip',
                 'fixerrors-only-%s.zip',
                 'fixerrors-%s.zip')))

oldest_date = '2011-06-01'
now = time.gmtime()
newest_date = '%d-%d-%d' % (now.tm_year, now.tm_mon, now.tm_mday)

def number_for_path( path ):
    file_path = base_path + path + "/stats/json?start_date=" + oldest_date + "&end_date=" + newest_date
    print path, "\t",

    conn = urllib.urlopen( host+file_path )

    if conn.getcode() == 200:
        file_data = json.loads( conn.read() )
        num = file_data['summaries']['time']['downloads']
        print num
        return num
    else:
        print file_path, "??", conn.getcode()
        raise IOError


for file_type in ('ctrax', 'matlab'):
    file_dirs = eval( file_type + "_dirs" )
    alltime_downloads = 0
    version_downloads = 0

    for file_info in file_dirs:
        file_dir, file_patterns = file_info
        alltime_downloads += number_for_path( file_dir )

        if len( sys.argv ) > 1:
            for file_pattern in file_patterns:
                file_name = file_pattern % sys.argv[1]
                try:
                    version_downloads += number_for_path( file_dir + "/" + file_name )
                except IOError:
                    pass


    print "\n\t", file_type, "cumulative downloads:", alltime_downloads
    if version_downloads > 0:
        print "\t", file_type, sys.argv[1], "total downloads:", version_downloads
    print
