# corresponds to version 0.6.5 of fview and 0.5.8 of flytrax

import shutil
import stat
import os.path
from glob import glob

# directories
from motmot import __path__ as motmotpath
from pygarrayimage import __path__ as pygarrayimagepath
Ctraxpath = os.path.join('..','..')

# things to copy here with the same base name, use wild cards
tocopy = {}

# Ctrax stuff
tocopy['kcluster2d'] = [os.path.join(Ctraxpath,'kcluster2d','kcluster2d_cython.pyx'),]
tocopy['tracking_funcs'] = [os.path.join(Ctraxpath,'tracking_funcs','tracking_funcs.pyx'),]
tocopy['hungarian'] = glob(os.path.join(Ctraxpath,'hungarian','*.cpp'))+\
    glob(os.path.join(Ctraxpath,'hungarian','*.h'))
tocopy['houghcircles'] = glob(os.path.join(Ctraxpath,'houghcircles','*.c'))
tocopy['Ctrax'] = glob(os.path.join(Ctraxpath,'Ctrax','*.py'))
tocopy['Ctrax'].append( os.path.join( Ctraxpath, 'Ctrax', 'Ctrax' ) )

# motmot stuff
motmot_pkgs = ['imops', 'ufmf', 'wxvalidatedtext', 'wxvideo']
motmot_pkg_files = [['imops.pyd'], ['ufmf.py'], ['wxvalidatedtext.py'], ['wxvideo.py']]
for pkg_name, pkg_files in zip( motmot_pkgs, motmot_pkg_files ):
    # find matching motmot path
    for mpath in motmotpath:
        if pkg_name in mpath:
            # append path name for each file needing copy
            pkg_paths = []
            for pfile in pkg_files:
                filename = os.path.join( mpath, pkg_name, pfile )
                if not os.access( filename, os.R_OK ):
                    filename = os.path.join( '.', 'py-sources', pfile )
                    if not os.access( filename, os.R_OK ):
                        raise NameError( "couldn't find %s anywhere"%filename )
                pkg_paths.append( filename )
            tocopy[pkg_name] = pkg_paths
    if pkg_name not in tocopy.keys(): print "couldn't find %s"%pkg_name
                
# pygarrayimage
pygarrayimagepath = pygarrayimagepath[0]
if '.egg' in pygarrayimagepath:
    head = pygarrayimagepath
    tail = ''
    tails = []
    while '.egg' in head:
        head, tail = os.path.split( head )
        tails.append( tail )
    for tail in reversed( tails[:-1] ):
        head = os.path.join( head, tail )
    pygarrayimagepath = head
tocopy['pygarrayimage'] = [os.path.join(pygarrayimagepath,'arrayimage.py'),]

# package build files
for (name,srcs) in tocopy.iteritems():
    print '\n%s : '%name
    for src in srcs:
        dst = os.path.join('..',os.path.basename(src))
        print 'cp %s %s'%(src,dst)
        shutil.copy(src,dst)
        os.chmod(dst, stat.S_IRWXU)


def copydir(name,srcdirname,dstdirname,pattern):
    print '\n%s:'%name
    if not os.path.isdir(dstdirname):
        os.mkdir(dstdirname)
        print 'mkdir %s'%dstdirname
    for src in glob(os.path.join(srcdirname,pattern)):
        dst = os.path.join(dstdirname,os.path.basename(src))
        print 'cp %s %s'%(src,dst)
        shutil.copy(src,dst)
        os.chmod(dst, stat.S_IRWXU)
    
# icons directory
srcdirname = os.path.join(Ctraxpath,'Ctrax','icons')
dstdirname = os.path.join('..','icons')
pattern = '*.ico'
name = 'icons'
copydir(name,srcdirname,dstdirname,pattern)

# xrc directory
srcdirname = os.path.join(Ctraxpath,'Ctrax','xrc')
dstdirname = os.path.join('..','xrc')
name = 'xrc'
copydir(name,srcdirname,dstdirname,'*.xrc')
copydir(name,srcdirname,dstdirname,'*.bmp')

# psutil directories
srcdirname = os.path.join(Ctraxpath,'psutil')
dstdirname = os.path.join('..','psutil')
print "\npsutil %s %s" % (srcdirname, dstdirname)
shutil.rmtree( dstdirname, ignore_errors=True )
shutil.copytree( srcdirname, dstdirname )
