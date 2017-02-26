#!/usr/bin/env python

import numpy
import os, glob
import sys

from setuptools import setup, Extension
from Cython.Distutils import build_ext
import py2exe

# include directories for hungarian
numpyincludedirs = numpy.get_include()

# read version number from version file
ver_file = open( "version.py", "r" )
for line in ver_file: # parse through file version.py
    if line.find( '__version__' ) >= 0:
        line_sp = line.split() # split by whitespace
        version_str = line_sp[2] # third item
        this_version = version_str[1:-1] # strip quotes
ver_file.close()

# write version number to text file
ver_file = open( "version.txt", "w" )
ver_file.write( '%s\n'%this_version )
ver_file.close()


# add all of the .xrc and .bmp files
Ctrax_data_files = [('xrc',glob.glob(os.path.join('xrc','*.xrc'))),
                    ('xrc',glob.glob(os.path.join('xrc','*.bmp'))),
                    ('icons',glob.glob(os.path.join('icons','*.ico')))]
Ctrax_package_data = ['icons/*.ico','xrc/*.xrc','xrc/*.bmp']
print 'Ctrax_package_data: ',Ctrax_package_data
print 'Ctrax_data_files: ',Ctrax_data_files

def get_winver():
    maj, min = sys.getwindowsversion()[0:2]
    return '0x0%s' % ((maj * 100) + min)

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

includes = ['scipy.cluster.vq',
            'scipy.io.matlab.streams', 
            'scipy.sparse.csgraph._validation',
            'scipy.special._ufuncs_cxx',
            'scipy.linalg.*',
            'matplotlib.backends.backend_tkagg']

extensions = [Extension('hungarian',['hungarian.cpp',
                                     'asp.cpp'],
                        include_dirs=[numpyincludedirs,]),
              Extension('houghcircles_C',
                        ['houghcircles_C.c'],
                        include_dirs=[numpyincludedirs,]),
              Extension('kcluster2d',
                        ['kcluster2d_cython.pyx'],
                        include_dirs=[numpyincludedirs,]),
              Extension('tracking_funcs',
                        ['tracking_funcs.pyx'],
                        include_dirs=[numpyincludedirs,]),
              Extension('psutil._psutil_windows',
                        sources=[
                            'psutil/_psutil_windows.c',
                            'psutil/_psutil_common.c',
                            'psutil/arch/windows/process_info.c',
                            'psutil/arch/windows/process_handles.c',
                            'psutil/arch/windows/security.c',
                            'psutil/arch/windows/inet_ntop.c',
                            'psutil/arch/windows/services.c',
                        ],
                        define_macros=[
                            ('PSUTIL_VERSION', int(get_psutilver().replace('.', ''))),
                            # be nice to mingw, see:
                            # http://www.mingw.org/wiki/Use_more_recent_defined_functions
                            ('_WIN32_WINNT', get_winver()),
                            ('_AVAIL_WINVER_', get_winver()),
                            ('_CRT_SECURE_NO_WARNINGS', None),
                            # see: https://github.com/giampaolo/psutil/issues/348
                            ('PSAPI_VERSION', 1),
                        ],
                        libraries=[
                            "psapi", "kernel32", "advapi32", "shell32", "netapi32",
                            "iphlpapi", "wtsapi32", "ws2_32",
                        ])
              ]

import matplotlib

setup( windows=[{"script": 'Ctrax',
                 "icon_resources": [(1,"icons/Ctraxicon.ico")]}],
       name="Ctraxexe",
       version=this_version,
       description="The Caltech Multiple Fly Tracker",
       author="Caltech Ethomics Project",
       author_email="bransonk@janelia.hhmi.org",
       url="http://ctrax.sourceforge.net",
       cmdclass = {'build_ext': build_ext},
       data_files = Ctrax_data_files,
       packages=['Ctrax', 'psutil'],
       package_dir={'Ctrax': '.', 'psutil': 'psutil'},
       package_data = {'Ctrax':Ctrax_package_data},
       ext_modules = extensions,
       options={"py2exe":{
           "includes": includes,
           "dll_excludes": [
                 "MSVFW32.dll",
                 "AVIFIL32.dll",
                 "AVICAP32.dll",
                 "ADVAPI32.dll",
                 "CRYPT32.dll",
                 "WLDAP32.dll"],
       }},
#       data_files=matplotlib.get_py2exe_datafiles(),
       )
