#!/usr/bin/env python

# main script for full Ctrax tracking tests
# JAB 5/10/11

import glob
import multiprocessing
import os
from subprocess import call
import tempfile
import time
import traceback
from types import NoneType, BooleanType, IntType, StringType, ListType, TupleType

from numpy import array

import datacompare
import filelist
from Ctrax import annfiles, movies

TEST_COMMAND_LINE = False
TEST_ACCURACY = True


def exec_ctrax( params, filename, to_null ):
    cmd = "Ctrax --Interactive=False --Input=%s " % filename
    cmd += params
    if to_null:
        cmd += " > /dev/null"

    print time.asctime(), cmd
    status = call( cmd, shell=True )
    if status == 139:
        print "**caught seg-fault on exit"
    elif status != 0:
        exit( status )

def main():
    ## test command-line execution ##
    if TEST_COMMAND_LINE:

        # get filename; one short movie
        files = filelist.CtraxFileList( ['short'] )
        tmp_files = files.movie_tempfiles()
        filename = tmp_files[0]
        settings_filename = files.ann_files()[0]

        # read number of frames in movie (to test offset parameters)
        mov = movies.Movie( filename )
        n_possible_frames = mov.get_n_frames()

        # run each combination of command-line parameters
        parms = {'Output': '.ann',
                 'AutoEstimateBackground': None, # => True/False
                 'AutoEstimateShape': None,
                 'CompressMovie': '.sbfmf',
                 'Matfile': '.mat',
                 'DiagnosticsFile': '_ctraxdiagnostics.txt',
                 'FirstFrameTrack': [10],
                 'LastFrameTrack': [90],
                 'EnforceShapeBounds': None,
                 'FlipMovieUD': None}

        cl_runtimes = []
        cl_framestracked = []

        def check_expected_count( load_file, n_expected_frames ):
            n_expected_frames = max( n_expected_frames, 0 )
            ann_file = annfiles.AnnotationFile( load_file, readonly=True )
            if len( ann_file ) != n_expected_frames:
                print "*************** expected %d frames in output file but Ctrax wrote %d **************" % (n_expected_frames, len( ann_file ))

        def run_with_args( arg_dict ):
            print arg_dict

            def get_expected_frames():
                n_expected_frames = n_possible_frames
                if 'LastFrameTrack' in arg_dict.keys():
                    n_expected_frames = min( n_expected_frames, arg_dict['LastFrameTrack'] )
                if 'FirstFrameTrack' in arg_dict.keys():
                    n_expected_frames -= arg_dict['FirstFrameTrack']
                return n_expected_frames

            def construct_command():
                cmd = "--SettingsFile=%s " % (settings_filename)
                for key in arg_dict.iterkeys():
                    cmd += '--%s=%s ' % (key, arg_dict[key])
                return cmd

            def check_files():
                files_to_rm = []
                for key in arg_dict.iterkeys():
                    if type( arg_dict[key] ) is StringType:
                        if os.path.isfile( arg_dict[key] ):
                            files_to_rm.append( arg_dict[key] )
                        else:
                            print "*************** Ctrax didn\'t create file for parameter %s **************" % key
                if 'FirstFrameTrack' in arg_dict.keys() or 'LastFrameTrack' in arg_dict.keys():
                    load_file = filename + ".ann"
                    if 'Output' in arg_dict.keys():
                        load_file = arg_dict['Output']
                    check_expected_count( load_file, n_expected_frames )

                return files_to_rm

            def delete_files( files_to_rm ):
                for rmfile in files_to_rm:
                    os.remove( rmfile )
                for rmfile in glob.iglob( '/tmp/*.ann' ):
                    os.remove( rmfile )
                for rmfile in glob.iglob( '/tmp/*.mat' ):
                    os.remove( rmfile )
                for rmfile in glob.iglob( '/tmp/*.sbfmf' ):
                    os.remove( rmfile )
                for rmfile in glob.iglob( '/tmp/Ctrax-test-data/bak*' ):
                    os.remove( rmfile )

            n_expected_frames = get_expected_frames()

            cmd = construct_command()

            starttime = time.time()

            exec_ctrax( cmd, filename, True )

            if n_expected_frames > 15:
                cl_runtimes.append( time.time() - starttime )
                cl_framestracked.append( n_expected_frames )

            files_to_rm = check_files()

            delete_files( files_to_rm )

        def construct_parms_and_run( this_args, index ):
            def get_val_list( val, parms, filename ):    
                if type( val ) is ListType or type( val ) is TupleType:
                    return val
                elif type( val ) is NoneType:
                    return (True, False)
                elif type( val ) is IntType:
                    return [val]
                elif type( val ) is StringType:
                    basename, ext = os.path.splitext( filename )
                    tempdata = tempfile.mkstemp( suffix=val )
                    os.close( tempdata[0] )
                    os.remove( tempdata[1] )
                    return [tempdata[1]]
                else:
                    raise NotImplementedError

            if index == len( parms ):
                run_with_args( this_args )
            else:
                key = parms.keys()[index]
                val_list = get_val_list( parms[key], parms, filename )

                for v in range( len( val_list ) + 1 ):
                    if v < len( val_list ):
                        this_args[key] = val_list[v]
                    else:
                        del this_args[key]
                    construct_parms_and_run( this_args, index + 1 )

        construct_parms_and_run( {}, 0 )

        # test ResumeTracking
        basename, ext = os.path.splitext( filename )
        tempdata = tempfile.mkstemp( suffix='.ann' )
        os.close( tempdata[0] )
        os.remove( tempdata[1] )
        outfile = tempdata[1]

        exec_ctrax( "--SettingsFile=%s --Output=%s --LastFrameTrack=20" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, 20 )
        exec_ctrax( "--SettingsFile=%s --Output=%s --ResumeTracking=True" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, n_possible_frames )
        os.remove( outfile )

        exec_ctrax( "--SettingsFile=%s --Output=%s --FirstFrameTrack=10 --LastFrameTrack=20" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, 10 )
        exec_ctrax( "--SettingsFile=%s --Output=%s --ResumeTracking=True" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, n_possible_frames - 10 )
        os.remove( outfile )

        exec_ctrax( "--SettingsFile=%s --Output=%s --FirstFrameTrack=90" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, n_possible_frames - 90 )
        exec_ctrax( "--SettingsFile=%s --Output=%s --ResumeTracking=True" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, n_possible_frames - 90 )
        os.remove( outfile )

        exec_ctrax( "--SettingsFile=%s --Output=%s" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, n_possible_frames )
        exec_ctrax( "--SettingsFile=%s --Output=%s --ResumeTracking=True" % (settings_filename, outfile), filename, True )
        check_expected_count( outfile, n_possible_frames )
        os.remove( outfile )


    ## test for tracking accuracy ##
    if TEST_ACCURACY:

        # get filenames
        files = filelist.CtraxFileList()
        tmp_files = files.movie_tempfiles()

        runtimes = multiprocessing.Manager().list()
        data = [(f, runtimes) for f in tmp_files]

        # run Ctrax on each file
        pool = multiprocessing.Pool( processes=3 )
        result = pool.map_async( run_file, data, chunksize=1 )
        pool.close()
        pool.join()
        if not result.successful():
            exit( 1 )

        # get Matlab to make readable versions of the test suite's original (fixed) MAT-files
        call( "matlab -nodisplay -nojvm -nosplash -r 'make_test_data; exit'", shell=True )

        # compare original MAT-data with newly generated MAT-data
        comparator = datacompare.CtraxDataComparator( files.resaved_mat_files(),
                                                      files.resaved_mat_tempfiles() )
        out_filename = comparator.save_data( files, runtimes )

        # run visualization in Matlab
        print "wrote tracking data to", out_filename
        call( "matlab -r \"plot_test_data_comparisons( '" + out_filename + "' )\"", shell=True )


    if TEST_COMMAND_LINE:
        total_framestracked = array( cl_framestracked ).sum()
        total_runtime = array( cl_runtimes ).sum()
        tracking_speed = (array( cl_framestracked )/array( cl_runtimes )).mean()
        print "mean speed for command-line tests: %f fps (%d frames in %d sec)" % (tracking_speed, total_framestracked, total_runtime)

def run_file( stuff ):
    """Execute Ctrax on a single file."""
    filename, runtimes = stuff
    starttime = time.time()
    try:
        exec_ctrax( "", filename, True )
    except:
        print traceback.format_exc()
        raise
    runtimes.append( time.time() - starttime )


if __name__ == '__main__':
    print "***** before testing, do 'sudo rm -r /usr/local/lib/python2.7/dist-packages/Ctrax/' and then rebuild!! *****"
    main()
