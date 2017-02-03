function plot_test_data_comparisons( dump_filename )
% plot_test_data_comparisons( dump_filename )
%
% shows comparisons of ground-truthed and newly tracked data
%
% JAB 5/17/11

if ~exist( 'dump_filename', 'var' )
%    dump_filename = '~/data/tmp.Ctrax-test-data.2011-05-20/stats_2011-05-20_19-01-09.tmp';
end

analysis_version = 2;

% read in list of stat filenames
fp = fopen( dump_filename, 'r' );
stat_filenames = {};
line = fgetl( fp );
while line ~= -1
   stat_filenames{end+1} = line;
   line = fgetl( fp );
end
fclose( fp );

for fi = 1:length( stat_filenames )
   load( stat_filenames{fi} )

   use_animals = min( [length( truedata.x ), length( newdata.x )] );
   comp_length = zeros( [1, use_animals] );
   comp_pos = zeros( size( comp_length ) );
   comp_ang = zeros( size( comp_length ) );
   comp_size = zeros( size( comp_length ) );
   pos_range = [inf, -inf, inf, -inf]; % arena size: minx, maxx, miny, maxy
   true_size = zeros( size( comp_length ) ); % animal size (pix^2)
   comp_n_frames = 0;
   for an = 1:use_animals
      figure(1); clf; hold on; plot( truedata.x{an}, truedata.y{an}, 'r', 'linewidth', 2 ), plot( newdata.x{an}, newdata.y{an} )
      use_len = min( [length( truedata.x{an} ), length( newdata.x{an} )] );
      comp_n_frames = max( [comp_n_frames, length( truedata.x{an} )] );
      
      use_true.x = double( truedata.x{an}(1:use_len) );
      use_true.y = double( truedata.y{an}(1:use_len) );
      use_true.theta = double( truedata.theta{an}(1:use_len) );
      use_true.a = double( truedata.a{an}(1:use_len) );
      use_true.b = double( truedata.b{an}(1:use_len) );
      use_new.x = double( newdata.x{an}(1:use_len) );
      use_new.y = double( newdata.y{an}(1:use_len) );
      use_new.theta = double( newdata.theta{an}(1:use_len) );
      use_new.a = double( newdata.a{an}(1:use_len) );
      use_new.b = double( newdata.b{an}(1:use_len) );
   
      % 1: how many frames in the track
      comp_length(an) = length( truedata.x ) - use_len;

      % 2: position difference (pix)
      comp_pos(an) = mean( sqrt( (use_true.x - use_new.x).^2 + (use_true.y - use_new.y).^2 ) );
      pos_range(1) = min( [pos_range(1) use_true.x(:)'] );
      pos_range(2) = max( [pos_range(2) use_true.x(:)'] );
      pos_range(3) = min( [pos_range(3) use_true.y(:)'] );
      pos_range(4) = max( [pos_range(4) use_true.y(:)'] );

      % 3: angle difference (rad)
      comp_ang(an) = mean( use_true.theta - use_new.theta );

      % 4: size difference (pix^2)
      comp_size(an) = mean( use_true.a.*use_true.b - use_new.a.*use_new.b );
      true_size(an) = mean( use_true.a.*use_true.b );

   end % for each animal

   comp_runtime = runtime;
   
   save( stat_filenames{fi}, '-append', 'comp_length', 'comp_pos', 'comp_ang', ...
      'comp_size', 'comp_runtime', 'comp_n_frames', 'true_size', 'pos_range', ...
      'analysis_version' )
end % for each newly tracked file
