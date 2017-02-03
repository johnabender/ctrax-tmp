function data = plot_test_data()
% data = plot_test_data
%
% plots Ctrax test-suite analyzed data
%
% JAB 2/14/12

data_dir = '~/data/';
dir_pattern = 'tmp.Ctrax-test-data';
% dir_pattern = 'reallytmp.test-data';

% initialize data structures
long_data = struct( 'moviename',     '', ...
                    'length_diff',  {}, ...
                    'position_diff', {}, ...
                    'angle_diff',    {}, ...
                    'size_diff',     {}, ...
                    'runtime',       [], ...
                    'n_frames',      [], ...
                    'enddate',       [] );

% go through every test data directory
list = dir( data_dir );
for di = 1:length( list )
   if ~isempty( strfind( list(di).name, dir_pattern ) ) && list(di).isdir
      
      % find the most recent list of test statistics
      dirname = [data_dir, list(di).name];
      sublist = dir( dirname );
      statfile = '';
      for dj = 1:length( sublist )
         if ~isempty( strfind( sublist(dj).name, 'stats_' ) ) && ~sublist(dj).isdir
            statfile = sublist(dj).name;
         end % if it's a stats file
      end % for each entry in data directory
      % the last stats file is the one we want...
      statname = [dirname, '/', statfile];
      
      % read in list of stat filenames
      fp = fopen( statname, 'r' );
      stat_filenames = {};
      line = fgetl( fp );
      while line ~= -1
         stat_filenames{end+1} = line;
         line = fgetl( fp );
      end
      fclose( fp );
      
      % read tracking comparison data from each stats file
      loaded_movies = 0;
      for fi = 1:length( stat_filenames )
         if ~exist( stat_filenames{fi}, 'file' ), continue, end

         % find canonical movie name and whether it's new or not
         moviename = stat_filenames{fi};
         moviename = moviename(1:length( moviename ) - length( '_2011-05-20_19-01-03_comparison.mat' ));
         long_ind = -1;
         for mi = 1:length( long_data )
            if isempty( long_data(mi).moviename ) || ...
                  strcmp( long_data(mi).moviename, moviename )
               long_ind = mi;
               if isempty( long_data(mi).moviename )
                  long_data(mi).moviename = moviename;
               end
               break;
            end
         end
         if long_ind < 0
            long_data(end+1).moviename = moviename;
            long_ind = length( long_data );
         end

         % pack data into structure
         load( stat_filenames{fi} )
         loaded_movies = loaded_movies + 1;
         
         long_data(long_ind).length_diff{end+1} = comp_length;
         long_data(long_ind).position_diff{end+1} = comp_pos;
         if exist( 'analysis_version', 'var' ) && analysis_version >= 2
            long_data(long_ind).angle_diff{end+1} = comp_ang;
         else
            long_data(long_ind).angle_diff{end+1} = zeros( size( comp_ang ) );
         end
         long_data(long_ind).size_diff{end+1} = comp_size;
         long_data(long_ind).runtime(end+1) = comp_runtime;
         if exist( 'comp_n_frames', 'var' )
            long_data(long_ind).n_frames = max( [long_data(long_ind).n_frames, comp_n_frames] );
         elseif isempty( long_data(long_ind).n_frames )
            long_data(long_ind).n_frames = 1;
         end
         
         % calculate run date
         datestring = stat_filenames{fi};
         datestring = datestring(length( moviename ) + 2:length( datestring ) - length( '_comparison.mat' ));
         long_data(long_ind).enddate(end+1) = datenum( datestring, 'yyyy-mm-dd_HH-MM-SS' );

      end % for each stats file

      fprintf( 1, '%d movies in %s\n', loaded_movies, statname )
      
   end % if it's a test-suite data directory
end % for each directory item

