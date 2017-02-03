#!/usr/bin/python

# adapted for Ctrax from
# http://www.webupd8.org/2010/12/launchpad-finally-gets-ppa-usage-stats.html
# JAB 3/12/12

import sys

try:
  from launchpadlib.launchpad import Launchpad
except ImportError:
  print "missing launchpadlib (Ubuntu package \'python-launchpadlib\')"
  exit( 1 )

lp_ = Launchpad.login_anonymously('ppastats', 'edge', None, version='devel')
owner = lp_.people['ctrax']
archive = owner.getPPAByName(name='ppa')

#desired_dist_and_arch = 'https://api.launchpad.net/devel/ubuntu/' + dist + '/' + arch

total_downloads = 0
total_downloads_curr = 0
print "\npackage name:\t\t\t\tstatus:\t\tdownloads:"
for individualarchive in archive.getPublishedBinaries():
   n = individualarchive.getDownloadCount()
   print individualarchive.display_name + "\t" + individualarchive.status + "\t" + str(n)
   if individualarchive.status == 'Published':
     total_downloads_curr += n
   total_downloads += n
print "\ntotal downloads:", total_downloads, "\n"
print "\ntotal downloads of current version:", total_downloads_curr, "\n"
