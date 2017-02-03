#!/usr/bin/env python

import atexit
import contextlib
import glob
import io
import os
import sys
import tempfile

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from Cython.Distutils import build_ext
import numpy

# include numpy directories for extensions
numpyincludedirs = numpy.get_include()

# read version number from version file
path = os.path.abspath( os.curdir )
Ctrax_path = os.path.join( path, 'Ctrax' )
ver_filename = os.path.join( Ctrax_path, 'version.py' )
with open( ver_filename, "r" ) as ver_file:
  for line in ver_file: # parse through file version.py
      if line.find( '__version__' ) >= 0:
          line_sp = line.split() # split by whitespace
          version_str = line_sp[2] # third item
          this_version = version_str[1:-1] # strip quotes

if False and 'clean' in sys.argv and '-a' in sys.argv:
  print "clean build - not updating Ctrax version.txt"
else:
  # write version number to text file
  ver_filename = os.path.join( path, 'version.txt' )
  with open( ver_filename, "w" ) as ver_out:
    ver_out.write( '%s\n'%this_version )

# psutils stuff
@contextlib.contextmanager
def silenced_output(stream_name):
    class DummyFile(io.BytesIO):
        # see: https://github.com/giampaolo/psutil/issues/678
        errors = "ignore"

        def write(self, s):
            pass

    orig = getattr(sys, stream_name)
    try:
        setattr(sys, stream_name, DummyFile())
        yield
    finally:
        setattr(sys, stream_name, orig)

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

# add all of the .xrc and .bmp files
# where 6 == len( 'Ctrax/' )
Ctrax_package_data = [ f[6:] for f in glob.glob(os.path.join('Ctrax','xrc','*.xrc'))]+\
                     [ f[6:] for f in glob.glob(os.path.join('Ctrax','icons','*.ico'))]+\
                     [ f[6:] for f in glob.glob(os.path.join('Ctrax','xrc','*.bmp'))]


# determine setup config for psutil (1.0.1)
if sys.platform.startswith("linux"):
    def get_ethtool_macro():
        # see: https://github.com/giampaolo/psutil/issues/659
        from distutils.unixccompiler import UnixCCompiler
        from distutils.errors import CompileError

        with tempfile.NamedTemporaryFile(
                suffix='.c', delete=False, mode="wt") as f:
            f.write("#include <linux/ethtool.h>")

        @atexit.register
        def on_exit():
            try:
                os.remove(f.name)
            except OSError:
                pass

        compiler = UnixCCompiler()
        try:
            with silenced_output('stderr'):
                with silenced_output('stdout'):
                    compiler.compile([f.name])
        except CompileError:
            return ("PSUTIL_ETHTOOL_MISSING_TYPES", 1)
        else:
            return None

    ETHTOOL_MACRO = get_ethtool_macro()
    macros = [('PSUTIL_VERSION', int(get_psutilver().replace('.', '')))]
    if ETHTOOL_MACRO is not None:
        macros.append(ETHTOOL_MACRO)
    psutil_extensions = [Extension('psutil._psutil_linux',
                                   sources=['psutil/_psutil_linux.c'],
                                   define_macros=macros),
                         Extension('psutil._psutil_posix',
                                   sources=['psutil/_psutil_posix.c'],
                                   include_dirs=['psutil'])]



long_description = """
Ctrax: The Caltech Multiple Fly Tracker

(c) 2007-2016 The Caltech Ethomics Project
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
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
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
              ]
# If this line errors, you're not building on a known platform.
extensions.extend( psutil_extensions )

setup( name="Ctrax",
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
       requires=requires,
       provides=['Ctrax'],
       obsoletes=['mtrax'],
       scripts=['Ctrax/Ctrax'],
       cmdclass = {'build_ext': build_ext},
       packages=['Ctrax', 'psutil'],
       package_dir={'Ctrax': 'Ctrax', 'psutil': 'psutil'},
       package_data = {'Ctrax':Ctrax_package_data},
       ext_modules=extensions
      )
