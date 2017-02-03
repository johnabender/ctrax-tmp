function test_annfiles_read
% test reading a .mat file saved by test_annfiles.py
% JAB 1/14/13

mat_filename = '/home/jbender/ann_data_test/test.mat';
success_filename = '/home/jbender/ann_data_test/mat_test_success.txt';

success = 1;

data = load_tracks( mat_filename );
if length( data ) == 5
   for fl = 1:length( data )
      if length( data(fl).x == 10 )
         if data(fl).id == fl - 1
            for fr = 1:length( data(fl).x )
               if data(fl).x(fr) ~= fl + fr - 1
                  fprintf( 1, 'expected x value %f for fly %d frame %d, got %f\n', fl + fr, fl - 1, fr - 1, data(fl).x(fr) );
                  success = 0;
               end
               if data(fl).b(fr) ~= 10*fl
                  fprintf( 1, 'expected width value %f for fly %d frame %d, got %f\n', 10*fl, fl - 1, fr - 1, data(fl).b(fr) );
                  success = 0;
               end
            end
         else
            fprintf( 1, 'expected id %d for fly %d, got %d\n', fl - 1, fl - 1, data(fl).id );
            success = 0;
         end
      else
         fprintf( 1, 'fly %d was expected to have 10 flies, had %d\n', fl, length( data(fl).x ) );
         success = 0;
      end
   end
else
   fprintf( 1, 'MAT-file was expected to have 5 flies, had %d\n', length( data ) );
   success = 0;
end

fp = fopen( success_filename, 'w' );
fprintf( fp, '%d', success );
fclose( fp );


