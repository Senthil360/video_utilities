# Video Utilities
## A set of scripts to make the mundane jobs of video editors easier

  ### <ins>Pre-requisites</ins>
 1. ##### [Python](https://www.python.org/downloads/)
      - cv2
      - json
      - opencv-python
      - pandas
      - openpyxl
  - _install the above using pip_
  2. #####   [Ffmpeg](https://ffbinaries.com/downloads)
  3. #####   [Ffprobe](https://ffbinaries.com/downloads)
  - _Add the location of ffmpeg binary and ffprobe binary to your $PATH_

  ### <ins>Functions</ins>

  | Program | Description |
| --- | --- |
| screenshot_preview.py | Create a preview collage picture of a video from its frames |
| video_split.py | Splits video into 'n' number of smaller videos |
| video_info.py | Exports filename, size, resolution, duration, fps & codec to a excel file | 
| video_transcode.py | Re-encodes supported videos in other codecs such as vp9 to h264 | 

### <ins>How to Use</ins>

All the programs <ins>**accept command line arguments**</ins>, if arguments for input and output are **$${\color{red}NOT}$$** specified, then files in the _`current working directory`_ are processed by default

### $${\color{lightgreen}Screenshot \space Preview}$$

```batch
screenshot_preview.py /input/directory/or/file /output/directory
```

- If output directory is not specified then a directory with name _**`screencap`**_ will be created in the `current working directory` to which the jpg file will be written

### $${\color{lightgreen}Video \space Splitter}$$

Splitting a SINGLE file

```batch
video_split.py /path/to/video.mp4 /path/to/output --num_parts 4 --min_size 1000 --max_size 2000
```

Splitting MULTIPLE files in a given directory

```batch
video_split.py /path/to/video /path/to/output --num_parts 4 --min_size 1000 --max_size 2000
```

###### Explanation
    - `/path/to/video.mp4` - Input video file
    - `/path/to/video` - Input video directory
    - `/path/to/output` - Your output directory, name will be in the format `original name + part number`
    - `--num_parts` - Specify the number of parts the video should get split into
    - `--min_size` - The minimum size of the file that can be taken as input (given in MB, default = 100 MB)
    - `--max_size 100` - The maximum size of the file that can be taken as input (given in MB, default = 2000 MB)

- If output directory is not specified then a directory with name _**`output_parts`**_ will be created in the `current working directory` to which the jpg file will be written

* _The splitting is ultra_fast so start and end of a video files may not be reporduced accurately in cut parts_

### $${\color{lightgreen}Video \space Info}$$

##### Saves the following information of video(s) in a directory to an excel file, in these columns

- File name
- Duration (HH:MM:SS)
- File Size
- FPS
- Resolution
- Codec

```batch
video_info.py /input/directory/or/file /output/directory
```

### $${\color{lightgreen}Video \space Transcoder}$$
##### Popular NLEs such as Davinci Resolve, Adobe Premiere, Final Cut can give you a headache when trying to process a non h264/h265/dnxhd encoded video.
##### This program is super useful in re-encoding the input video file into **h264 codec**, mp4 format

| FFMPEG flags | Explanation |
| --- | --- | 
| '-r', str(frame_rate) |  Set frame rate from original video |
| '-c:v', 'libx264' | Specify output video codec as h264 |
| '-c:a', 'aac' | Use AAC for audio encoding |
| '-preset', 'veryfast' | Set veryfast preset for quicker processing |
| '-threads', '0', | Enable multithreading |
| '-movflags', '+faststart' | Optimize for streaming |

## **F.A.Q**
1. #### Why do I get an error when I run the program?
     - Read the instructions, make sure the binaries are in the $PATH

2. #### What Operating Systems can I run these on?
     - The `screenshot_preview` and `video_info` programs are purely written in python and hence can be run in any environment in which python is installed
     - The `video_split` program requires python, ffmpeg and ffprobe, so it can only be run on platforms which have the binary for it
  
3. #### Will there be frequent updates or additions to this repository?
     - These are scripts I use in my daily workflow which I have decided to share, if some feature is requested and is worthwhile I will definitely work on it but as far as additions and updates go, it will mostly depend on my use cases
