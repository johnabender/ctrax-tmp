% [readframe,nframes,fid,headerinfo] = get_readframe_fcn(filename)
% get_readframe_fcn inputs the name of a video, opens this video, and creates a
% function that can be used for random access to frames in the video. it can
% input files of type fmf, sbfmf, and avi. if videoio is installed on your
% machine, then get_readframe_fcn will use videoio to read all types of avi
% supported by videoio. otherwise, it uses VideoReader to open any type of avi
% supported by VideoReader. Run "help VideoReader" to determine what types of avi
% files are readable through VideoReader on your OS. 
%
% Input:
% filename is the name of the video to read. The type of video is determined
% based on the extension, so be sure the extension of your movie is correct. 
%
% Outputs:
% readframe is the handle to a function which inputs a frame number, reads this
% frame from filename, and outputs the corresponding frame. 
% nframes is the number of frames in the video. For avis, this may be
% approximate, as it is computed from the duration and framerate. 
% fid is the file identifier for filename. get_readframe_fcn will open the file
% filename. you must close fid yourself when you are done using the returned
% readframe. 
% headerinfo is a struct with fields depending on the type of movie

function [readframe,nframes,fid,headerinfo] = get_readframe_fcn(filename,varargin)

% allow videoio library to be used if it is installed and on the path
%CTRAX_ISVIDEOIO = exist('videoReader','file');
CTRAX_ISVIDEOIO = false;

if iscell(filename),
  
  readframes = cell(size(filename));
  nframes = inf;
  fid = nan(size(filename));
  headerinfo = cell(size(filename));
  for i = 1:numel(filename),
    [readframes{i},nframescurr,fid(i),headerinfo{i}] = get_readframe_fcn(filename{i},varargin{:});
    nframes = min(nframes,nframescurr);
  end
  
  readframe = @(f) multi_read_frame(f,readframes);
  return;
  
end

[~,ext] = splitext(filename);

if ispc && ~exist(filename,'file') && ~strcmpi(ext,'.seq'),  
  [actualfilename,didfind] = GetPCShortcutFileActualPath(filename);
  if didfind,
    filename = actualfilename;
  end
end

if strcmpi(ext,'.fmf'),
  [header_size,version,nr,nc,bytes_per_chunk,nframes,data_format] = fmf_read_header(filename);
  fid = fopen(filename);
  readframe = @(f) fmfreadframe(fid,header_size+(f-1)*bytes_per_chunk,nr,nc,bytes_per_chunk,data_format);
  headerinfo = struct('header_size',header_size,'version',version,'nr',nr,'nc',nc,...
    'bytes_per_chunk',bytes_per_chunk,'nframes',nframes,'data_format',data_format,'type','fmf');
elseif strcmpi(ext,'.sbfmf'),
  [nr,nc,nframes,bgcenter,bgstd,frame2file] = sbfmf_read_header(filename);
  fid = fopen(filename);
  readframe = @(f) sbfmfreadframe(f,fid,frame2file,bgcenter);
  headerinfo = struct('nr',nr,'nc',nc,'nframes',nframes,'bgcenter',bgcenter,...
    'bgstd',bgstd,'frame2file',frame2file,'type','sbfmf');
elseif strcmpi(ext,'.ufmf'),
  headerinfo = ufmf_read_header(filename);
  readframe = ufmf_get_readframe_fcn(headerinfo,varargin{:});
  nframes = headerinfo.nframes;
  fid = headerinfo.fid;
elseif strcmpi(ext,'.mmf'),
  headerinfo = mmf_read_header(filename);
  readframe = mmf_get_readframe_fcn(headerinfo,varargin{:});
  nframes = headerinfo.nframes;
  fid = headerinfo.fid;
elseif strcmpi(ext,'.tif'),
  info = imfinfo(filename);
  isimseq = false;
  if numel(info) == 1,
    filespec = regexprep(filename,'_\d+\.tif$','_*.tif');
    imfiles = mydir(filespec);
    if numel(imfiles) > 1,
      imfiles = sort(imfiles);
      im = imread(imfiles{1});
      headerinfo = struct('nr',size(im,1),'nc',size(im,2),'ncolors',size(im,3),'nframes',numel(imfiles),...
        'type','imseq','imfiles',{imfiles});
      readframe = @(f) imseq_read_frame(f,imfiles);
      nframes = headerinfo.nframes;
      fid = -1;
      isimseq = true;
    end
  end
  if ~isimseq,
    headerinfo = struct('nr',info(1).Height,'nc',info(1).Width,'nframes',numel(info),'type','tif',...
      'bitdepth',info(1).BitDepth);
    readframe = @(f) deal(imread(filename,f),f);
    nframes = headerinfo.nframes;
    fid = -1;
  end