for fi = 1:length( long_data )
%          % 1: how many frames in the track
%          comp_length(an) = length( truedata.x ) - use_len;
%          % 2: position difference
%          comp_pos(an) = mean( sqrt( (use_true.x - use_new.x).^2 + (use_true.y - use_new.y).^2 ) );
%          % 3: angle difference
%          comp_ang(an) = mean( unwrap( use_true.theta ) - unwrap( use_new.theta ) );
%          % 4: size difference
%          comp_size(an) = mean( use_true.a.*use_true.b - use_new.a.*use_new.b );
%
%          comp_runtime = runtime;

   % count n. animals
   n_runs = length( long_data(fi).length_diff );
   n_animals = inf;
   for ri = 1:n_runs
      n_animals = min( [n_animals, length( long_data(fi).length_diff{ri} )] );
   end % for each run of this movie

   % gather data
   lengths = zeros( [n_animals, n_runs] );
   positions = zeros( size( lengths ) );
   angles = zeros( size( lengths ) );
   sizes = zeros( size( lengths ) );
   for ri = 1:n_runs
      for ai = 1:n_animals
         lengths(ai,ri) = -long_data(fi).length_diff{ri}(ai);
         positions(ai,ri) = long_data(fi).position_diff{ri}(ai);
         angles(ai,ri) = long_data(fi).angle_diff{ri}(ai);
         sizes(ai,ri) = -long_data(fi).size_diff{ri}(ai);
      end
   end
   n_frames = long_data(fi).n_frames;
   runtimes = long_data(fi).runtime;

   lengths(isinf( lengths )) = nan;
   positions(isinf( positions )) = nan;
   angles(isinf( angles )) = nan;
   sizes(isinf( sizes )) = nan;
   
   xvals = long_data(fi).enddate - long_data(fi).enddate(1);

   % plot
   figure( fi ); clf

   co = jet( n_animals );
   for ai = 1:n_animals
      subplot( 3, 2, 1 ); hold on
      plot( xvals, lengths(ai,:), 'color', co(ai,:) )
      subplot( 3, 2, 2 ); hold on
      plot( xvals, positions(ai,:), 'color', co(ai,:) )
      subplot( 3, 2, 3 ); hold on
      plot( xvals, angles(ai,:), 'color', co(ai,:) )
      subplot( 3, 2, 4 ); hold on
      plot( xvals, sizes(ai,:), 'color', co(ai,:) )
   end
   subplot( 3, 2, 5 )
   plot( xvals(runtimes > 1), runtimes(runtimes > 1)/n_animals/n_frames, 'k' )

   subplot( 3, 2, 1 )
   m = nanmean( lengths, 1 ); s = nanstd( lengths, [], 1 );%/sqrt( size( lengths, 1 ) - 1 );
   h = fill( [xvals xvals(end:-1:1)], [m-s m(end:-1:1)+s(end:-1:1)], 'k' );
   subplot( 3, 2, 2 )
   m = nanmean( positions, 1 ); s = nanstd( positions, [], 1 );%/sqrt( size( positions, 1 ) - 1 );
   h = [h fill( [xvals xvals(end:-1:1)], [m-s m(end:-1:1)+s(end:-1:1)], 'k' )];
   subplot( 3, 2, 3 )
   m = nanmean( angles, 1 ); s = nanstd( angles, [], 1 );%/sqrt( size( angles, 1 ) - 1 );
   h = [h fill( [xvals xvals(end:-1:1)], [m-s m(end:-1:1)+s(end:-1:1)], 'k' )];
   subplot( 3, 2, 4 )
   m = nanmean( sizes, 1 ); s = nanstd( sizes, [], 1 );%/sqrt( size( sizes, 1 ) - 1 );
   h = [h fill( [xvals xvals(end:-1:1)], [m-s m(end:-1:1)+s(end:-1:1)], 'k' )];
   set( h, 'edgecolor', 'none', 'facealpha', 0.6 )
   
   % label
   for p = 1:5
      subplot( 3, 2, p )
      set( gca, 'xtick', xvals )
      xlim( [-1 xvals(end)+1] )
      set( gca, 'xticklabel', {} )
      if p == 1
         h = title( long_data(fi).moviename(strfind( long_data(fi).moviename, 'test-suite' ) + length( 'test-suite' ) + 1:end) );
         set( h, 'interpreter', 'none' )
         xlabel( 'each color is one animal' )
         ylabel( 'track len. err. (frames)' )
         yl = get( gca, 'ylim' );
         ylim( [0 yl(2)] )
      elseif p == 2
         ylabel( 'position err. (pix)' )
         yl = get( gca, 'ylim' );
         ylim( [0 yl(2)] )
      elseif p == 3
         ylabel( 'angle err. (rad)' )
      elseif p == 4
         xlabel( 'run date' )
         set( gca, 'xticklabel', datestr( long_data(fi).enddate, 'mmmyy' ) )
         ylabel( 'size err. (pix^2)' )
      elseif p == 5
         xlabel( 'run date' )
         set( gca, 'xticklabel', datestr( long_data(fi).enddate, 'mmmyy' ) )
         ylabel( 'runtime (sec/animal)' )
      end
   end
   
end % for each unique movie file

