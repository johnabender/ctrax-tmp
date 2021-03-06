#!/usr/bin/env python

import py2app
from setuptools import setup, Extension
from Cython.Distutils import build_ext
import numpy
import os, glob
import sys

from modulegraph import modulegraph
modulegraph.addPackagePath('psutil', 'build/bdist.macosx-10.6-x86_64/lib.macosx-10.6-x86_64-2.7/psutil/')

# include numpy directories for extensions
numpyincludedirs = numpy.get_include()

# read version number from version file
path = os.path.abspath( os.curdir )
Ctrax_path = os.path.join( path, 'Ctrax' )
ver_filename = os.path.join( Ctrax_path, 'version.py' )
ver_file = open( ver_filename, "r" )
for line in ver_file: # parse through file version.py
    if line.find( '__version__' ) >= 0:
        line_sp = line.split() # split by whitespace
        version_str = line_sp[2] # third item
        this_version = version_str[1:-1] # strip quotes
ver_file.close()

# write version number to text file
ver_filename = os.path.join( path, 'version.txt' )
ver_file = open( ver_filename, "w" )
ver_file.write( '%s\n'%this_version )
ver_file.close()

def get_psutilver():
    INIT = 'psutil/__init__.py'
    with open(INIT, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                ret = eval(line.strip().split(' = ')[1])
                assert ret.count('.') == 2, ret
                for num in ret.split('.'):
                    assert num.isdigit(), ret
                return ret

extensions = [Extension('hungarian',['hungarian/hungarian.cpp',
                                     'hungarian/asp.cpp'],
                        include_dirs=[numpyincludedirs,]),
              Extension('houghcircles_C',
                        ['houghcircles/houghcircles_C.c'],
                        include_dirs=[numpyincludedirs,]),
              Extension('kcluster2d',
                        ['kcluster2d/kcluster2d_cython.pyx'],
                        include_dirs=[numpyincludedirs,]),
              Extension('tracking_funcs',
                        ['tracking_funcs/tracking_funcs.pyx'],
                        include_dirs=[numpyincludedirs,]),
              Extension('psutil._psutil_posix',
                        sources=['psutil/_psutil_posix.c']),
              Extension('psutil._psutil_osx',
                        sources=['psutil/_psutil_osx.c',
                                  'psutil/_psutil_common.c',
                                  'psutil/arch/osx/process_info.c'],
                                  define_macros=[('PSUTIL_VERSION', int(get_psutilver().replace('.', '')))],
                                  extra_link_args=['-framework', 'CoreFoundation',
                                                   '-framework', 'IOKit'])]

# add all of the .xrc and .bmp files
Ctrax_package_data = [ f[6:] for f in glob.glob(os.path.join('Ctrax','xrc','*.xrc'))]+\
                     [ f[6:] for f in glob.glob(os.path.join('Ctrax','icons','*.ico'))]+\
                     [ f[6:] for f in glob.glob(os.path.join('Ctrax','xrc','*.bmp'))]

long_description = """
Ctrax: The Caltech Multiple Fly Tracker

(c) 2007-2017 The Caltech Ethomics Project
http://ctrax.sourceforge.net
bransonk@janelia.hhmi.org

Ctrax is an open-source, freely available, machine vision program for
estimating the positions and orientations of many walking flies,
maintaining their individual identities over long periods of time. It
was designed to allow high-throughput, quantitative analysis of
behavior in freely moving flies. Our primary goal in this project is
to provide quantitative behavior analysis tools to the neuroethology
community, thus we've endeavored to make the system adaptable to other
labs' setups. We have assessed the quality of the tracking results for
our setup, and found that it can maintain fly identities indefinitely
with minimal supervision, and on average for 1.5 fly-hours
automatically.
"""

classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: C',
    'Programming Language :: C++',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ]

requires=['cython',
          'matplotlib',
          'motmot.imops',
          'motmot.ufmf',
          'motmot.wxvalidatedtext',
          'motmot.wxvideo',
          'numpy',
          'opencv',
          'PIL',
          'scipy',
          'wx',
          ]

setup( 
    name="Ctrax",
    version=this_version,
    author="Caltech Ethomics Project",
    author_email="bransonk@janelia.hhmi.org",
    maintainer="Kristin Branson",
    maintainer_email="bransonk@janelia.hhmi.org",
    url="http://ctrax.sourceforge.net",
    description="Ctrax: The Caltech Multiple Fly Tracker",
    long_description=long_description,
    download_url="http://sourceforge.net/projects/ctrax/",
    classifiers=classifiers,
    platforms=['Windows','Linux','MacOS X'],
    packages=['Ctrax'],
    requires=requires,
    provides=['Ctrax'],
    obsoletes=['mtrax'],
    scripts=['Ctrax/Ctrax'],
    cmdclass = {'build_ext': build_ext},
    package_dir={'Ctrax': 'Ctrax'},
    package_data = {'Ctrax': Ctrax_package_data},
    ext_modules=extensions,
    app=['Ctrax/Ctrax-script.py'],
    options={'py2app': {'iconfile': 'Ctrax/icons/Ctraxicon.icns',
                        'plist': {'CFBundleIdentifier': 'edu.caltech.ctrax',
                                  'NSHumanReadableCopyright': '2007-2017 Kristin Branson/Caltech Ethomics Project',
                                  'LSApplicationCategoryType': 'public.app-category.utilities',
                                  'CFBundleDocumentTypes': [{'CFBundleTypeExtensions': ['fmf'],
                                                             'CFBundleTypeIconFile': 'Ctrax/icons/drosophila.icns',
                                                             'CFBundleTypeRole': 'Viewer'},
                                                             {'CFBundleTypeExtensions': ['sbfmf'],
                                                             'CFBundleTypeIconFile': 'Ctrax/icons/drosophila-grag.icns',
                                                             'CFBundleTypeRole': 'Viewer'},
                                                             {'CFBundleTypeExtensions': ['ufmf'],
                                                             'CFBundleTypeIconFile': 'Ctrax/icons/drosophila-orange.icns',
                                                             'CFBundleTypeRole': 'Viewer'},
                                                             {'CFBundleTypeExtensions': ['avi'],
                                                             'CFBundleTypeRole': 'Viewer'}
                                                            ]
                                 }
                        }
            }
)
