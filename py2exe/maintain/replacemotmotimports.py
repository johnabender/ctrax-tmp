import os, glob

for filename in glob.glob(os.path.join('..','*.py')):
    if filename == 'removepkgresources.py' or filename == "setup.py" or filename == "setup_py2exe.py" or filename == "replacemotmotimports.py":
        continue
    fidin = open(filename,'r')
    (head,tail) = os.path.split(filename)
    tmpfilename = os.path.join(head,'rmi_tmp_' + tail)
    fidout = open(tmpfilename,'w')
    lineno = 0
    ischange = False
    print "\n\nProcessing file = %s:"%filename
    for line in fidin:
        lineno+=1
        allsnew = ['imops','wxvalidatedtext','wxvideo','ufmf','arrayimage','FlyMovieFormat']
        alls = ['motmot.imops.imops','motmot.wxvalidatedtext.wxvalidatedtext',
                'motmot.wxvideo.wxvideo','motmot.ufmf.ufmf','pygarrayimage.arrayimage','motmot.FlyMovieFormat.FlyMovieFormat']
        for i in range(len(alls)):
            s = alls[i]
            snew = allsnew[i]
            motmot = line.find(s)
            if motmot >= 0:
                line = line.replace(s,snew)
                ischange = True
                print "[%s:%d] Replaced %s:\n  %s"%(filename,lineno,snew,line)
        fidout.write(line)
    fidin.close()
    fidout.close()
    if ischange:
        print "Replacing old %s"%filename
        os.remove(filename)
        os.rename(tmpfilename,filename)
    else:
        print "No changes made to %s"%filename
        os.remove(tmpfilename)