elseif strcmpi(ext,'.mat'),
  videofiletype = load(filename,'videofiletype');
  switch videofiletype,
    
    case 'SingleLarvaTracker',
      videodata = load(filename);
      readframe = @(f) ReadSingleLarvaTrackerFrame(f,videodata.firstframeim,videodata.imraw,videodata.finalbbox,videodata.fps,varargin{:});
      nframes = numel(imraw);
      fid = 0;
      [nr,nc,~] = size(firstframeim);
      headerinfo = struct('nr',nr,'nc',nc,'nframes',nframes,'bgcenter',firstframeim,...
        'type','SingleLarvaTracker');
    otherwise
      error('Do not know how to parse mat file of type %s',videofiletype);
  end
else
  fid = 0;
  
  isindexedmjpg = false;
  if strcmpi(ext,'.mjpg'),
    [indexfilename] = myparse(varargin,'indexfilename',0);
    if ischar(indexfilename),
      isindexedmjpg = true;
    end
  end
  
  if isindexedmjpg,
    % get file names
    if ispc && ~exist(filename,'file'),
      [actualfilename,didfind] = GetPCShortcutFileActualPath(filename);
      if ~didfind,
        error('Could not find movie file %s',filename);
      end
      filename0 = filename;
      % use actualfilename instead
      filename = actualfilename;

      [actualindexfilename,didfind] = GetPCShortcutFileActualPath(indexfilename);
      if ~didfind,
        error('Could not find index file %s',indexfilename);
      end
      indexfilename0 = indexfilename;
      % use actualfilename instead
      indexfilename = actualindexfilename;
    end

    headerinfo = ReadIndexedMJPGHeader(filename,indexfilename);
    headerinfo.fid = 0;
    nframes = headerinfo.nframes;
    readframe = @(f) read_mjpg_frame(headerinfo,f);
  
  else
    
    if CTRAX_ISVIDEOIO,
      readerobj = videoReader(filename,'preciseFrames',30,'frameTimeoutMS',5000);
      info = getinfo(readerobj);
      nframes = info.numFrames;
      seek(readerobj,0);
      seek(readerobj,1);
      readframe = @(f) videoioreadframe(readerobj,f);
      headerinfo = info;
      headerinfo.type = 'avi';
    else
      try
        readerobj = VideoReader(filename);
        nframes = get(readerobj,'NumberOfFrames');
        if isempty(nframes),
          % approximate nframes from duration
          nframes = get(readerobj,'Duration')*get(readerobj,'FrameRate');
        end
        %readframe = @(f) flipdim(read(readerobj,f),1);
        headerinfo = get(readerobj);
        headerinfo.type = 'avi';
        headerinfo.nr = headerinfo.Height;
        headerinfo.nc = headerinfo.Width;
        if isfield(headerinfo,'NumberOfFrames'),
          headerinfo.nframes = headerinfo.NumberOfFrames;
        elseif isfield(headerinfo,'Duration') && isfield(headerinfo,'FrameRate'),
          headerinfo.nframes = headerinfo.Duration*headerinfo.FrameRate;
        end
        readframe = @(f) avi_read_frame(readerobj,headerinfo,f);
      catch ME_videoreader,
        
        % try using aviread
        try
          headerinfo = aviinfo(filename); %#ok<FREMO>
          nframes = headerinfo.NumFrames;
          fps = headerinfo.FramesPerSecond;
          
          readframe = @(f) aviread_helper(filename,f,fps);
          headerinfo.type = 'avi';
          fid = -1;
        catch ME_aviread,
          error('Could not open file %s with VideoReader (%s) or with aviread (%s)',...
            filename,getReport(ME_videoreader),getReport(ME_aviread));
        end
        
      end
    end
  end
end

function varargout = multi_read_frame(f,readframes)

[im,timestamp] = readframes{1}(f);

for i = 2:numel(readframes),
  im = cat(2,im,readframes{i}(f));  
end
varargout{1} = im;
if nargout >= 2,
  varargout{2} = timestamp;
end

function [im,timestamp] = seq_read_frame_piotr(f,sr)
im = [];
timestamp = [];

if ~sr.seek(f-1),
  warning('Could not seek to frame %d',f);
  return;
end

[im,timestamp] = sr.getframe();

function [im,timestamp] = avi_read_frame(readerobj,headerinfo,f)

try
  im = read(readerobj,f);
catch ME,
  warning('Error reading the first try: %s',getReport(ME));
  pause(.01);
  im = read(readerobj,f);
end
timestamp = (f-1)/headerinfo.FrameRate;

function [im,f] = imseq_read_frame(f,imfiles)

im = imread(imfiles{f});

function [im,stamp] = aviread_helper(filename,f,fps)

if numel(f) == 2,
  M = aviread_rawy8(filename,f(1):f(2)); % JAB 8/6/17 - I don't know if aviread_rawy8() ever existed,
                                         % or where it came from if it did. This code hasn't worked
                                         % since 2016 at the latest.
else
  M = aviread_rawy8(filename,f);
end
im = flipdim(cat(4,M.cdata),1);
stamp = f / fps;
