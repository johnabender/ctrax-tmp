#!/usr/bin/env python

import os
import sys

import numpy as num

NEW_VERSION = '0.5.7'
OLD_VERSION = '0.3.1'

SCRIPT_VERSION = '1.0.2'

"""
New annotation files:
- old:                 area0[j] = major0[j]*minor0[j]*num.pi*4.0
  new:                 area0[j] = major0[j]*minor0[j]*num.pi
  (relevant in estconncomps.trysplit())
- old:    eccen = minor / major
  new:    eccen = num.sqrt( major*major - minor*minor )/major
- ellipses don't store area, they calculate it
- enforce_minmax_shape in annfile (default True)
- movie_flipud in annfile
- bg_firstframe and bg_lastframe
- bg_norm_type changed to norm_type
- missing nframes_size, nstd_shape
"""

# import annfiles_057 as newann # "new format" = 0.5.7
# import bg_057 as newbg

# import annfiles_031 as oldann # "old format" = 0.3.1
# import bg_030 as oldbg

# class FakeMovie:
#     def __init__(self, h, w, n):
#         self.h = h
#         self.w = w
#         self.n = n
#         self.type = ''
#     def get_height(self):
#         return self.h
#     def get_width(self):
#         return self.w
#     def get_n_frames(self):
#         return self.n

# def convert_up(filename, h, w, start_frame, n_frames):
#     """
#     Convert a file from old format to new format.
#     Requires image height, width, number of frames (read from old file).
#     """
#     # this doesn't work correctly yet - runs, but values are wrong -JAB 4/23/16
#     out_filename = filename + ".upconverted"
#     if os.access(out_filename, os.F_OK):
#         os.remove(out_filename)
#     out_file = newann.AnnotationFile(out_filename)

#     mov = FakeMovie(h, w, n_frames)
#     ref_bg = oldbg.BackgroundCalculator(mov)
#     ref_file = oldann.AnnotationFile(filename, doreadtrx=True, readonly=True)

#     out_bg = newbg.BackgroundCalculator(mov)
#     out_file.InitializeData(start_frame, bg_model=out_bg)

#     print out_filename
#     for fr in ref_file:
#         out_file.append(fr)
#     out_file.close()

def convert_up(filename):
    """
    Convert a file from old format to new format.
    """
    out_filename = filename + ".upconverted"
    if os.access(out_filename, os.F_OK):
        os.remove(out_filename)

    print "upconverting", filename, "to", out_filename

    with open(filename, 'r') as infile:
        with open (out_filename, 'w') as outfile:
            majmin = {}
            wrote_new_headers = False

            for line in infile:
                try:
                    key, val = line.strip().split(':')
                except ValueError:
                    outfile.write(line)
                    continue

                if key == 'version':
                    outfile.write(key + ':' + NEW_VERSION + '\n')
                elif not wrote_new_headers:
                    outfile.write('enforce_minmax_shape:0\n')
                    wrote_new_headers = True
                elif key == 'norm_type':
                    outfile.write('bg_norm_type:' + val + '\n')
                elif 'area' in key:
                    try:
                        val = float(val)
                    except ValueError:
                        print "couldn't cast", val, "for 'area' in", key
                        outfile.write(line)
                    else:
                        outfile.write(key + ':' + str(val/4.) + '\n')
                        print "converted %s from %f to %f in %s" % (key, val, val/4., out_filename)
                elif key.endswith('ecc'):
                    common = key[:key.index('ecc')]
                    if (common + 'major' in majmin) and (common + 'minor' in majmin):
                        major = majmin[common + 'major']
                        minor = majmin[common + 'minor']
                        newval = num.sqrt( major*major - minor*minor )/major
                        outfile.write(key + ':' + str(newval) + '\n')
                        print "converted %s from %s to %s in %s" % (key, val, newval, out_filename)
                    else:
                        print "got 'ecc' key", key, "but no major/minor to recalculate"
                        outfile.write(line)
                elif key == 'nframes_size' or key == 'nstd_shape' or key == 'expbgfgmodel_filename':
                    continue
                else:
                    outfile.write(line)

                    if ('major' in key) or ('minor' in key):
                        try:
                            majmin[key] = float(val)
                        except ValueError:
                            print "couldn't cast", val, "for 'major/minor' in", key


def convert_down(filename):
    """
    Convert a file from new format to old format.
    """
    out_filename = filename + ".downconverted"
    if os.access(out_filename, os.F_OK):
        os.remove(out_filename)


def convert_file(filename):
    """
    Determine whether to convert from old version up or from new version down.
    Then run conversion.
    """
    if not os.access(filename, os.R_OK):
        print "couldn't read %s, skipping" % filename
        return

    with open(filename, 'r') as fp:
        line = fp.readline().strip()
        if line != 'Ctrax header':
            print "%s doesn't appear to be a Ctrax annotation file, skipping" % filename
            return

        line = fp.readline().strip()
        if not line.startswith('version:'):
            print "error parsing version from %s, skipping" % filename
            return

        ver = line[len('version:'):]
        if ver.startswith('0.3'): # could be others too...
            # while 'movie_height:' not in line:
            #     line = fp.readline().strip()
            # h = int(line[line.index('movie_height:') + len('movie_height:'):])
            # line = fp.readline().strip()
            # if not line.startswith('movie_width:'):
            #     print "couldn't find movie_width in %s, skipping" % filename
            #     return
            # w = int(line[len('movie_width:'):])
            # while line and (not line.startswith('start_frame')):
            #     line = fp.readline().strip()
            # if not line:
            #     print "couldn't find start_frame in %s, skipping" % filename
            #     return
            # start_frame = int(line[len('start_frame:')])
            # while line and (line != 'end header'):
            #     line = fp.readline().strip()
            # if not line:
            #     print 'improper header in %s, skipping' % filename
            #     return
            # n_frames = 0
            # while line:
            #     n_frames += 1
            #     line = fp.readline()
            # convert_up(filename, h, w, start_frame, n_frames)
            convert_up(filename)
        else:
            convert_down(filename)


if __name__ == '__main__':
    filelist = sys.argv[1:]
    for filename in filelist:
        convert_file(filename)
