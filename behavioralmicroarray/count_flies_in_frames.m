trx = load_tracks;
n_tracks = length(trx);

% find number of frames in movie
n_frames = -inf;
for t = 1:n_tracks
   if trx(t).endframe > n_frames
      n_frames = trx(t).endframe;
   end
end

% find number of flies in each frame
n_flies = zeros(1, n_frames);
for f = 1:n_frames
   flies_in_frame = 0;
   for t = 1:n_tracks
      if trx(t).firstframe <= f && trx(t).endframe >= f
         flies_in_frame = flies_in_frame + 1;
      end
   end
   n_flies(f) = flies_in_frame;
end
